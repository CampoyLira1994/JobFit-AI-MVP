import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup


INDEED_BASE_URL = "https://mx.indeed.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
}


DOMAIN_TERMS = [
    "supervisión de obra eléctrica",
    "supervisión de obra",
    "residencia de obra",
    "residente de obra",
    "residente MEP",
    "instalaciones MEP",
    "instalaciones electromecánicas",
    "instalaciones eléctricas",
    "instalaciones especiales",
    "obra eléctrica",
    "media y baja tensión",
    "media tensión",
    "baja tensión",
    "subestaciones eléctricas",
    "subestaciones",
    "tableros eléctricos",
    "puesta a tierra",
    "pararrayos",
    "canalizaciones",
    "cableado",
    "cableado estructurado",
    "voz y datos",
    "CCTV",
    "HVAC",
    "instalaciones hidrosanitarias",
    "instalaciones pluviales",
    "instalaciones contra incendio",
    "AutoCAD",
    "Excel",
    "MS Office",
    "Project",
    "MS Project",
    "OPUS",
    "Neodata",
    "ERP",
    "Revit",
    "NOM",
    "NOM-001-SEDE",
    "memorias de cálculo",
    "planos",
    "interpretación de planos",
    "planos As-Built",
    "estimaciones",
    "generadores",
    "presupuestos",
    "control presupuestal",
    "control de obra",
    "control de avances",
    "reportes de avance",
    "seguridad industrial",
    "seguridad e higiene",
    "gestión de contratistas",
    "coordinación de contratistas",
    "coordinación de contratistas eléctricos",
    "supervisión de cuadrillas",
    "supervisión de cuadrillas eléctricas",
    "manejo de personal",
    "validación de materiales",
    "logística de suministros",
    "titulado",
    "cédula",
    "cedula",
    "inglés conversacional",
    "ingles conversacional",
    "disponibilidad para proyecto fuera de México",
    "fuera de México",
    "Guatemala",
]


def normalize_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
    }

    text = text.lower().strip()

    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    return text


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_salary_range(text: str) -> Dict[str, int]:
    """
    Extract salary range from Spanish/Mexican job text.
    Examples:
    - "$25,000 a $30,000 por mes"
    - "$24,000 - $25,000"
    - "$30,000 por mes"
    """
    if not text:
        return {"salary_min": 0, "salary_max": 0}

    salary_matches = re.findall(r"\$?\s?(\d{1,3}(?:,\d{3})+|\d{4,6})", text)

    numbers = []

    for raw in salary_matches:
        try:
            value = int(raw.replace(",", "").strip())

            # Avoid picking tiny numbers.
            if value >= 10000:
                numbers.append(value)
        except ValueError:
            continue

    if not numbers:
        return {"salary_min": 0, "salary_max": 0}

    if len(numbers) == 1:
        return {"salary_min": numbers[0], "salary_max": numbers[0]}

    return {
        "salary_min": min(numbers[:2]),
        "salary_max": max(numbers[:2]),
    }


def build_indeed_search_url(query: str, location: str, start: int = 0) -> str:
    params = {
        "q": query,
        "l": location,
        "start": start,
    }

    return f"{INDEED_BASE_URL}/jobs?{urlencode(params)}"


def fetch_html(url: str, timeout: int = 20) -> Optional[str]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)

        if response.status_code != 200:
            print(f"[WARN] Indeed respondió status {response.status_code}: {url}")
            return None

        return response.text

    except requests.RequestException as error:
        print(f"[ERROR] No se pudo descargar: {url}")
        print(f"        {error}")
        return None


def get_text_from_soup(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return clean_text(soup.get_text(" "))


def extract_job_key_from_url(url: str) -> Optional[str]:
    match = re.search(r"[?&]jk=([^&]+)", url)

    if match:
        return match.group(1)

    return None


def find_job_links(search_html: str) -> List[str]:
    soup = BeautifulSoup(search_html, "html.parser")
    links = []

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "")

        if "viewjob" in href and "jk=" in href:
            full_url = urljoin(INDEED_BASE_URL, href)
            links.append(full_url)

    unique_links = []
    seen_keys = set()

    for link in links:
        job_key = extract_job_key_from_url(link) or link

        if job_key not in seen_keys:
            unique_links.append(link)
            seen_keys.add(job_key)

    return unique_links


def extract_title(soup: BeautifulSoup) -> str:
    selectors = [
        "h1",
        "[data-testid='jobsearch-JobInfoHeader-title']",
        ".jobsearch-JobInfoHeader-title",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            title = clean_text(element.get_text(" "))
            title = title.replace("- job post", "").strip()

            if title:
                return title

    return "Título no detectado"


def extract_company(soup: BeautifulSoup) -> str:
    selectors = [
        "[data-testid='inlineHeader-companyName']",
        "[data-testid='company-name']",
        ".jobsearch-InlineCompanyRating div",
        ".css-1saizt3",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            company = clean_text(element.get_text(" "))

            if company:
                return company

    text = get_text_from_soup(soup)
    lines = [line.strip() for line in text.split(" ") if line.strip()]

    if lines:
        return "Empresa no detectada"

    return "Empresa no detectada"


def extract_location(soup: BeautifulSoup) -> str:
    selectors = [
        "[data-testid='job-location']",
        "[data-testid='text-location']",
        ".jobsearch-JobInfoHeader-subtitle div",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            location = clean_text(element.get_text(" "))

            if location:
                return location

    return "Ubicación no detectada"


def extract_description_text(soup: BeautifulSoup) -> str:
    selectors = [
        "#jobDescriptionText",
        "[data-testid='jobDescriptionText']",
        ".jobsearch-jobDescriptionText",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            return clean_text(element.get_text(" "))

    return get_text_from_soup(soup)


def extract_requirements_from_text(text: str) -> List[str]:
    normalized = normalize_text(text)
    found_terms = []

    for term in DOMAIN_TERMS:
        if normalize_text(term) in normalized:
            found_terms.append(term)

    # Deduplicate preserving order.
    unique_terms = []

    for term in found_terms:
        if term not in unique_terms:
            unique_terms.append(term)

    return unique_terms


def fetch_indeed_job_detail(url: str) -> Optional[Dict[str, Any]]:
    html = fetch_html(url)

    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = extract_title(soup)
    company = extract_company(soup)
    location = extract_location(soup)
    description = extract_description_text(soup)

    salary_data = extract_salary_range(description)
    requirements = extract_requirements_from_text(f"{title} {description}")

    if not requirements:
        requirements = [title]

    return {
        "title": title,
        "company": company,
        "location": location,
        "source": "Indeed",
        "source_url": url,
        "apply_url": url,
        "salary_min": salary_data["salary_min"],
        "salary_max": salary_data["salary_max"],
        "requirements": requirements,
        "raw_description": description[:3000],
    }


def search_indeed_jobs(
    queries: List[str],
    locations: List[str],
    max_jobs_total: int = 10,
    max_pages_per_search: int = 1,
    delay_seconds: float = 2.0,
) -> List[Dict[str, Any]]:
    """
    Search Indeed and return job dictionaries compatible with analyze_job().

    Important:
    - This does not apply to jobs.
    - It only searches public result pages.
    - It rate-limits requests with delay_seconds.
    """
    found_jobs = []
    seen_urls = set()

    for query in queries:
        for location in locations:
            for page_index in range(max_pages_per_search):
                if len(found_jobs) >= max_jobs_total:
                    return found_jobs

                start = page_index * 10
                search_url = build_indeed_search_url(query, location, start=start)

                print(f"[SEARCH] {query} | {location}")
                print(f"         {search_url}")

                search_html = fetch_html(search_url)

                if not search_html:
                    continue

                job_links = find_job_links(search_html)

                print(f"[INFO] Links encontrados: {len(job_links)}")

                for job_url in job_links:
                    if len(found_jobs) >= max_jobs_total:
                        return found_jobs

                    if job_url in seen_urls:
                        continue

                    seen_urls.add(job_url)

                    print(f"[DETAIL] {job_url}")

                    job_detail = fetch_indeed_job_detail(job_url)

                    if job_detail:
                        found_jobs.append(job_detail)

                    time.sleep(delay_seconds)

                time.sleep(delay_seconds)

    return found_jobs