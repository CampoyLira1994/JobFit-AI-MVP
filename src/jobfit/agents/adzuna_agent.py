import os
import re
import time
import unicodedata
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


ADZUNA_API_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


DOMAIN_TERMS = [
    # Puestos objetivo
    "supervisor eléctrico",
    "supervisor electrico",
    "supervisor de obra eléctrica",
    "supervisor de obra electrica",
    "residente eléctrico",
    "residente electrico",
    "residente de obra",
    "residente de obra eléctrica",
    "residente de obra electrica",
    "residente MEP",
    "residente instalaciones",
    "residente instalaciones MEP",
    "supervisor MEP",
    "supervisor instalaciones",
    "supervisor instalaciones eléctricas",
    "supervisor instalaciones electricas",
    "coordinador eléctrico",
    "coordinador electrico",
    "coordinador de obra eléctrica",
    "coordinador de obra electrica",
    "ingeniero eléctrico",
    "ingeniero electrico",
    "ingeniero eléctrico en campo",
    "ingeniero electrico en campo",
    "ingeniero de instalaciones",
    "jefe de obra",
    "jefe de obra eléctrica",
    "jefe de obra electrica",

    # Áreas técnicas
    "obra eléctrica",
    "obra electrica",
    "instalaciones eléctricas",
    "instalaciones electricas",
    "instalaciones electromecánicas",
    "instalaciones electromecanicas",
    "instalaciones especiales",
    "instalaciones MEP",
    "MEP",
    "media y baja tensión",
    "media y baja tension",
    "media tensión",
    "media tension",
    "baja tensión",
    "baja tension",
    "alta tensión",
    "alta tension",
    "subestaciones eléctricas",
    "subestaciones electricas",
    "subestaciones",
    "tableros eléctricos",
    "tableros electricos",
    "puesta a tierra",
    "pararrayos",
    "canalizaciones",
    "cableado estructurado",
    "voz y datos",
    "CCTV",
    "HVAC",
    "instalaciones hidrosanitarias",
    "instalaciones pluviales",
    "instalaciones contra incendio",
    "gas natural",

    # Mantenimiento eléctrico
    "mantenimiento eléctrico",
    "mantenimiento electrico",
    "mantenimiento preventivo",
    "mantenimiento correctivo",
    "diagnóstico de fallas eléctricas",
    "diagnostico de fallas electricas",
    "plantas de emergencia",

    # Software / documentación
    "AutoCAD",
    "Excel",
    "Excel avanzado",
    "Office",
    "MS Office",
    "Project",
    "MS Project",
    "OPUS",
    "Neodata",
    "ERP",
    "Revit",
    "SAP",
    "planos",
    "interpretación de planos",
    "interpretacion de planos",
    "planos As-Built",
    "As-Built",
    "memorias de cálculo",
    "memorias de calculo",
    "NOM",
    "NOM-001-SEDE",
    "RFIs",
    "RFI",

    # Administración de obra
    "estimaciones",
    "generadores",
    "generadores de obra",
    "presupuestos",
    "control presupuestal",
    "control de obra",
    "control de avances",
    "reportes de avance",
    "seguimiento de obra",
    "seguimiento de cronograma",
    "cronograma de obra",
    "cronogramas",
    "tiempos de entrega",
    "logística de suministros",
    "logistica de suministros",
    "control de materiales",
    "compras de materiales",
    "requisiciones de material",

    # Personal / seguridad
    "seguridad industrial",
    "seguridad e higiene",
    "normatividad aplicable",
    "gestión de contratistas",
    "gestion de contratistas",
    "coordinación de contratistas",
    "coordinacion de contratistas",
    "supervisión de contratistas",
    "supervision de contratistas",
    "supervisión de cuadrillas",
    "supervision de cuadrillas",
    "manejo de personal",
    "liderazgo",

    # Requisitos académicos / alertas
    "titulado",
    "título profesional",
    "titulo profesional",
    "cédula",
    "cedula",
    "cédula profesional",
    "cedula profesional",
    "inglés conversacional",
    "ingles conversacional",
]


def strip_accents(text: str) -> str:
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKD", str(text))
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = strip_accents(str(text))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\.\-]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_html(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = str(raw_text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_env_config() -> Dict[str, str]:
    load_dotenv()

    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()
    country = os.getenv("ADZUNA_COUNTRY", "mx").strip().lower()

    if not app_id or not app_key:
        raise ValueError(
            "Faltan credenciales de Adzuna. Configura ADZUNA_APP_ID y ADZUNA_APP_KEY en .env."
        )

    if app_id == "TU_APP_ID" or app_key == "TU_APP_KEY":
        raise ValueError(
            "Todavía tienes placeholders en .env. Reemplaza TU_APP_ID y TU_APP_KEY."
        )

    return {
        "app_id": app_id,
        "app_key": app_key,
        "country": country,
    }


def safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def convert_salary_to_monthly(salary_value: int) -> int:
    """
    En Adzuna MX es común recibir salario anual.
    Ejemplo: 276000 anual = 23000 mensual aprox.
    """
    if salary_value <= 0:
        return 0

    if salary_value >= 100000:
        return round(salary_value / 12)

    return salary_value


def add_unique_normalized(target_list: List[str], value: str) -> None:
    normalized_value = normalize_text(value)

    if not normalized_value:
        return

    existing = {normalize_text(item) for item in target_list}

    if normalized_value not in existing:
        target_list.append(value)


def extract_requirements_from_text(text: str) -> List[str]:
    normalized = normalize_text(text)
    found_terms: List[str] = []

    for term in DOMAIN_TERMS:
        if normalize_text(term) in normalized:
            add_unique_normalized(found_terms, term)

    return found_terms


def has_electrical_context(text: str) -> bool:
    normalized = normalize_text(text)

    electrical_keywords = [
        "electrico",
        "electrica",
        "electricidad",
        "electromecanico",
        "electromecanica",
        "mep",
        "media tension",
        "baja tension",
        "alta tension",
        "subestacion",
        "subestaciones",
        "tablero",
        "tableros",
        "instalaciones electricas",
    ]

    return any(keyword in normalized for keyword in electrical_keywords)


def has_obra_context(text: str) -> bool:
    normalized = normalize_text(text)

    obra_keywords = [
        "obra",
        "residente",
        "supervisor",
        "instalaciones",
        "construccion",
        "proyecto",
        "proyectos",
        "mep",
    ]

    return any(keyword in normalized for keyword in obra_keywords)


def infer_requirements_from_title(title: str, description: str) -> List[str]:
    """
    Inferencia conservadora:
    No inflamos vacantes genéricas solo porque digan supervisor o mantenimiento.
    Solo agregamos requisitos si hay contexto eléctrico, MEP u obra claro.
    """
    full_text = f"{title} {description}"
    normalized = normalize_text(full_text)

    inferred: List[str] = []
    electrical_context = has_electrical_context(full_text)
    obra_context = has_obra_context(full_text)

    if "supervisor" in normalized and (electrical_context or obra_context):
        add_unique_normalized(inferred, "supervisión de obra")
        add_unique_normalized(inferred, "manejo de personal")
        add_unique_normalized(inferred, "reportes de avance")

    if "residente" in normalized and obra_context:
        add_unique_normalized(inferred, "residencia de obra")
        add_unique_normalized(inferred, "seguimiento de obra")
        add_unique_normalized(inferred, "reportes de avance")

    if "obra" in normalized and electrical_context:
        add_unique_normalized(inferred, "obra eléctrica")
        add_unique_normalized(inferred, "control de obra")
        add_unique_normalized(inferred, "seguridad e higiene")
        add_unique_normalized(inferred, "estimaciones")

    if electrical_context:
        add_unique_normalized(inferred, "instalaciones eléctricas")

        if (
            "media tension" in normalized
            or "baja tension" in normalized
            or "alta tension" in normalized
        ):
            add_unique_normalized(inferred, "media y baja tensión")

        if "tablero" in normalized:
            add_unique_normalized(inferred, "tableros eléctricos")

    if "mep" in normalized:
        add_unique_normalized(inferred, "instalaciones MEP")
        add_unique_normalized(inferred, "instalaciones electromecánicas")
        add_unique_normalized(inferred, "instalaciones especiales")
        add_unique_normalized(inferred, "instalaciones hidrosanitarias")
        add_unique_normalized(inferred, "HVAC")

    if "mantenimiento" in normalized and electrical_context:
        add_unique_normalized(inferred, "mantenimiento eléctrico")
        add_unique_normalized(inferred, "mantenimiento preventivo")
        add_unique_normalized(inferred, "mantenimiento correctivo")
        add_unique_normalized(inferred, "diagnóstico de fallas eléctricas")

    if "instalaciones" in normalized and electrical_context:
        add_unique_normalized(inferred, "interpretación de planos")
        add_unique_normalized(inferred, "AutoCAD")

    return inferred


def build_requirements(title: str, description: str) -> List[str]:
    detected = extract_requirements_from_text(f"{title} {description}")
    inferred = infer_requirements_from_title(title, description)

    requirements: List[str] = []

    for item in detected + inferred:
        add_unique_normalized(requirements, item)

    if not requirements:
        requirements = [title]

    return requirements


def normalize_adzuna_job(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    title = clean_html(raw_job.get("title") or "Título no disponible")

    company_data = raw_job.get("company") or {}
    company = clean_html(company_data.get("display_name") or "Empresa no disponible")

    location_data = raw_job.get("location") or {}
    location = clean_html(location_data.get("display_name") or "Ubicación no disponible")

    description = clean_html(raw_job.get("description") or "")

    raw_salary_min = safe_int(raw_job.get("salary_min"), 0)
    raw_salary_max = safe_int(raw_job.get("salary_max"), 0)

    monthly_salary_min = convert_salary_to_monthly(raw_salary_min)
    monthly_salary_max = convert_salary_to_monthly(raw_salary_max)

    redirect_url = raw_job.get("redirect_url") or "URL no disponible"

    requirements = build_requirements(title, description)

    salary_period_guess = (
        "monthly_converted_from_annual"
        if raw_salary_min >= 100000 or raw_salary_max >= 100000
        else "monthly_or_unknown"
    )

    return {
        "title": title,
        "company": company,
        "location": location,
        "source": "Adzuna API",
        "source_url": redirect_url,
        "apply_url": redirect_url,
        "salary_min": monthly_salary_min,
        "salary_max": monthly_salary_max,
        "requirements": requirements,
        "raw_description": description[:3000],
        "external_id": str(raw_job.get("id", "")),
        "raw_salary_min": raw_salary_min,
        "raw_salary_max": raw_salary_max,
        "salary_period_guess": salary_period_guess,
    }


def search_adzuna_page(
    query: str,
    location: str,
    page: int = 1,
    results_per_page: int = 20,
    salary_min: Optional[int] = None,
    full_time: bool = True,
) -> Dict[str, Any]:
    config = get_env_config()
    url = f"{ADZUNA_API_BASE_URL}/{config['country']}/search/{page}"

    params = {
        "app_id": config["app_id"],
        "app_key": config["app_key"],
        "results_per_page": results_per_page,
        "what": query,
        "where": location,
        "content-type": "application/json",
    }

    if salary_min is not None:
        params["salary_min"] = salary_min

    if full_time:
        params["full_time"] = 1

    try:
        response = requests.get(url, params=params, timeout=30)
    except requests.RequestException as error:
        print(f"[ERROR] Error consultando Adzuna: {error}")
        return {"results": [], "count": 0}

    if response.status_code != 200:
        print(f"[WARN] Adzuna respondió status {response.status_code}")
        print(f"       Query: {query} | Location: {location}")
        print(f"       Body: {response.text[:500]}")
        return {"results": [], "count": 0}

    return response.json()


def search_adzuna_jobs(
    queries: List[str],
    locations: List[str],
    max_jobs_total: int = 60,
    results_per_page: int = 20,
    pages_per_search: int = 1,
    salary_min: Optional[int] = None,
    delay_seconds: float = 0.5,
    max_search_calls: int = 100,
) -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    seen_ids = set()
    seen_urls = set()
    search_calls = 0

    for query in queries:
        for location in locations:
            for page in range(1, pages_per_search + 1):
                if len(jobs) >= max_jobs_total:
                    return jobs

                if search_calls >= max_search_calls:
                    print(f"[INFO] Límite de búsquedas alcanzado: {max_search_calls}")
                    return jobs

                search_calls += 1

                print(f"[ADZUNA SEARCH] {query} | {location} | page {page}")

                data = search_adzuna_page(
                    query=query,
                    location=location,
                    page=page,
                    results_per_page=results_per_page,
                    salary_min=salary_min,
                    full_time=True,
                )

                raw_results = data.get("results", [])
                print(f"[INFO] Resultados recibidos: {len(raw_results)}")

                for raw_job in raw_results:
                    if len(jobs) >= max_jobs_total:
                        return jobs

                    external_id = str(raw_job.get("id", ""))
                    redirect_url = raw_job.get("redirect_url", "")

                    if external_id and external_id in seen_ids:
                        continue

                    if redirect_url and redirect_url in seen_urls:
                        continue

                    normalized_job = normalize_adzuna_job(raw_job)
                    jobs.append(normalized_job)

                    if external_id:
                        seen_ids.add(external_id)

                    if redirect_url:
                        seen_urls.add(redirect_url)

                time.sleep(delay_seconds)

    return jobs