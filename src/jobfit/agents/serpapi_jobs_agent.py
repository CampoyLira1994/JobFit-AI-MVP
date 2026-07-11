import os
import re
import time
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

from src.jobfit.agents.adzuna_agent import build_requirements, clean_html, normalize_text


SERPAPI_ENDPOINT = "https://serpapi.com/search"


def get_serpapi_config() -> Optional[Dict[str, str]]:
    load_dotenv()

    api_key = os.getenv("SERPAPI_API_KEY", "").strip()

    if not api_key:
        return None

    return {
        "api_key": api_key,
        "google_domain": os.getenv("SERPAPI_GOOGLE_DOMAIN", "google.com.mx").strip(),
        "gl": os.getenv("SERPAPI_GL", "mx").strip(),
        "hl": os.getenv("SERPAPI_HL", "es").strip(),
        "no_cache": os.getenv("SERPAPI_NO_CACHE", "false").strip().lower(),
    }


def parse_money_value(raw_value: str, multiplier_hint: str = "") -> int:
    if not raw_value:
        return 0

    value_text = str(raw_value).lower().strip()
    value_text = value_text.replace(" ", "")
    value_text = value_text.replace(",", "")

    # Si llega algo tipo 20.000, lo tratamos como 20000.
    if value_text.count(".") == 1:
        left, right = value_text.split(".")
        if len(right) == 3:
            value_text = left + right

    try:
        value = float(value_text)
    except ValueError:
        return 0

    hint = normalize_text(multiplier_hint)

    if "k" in hint or "mil" in hint:
        value *= 1000

    return round(value)


def is_plausible_monthly_salary(value: int) -> bool:
    """
    Rango razonable para sueldo mensual MXN.
    Evita falsos positivos como $3,114,000 o $6,055,000.
    """
    return 8000 <= value <= 100000


def find_nearest_period(context: str) -> str:
    context_norm = unicodedata.normalize("NFKD", str(context or ""))
    context_norm = "".join(char for char in context_norm if not unicodedata.combining(char))
    context_norm = context_norm.lower()
    context_norm = re.sub(r"[^a-z0-9\s\.\-\$]", " ", context_norm)
    context_norm = re.sub(r"\s+", " ", context_norm)

    period_terms = {
        "hourly": ["por hora", "hora", "hour", "hourly", "hr"],
        "weekly": ["por semana", "semanal", "week", "weekly"],
        "biweekly": ["quincenal", "quincena", "biweekly"],
        "annual": ["por ano", "anual", "year", "yearly", "annual", "al ano"],
        "monthly": ["por mes", "mensual", "month", "monthly", "al mes"],
    }

    anchors = [
        index
        for index in [
            context_norm.find("$"),
            context_norm.find("mxn"),
            context_norm.find("mx"),
        ]
        if index >= 0
    ]
    anchor = min(anchors) if anchors else len(context_norm) // 2

    nearest_period = ""
    nearest_distance = None

    for period, terms in period_terms.items():
        for term in terms:
            pattern = re.compile(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])")

            for match in pattern.finditer(context_norm):
                distance = abs(match.start() - anchor)

                if nearest_distance is None or distance < nearest_distance:
                    nearest_period = period
                    nearest_distance = distance

    return nearest_period


def convert_salary_value_to_monthly(value: int, context: str) -> int:
    if value <= 0:
        return 0

    period = find_nearest_period(context)

    if period == "hourly":
        monthly_value = round(value * 173)
    elif period == "weekly":
        monthly_value = round(value * 4.33)
    elif period == "biweekly":
        monthly_value = round(value * 2)
    elif period == "annual":
        monthly_value = round(value / 12)
    elif period == "monthly":
        monthly_value = value
    elif value >= 100000:
        # En México muchos portales devuelven sueldo anual.
        monthly_value = round(value / 12)
    else:
        monthly_value = value

    if not is_plausible_monthly_salary(monthly_value):
        return 0

    return monthly_value


def remove_urls(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"www\.\S+", " ", text)

    return text


def get_match_context(text: str, match: re.Match, before: int = 80, after: int = 80) -> str:
    start = max(0, match.start() - before)
    end = min(len(text), match.end() + after)

    return text[start:end]


def parse_salary_from_text(text: str) -> Tuple[int, int]:
    """
    Intenta detectar salarios razonables desde Google Jobs/SerpAPI.

    Evita falsos positivos:
    - IDs enormes
    - números de URL
    - sueldos mensuales imposibles
    - valores muy bajos tipo $2,500 si no se detecta semana/hora/quincena
    """
    if not text:
        return 0, 0

    text_clean = clean_html(remove_urls(text))
    text_norm = normalize_text(text_clean)

    salary_context_keywords = [
        "salario",
        "sueldo",
        "pago",
        "mensual",
        "mes",
        "anual",
        "ano",
        "quincenal",
        "quincena",
        "semanal",
        "semana",
        "hora",
        "salary",
        "pay",
        "rate",
        "mxn",
        "$",
    ]

    if not any(keyword in text_norm for keyword in salary_context_keywords):
        return 0, 0

    range_pattern = re.compile(
        r"(?:mxn|mx\$|\$)\s*([0-9]+(?:[,\.\s][0-9]{3})*(?:\.\d+)?)\s*(k|mil)?"
        r"\s*(?:-|a|al|hasta)\s*"
        r"(?:mxn|mx\$|\$)?\s*([0-9]+(?:[,\.\s][0-9]{3})*(?:\.\d+)?)\s*(k|mil)?",
        re.IGNORECASE,
    )

    single_pattern = re.compile(
        r"(?:mxn|mx\$|\$)\s*([0-9]+(?:[,\.\s][0-9]{3})*(?:\.\d+)?)\s*(k|mil)?",
        re.IGNORECASE,
    )

    range_matches = list(range_pattern.finditer(text_clean))

    for match in range_matches:
        value_1 = parse_money_value(match.group(1), match.group(2) or "")
        value_2 = parse_money_value(match.group(3), match.group(4) or "")
        match_context = get_match_context(text_clean, match)

        monthly_1 = convert_salary_value_to_monthly(value_1, match_context)
        monthly_2 = convert_salary_value_to_monthly(value_2, match_context)

        valid_values = [value for value in [monthly_1, monthly_2] if value > 0]

        if len(valid_values) == 2:
            return min(valid_values), max(valid_values)

    values = []

    for match in single_pattern.finditer(text_clean):
        raw_number = match.group(1)
        multiplier_hint = match.group(2) or ""
        match_context = get_match_context(text_clean, match)

        value = parse_money_value(raw_number, multiplier_hint)
        monthly_value = convert_salary_value_to_monthly(value, match_context)

        if monthly_value > 0:
            values.append(monthly_value)

    if not values:
        return 0, 0

    values = sorted(set(values))

    if len(values) == 1:
        return values[0], values[0]

    return values[0], values[-1]


def get_apply_url(raw_job: Dict[str, Any]) -> str:
    apply_options = raw_job.get("apply_options") or []

    if isinstance(apply_options, list) and apply_options:
        first_option = apply_options[0] or {}
        link = first_option.get("link")

        if link:
            return link

    share_link = raw_job.get("share_link")

    if share_link:
        return share_link

    return "URL no disponible"


def normalize_serpapi_job(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    title = clean_html(raw_job.get("title") or "Título no disponible")
    company = clean_html(raw_job.get("company_name") or "Empresa no disponible")
    location = clean_html(raw_job.get("location") or "Ubicación no disponible")
    description = clean_html(raw_job.get("description") or "")

    apply_url = get_apply_url(raw_job)
    source_url = raw_job.get("share_link") or apply_url

    extensions = raw_job.get("extensions") or []
    extensions_text = " ".join([str(item) for item in extensions])

    salary_min, salary_max = parse_salary_from_text(
        f"{title}\n{description}\n{extensions_text}"
    )

    requirements = build_requirements(title, description)

    detected_extensions = raw_job.get("detected_extensions") or {}
    posted_at = detected_extensions.get("posted_at", "")

    return {
        "title": title,
        "company": company,
        "location": location,
        "source": "SerpAPI Google Jobs",
        "source_url": source_url,
        "apply_url": apply_url,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "requirements": requirements,
        "raw_description": description[:4000],
        "external_id": str(raw_job.get("job_id", "")),
        "raw_salary_min": salary_min,
        "raw_salary_max": salary_max,
        "salary_period_guess": "parsed_from_google_jobs_text" if salary_min else "not_available",
        "posted_at": posted_at,
        "via": raw_job.get("via", ""),
    }


def search_serpapi_page(
    query: str,
    location: str,
    next_page_token: Optional[str] = None,
    no_cache: bool = False,
) -> Dict[str, Any]:
    config = get_serpapi_config()

    if not config:
        print("[WARN] SERPAPI_API_KEY no está configurada. Se omite SerpAPI.")
        return {
            "jobs_results": [],
        }

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "google_domain": config["google_domain"],
        "gl": config["gl"],
        "hl": config["hl"],
        "api_key": config["api_key"],
    }

    if no_cache:
        params["no_cache"] = "true"

    if next_page_token:
        params["next_page_token"] = next_page_token

    try:
        response = requests.get(SERPAPI_ENDPOINT, params=params, timeout=45)
    except requests.RequestException as error:
        print(f"[ERROR] Error consultando SerpAPI: {error}")
        return {
            "jobs_results": [],
        }

    if response.status_code != 200:
        print(f"[WARN] SerpAPI respondió status {response.status_code}")
        print(f"       Query: {query} | Location: {location}")
        print(f"       Body: {response.text[:500]}")

        return {
            "jobs_results": [],
        }

    return response.json()


def search_serpapi_jobs(
    queries: List[str],
    locations: List[str],
    max_jobs_total: int = 40,
    pages_per_search: int = 1,
    delay_seconds: float = 1.0,
    max_search_calls: int = 40,
) -> List[Dict[str, Any]]:
    config = get_serpapi_config()

    if not config:
        print("[INFO] SerpAPI no configurado. Para activarlo agrega SERPAPI_API_KEY en .env.")
        return []

    no_cache = config.get("no_cache") == "true"

    jobs: List[Dict[str, Any]] = []
    seen_ids = set()
    seen_urls = set()
    search_calls = 0

    for query in queries:
        for location in locations:
            next_page_token: Optional[str] = None

            for page_number in range(1, pages_per_search + 1):
                if len(jobs) >= max_jobs_total:
                    return jobs

                if search_calls >= max_search_calls:
                    print(f"[INFO] Límite de búsquedas SerpAPI alcanzado: {max_search_calls}")
                    return jobs

                search_calls += 1

                print(f"[SERPAPI SEARCH] {query} | {location} | page {page_number}")

                data = search_serpapi_page(
                    query=query,
                    location=location,
                    next_page_token=next_page_token,
                    no_cache=no_cache,
                )

                raw_results = data.get("jobs_results", []) or []
                print(f"[INFO] Resultados SerpAPI recibidos: {len(raw_results)}")

                for raw_job in raw_results:
                    if len(jobs) >= max_jobs_total:
                        return jobs

                    external_id = str(raw_job.get("job_id", ""))
                    apply_url = get_apply_url(raw_job)

                    if external_id and external_id in seen_ids:
                        continue

                    if apply_url and apply_url in seen_urls:
                        continue

                    normalized_job = normalize_serpapi_job(raw_job)
                    jobs.append(normalized_job)

                    if external_id:
                        seen_ids.add(external_id)

                    if apply_url:
                        seen_urls.add(apply_url)

                pagination = data.get("serpapi_pagination") or {}
                next_page_token = pagination.get("next_page_token")

                if not next_page_token:
                    break

                time.sleep(delay_seconds)

    return jobs
