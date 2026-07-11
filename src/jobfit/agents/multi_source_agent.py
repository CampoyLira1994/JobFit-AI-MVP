from typing import Dict, List, Optional

from src.jobfit.agents.adzuna_agent import normalize_text, search_adzuna_jobs
from src.jobfit.agents.serpapi_jobs_agent import search_serpapi_jobs


def normalize_url(value: str) -> str:
    normalized = normalize_text(value)

    if not normalized or normalized == "url no disponible":
        return ""

    return normalized


def normalize_location_alias(location: str) -> str:
    normalized = normalize_text(location)

    cdmx_aliases = [
        "cdmx",
        "ciudad de mexico",
        "mexico city",
        "cdad. de mexico",
    ]

    if any(alias in normalized for alias in cdmx_aliases):
        return "ciudad de mexico"

    return normalized


def safe_int(value) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def get_salary_average(job: Dict) -> Optional[float]:
    salary_min = safe_int(job.get("salary_min"))
    salary_max = safe_int(job.get("salary_max"))

    if salary_min <= 0 and salary_max <= 0:
        return None

    if salary_min <= 0:
        return float(salary_max)

    if salary_max <= 0:
        return float(salary_min)

    return (salary_min + salary_max) / 2


def has_similar_salary(left: Dict, right: Dict) -> bool:
    left_average = get_salary_average(left)
    right_average = get_salary_average(right)

    if left_average is None or right_average is None:
        return False

    tolerance = max(3000, max(left_average, right_average) * 0.12)

    return abs(left_average - right_average) <= tolerance


def get_salary_signature(job: Dict) -> str:
    average = get_salary_average(job)

    if average is None:
        return "sin_sueldo"

    return str(round(average / 1000) * 1000)


def has_useful_url(value: str) -> bool:
    normalized = normalize_url(value)

    return bool(normalized)


def is_google_jobs_url(value: str) -> bool:
    normalized = normalize_url(value)

    return "google" in normalized and "jobs" in normalized


def is_better_url(candidate: str, current: str) -> bool:
    if not has_useful_url(candidate):
        return False

    if not has_useful_url(current):
        return True

    return is_google_jobs_url(current) and not is_google_jobs_url(candidate)


def is_probable_duplicate(left: Dict, right: Dict) -> bool:
    left_title = normalize_text(left.get("title", ""))
    right_title = normalize_text(right.get("title", ""))
    left_company = normalize_text(left.get("company", ""))
    right_company = normalize_text(right.get("company", ""))

    if not left_title or not right_title or not left_company or not right_company:
        return False

    if left_title != right_title or left_company != right_company:
        return False

    left_location = normalize_location_alias(left.get("location", ""))
    right_location = normalize_location_alias(right.get("location", ""))
    both_salaries_known = (
        get_salary_average(left) is not None
        and get_salary_average(right) is not None
    )

    if left_location and right_location and left_location == right_location:
        if both_salaries_known:
            return has_similar_salary(left, right)

        return True

    return has_similar_salary(left, right)


def add_unique_items(target: List, values: List) -> None:
    existing = {normalize_text(item) for item in target}

    for value in values:
        normalized = normalize_text(value)

        if normalized and normalized not in existing:
            target.append(value)
            existing.add(normalized)


def merge_job_metadata(target: Dict, incoming: Dict) -> Dict:
    if is_better_url(incoming.get("apply_url", ""), target.get("apply_url", "")):
        target["apply_url"] = incoming.get("apply_url")
        target["source"] = incoming.get("source", target.get("source"))

    if is_better_url(incoming.get("source_url", ""), target.get("source_url", "")):
        target["source_url"] = incoming.get("source_url")

    if get_salary_average(target) is None and get_salary_average(incoming) is not None:
        for key in ["salary_min", "salary_max", "raw_salary_min", "raw_salary_max", "salary_period_guess"]:
            if key in incoming:
                target[key] = incoming.get(key)

    if len(str(incoming.get("raw_description", ""))) > len(str(target.get("raw_description", ""))):
        target["raw_description"] = incoming.get("raw_description")

    if isinstance(target.get("requirements"), list) and isinstance(incoming.get("requirements"), list):
        add_unique_items(target["requirements"], incoming["requirements"])
    elif "requirements" not in target and "requirements" in incoming:
        target["requirements"] = incoming.get("requirements")

    for key in ["external_id", "posted_at", "via", "company", "location", "title"]:
        if not target.get(key) and incoming.get(key):
            target[key] = incoming.get(key)

    return target


def get_dedupe_key(job: Dict) -> str:
    title = normalize_text(job.get("title", ""))
    company = normalize_text(job.get("company", ""))
    location = normalize_location_alias(job.get("location", ""))
    apply_url = normalize_url(job.get("apply_url", ""))
    source_url = normalize_url(job.get("source_url", ""))

    external_id = normalize_text(job.get("external_id", ""))
    source = normalize_text(job.get("source", ""))

    if apply_url:
        return f"url|{apply_url}"

    if source_url:
        return f"url|{source_url}"

    if external_id:
        return f"{source}|{external_id}"

    return f"{title}|{company}|{location}|{get_salary_signature(job)}"


def dedupe_jobs(jobs: List[Dict]) -> List[Dict]:
    unique_jobs: List[Dict] = []
    seen_keys = {}

    for job in jobs:
        key = get_dedupe_key(job)

        if key in seen_keys:
            merge_job_metadata(unique_jobs[seen_keys[key]], job)
            continue

        duplicate_index = None

        for index, unique_job in enumerate(unique_jobs):
            if is_probable_duplicate(unique_job, job):
                duplicate_index = index
                break

        if duplicate_index is not None:
            merge_job_metadata(unique_jobs[duplicate_index], job)
            continue

        seen_keys[key] = len(unique_jobs)
        unique_jobs.append(job)

    return unique_jobs


def search_jobs_from_all_sources(
    queries: List[str],
    locations: List[str],
    use_adzuna: bool = True,
    use_serpapi: bool = True,
    max_jobs_total: int = 80,
) -> List[Dict]:
    all_jobs: List[Dict] = []

    if use_adzuna:
        print("=" * 90)
        print("FUENTE 1: ADZUNA API")
        print("=" * 90)

        adzuna_jobs = search_adzuna_jobs(
            queries=queries,
            locations=locations,
            max_jobs_total=max_jobs_total,
            results_per_page=20,
            pages_per_search=1,
            salary_min=None,
            delay_seconds=0.5,
            max_search_calls=80,
        )

        print(f"[INFO] Vacantes recibidas desde Adzuna: {len(adzuna_jobs)}")
        all_jobs.extend(adzuna_jobs)

    if use_serpapi:
        print("=" * 90)
        print("FUENTE 2: SERPAPI GOOGLE JOBS")
        print("=" * 90)

        serpapi_jobs = search_serpapi_jobs(
            queries=queries,
            locations=locations,
            max_jobs_total=max_jobs_total,
            pages_per_search=1,
            delay_seconds=1.0,
            max_search_calls=30,
        )

        print(f"[INFO] Vacantes recibidas desde SerpAPI: {len(serpapi_jobs)}")
        all_jobs.extend(serpapi_jobs)

    unique_jobs = dedupe_jobs(all_jobs)

    if len(unique_jobs) > max_jobs_total:
        unique_jobs = unique_jobs[:max_jobs_total]

    print("=" * 90)
    print("RESUMEN DE FUENTES")
    print("=" * 90)
    print(f"Vacantes brutas recibidas: {len(all_jobs)}")
    print(f"Vacantes únicas después de deduplicar: {len(unique_jobs)}")

    return unique_jobs
