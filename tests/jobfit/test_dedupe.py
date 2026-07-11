from src.jobfit.agents.multi_source_agent import dedupe_jobs


def test_dedupe_jobs_removes_same_title_company_and_location():
    jobs = [
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
        },
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
        },
    ]

    assert dedupe_jobs(jobs) == [jobs[0]]


def test_dedupe_jobs_uses_same_apply_url_across_sources():
    jobs = [
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
            "source": "Adzuna API",
            "external_id": "adzuna-1",
            "apply_url": "https://empresa.example/jobs/123",
        },
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
            "source": "SerpAPI Google Jobs",
            "external_id": "google-2",
            "apply_url": "https://empresa.example/jobs/123",
        },
    ]

    assert dedupe_jobs(jobs) == [jobs[0]]


def test_dedupe_jobs_treats_cdmx_aliases_as_merge_candidates():
    jobs = [
        {
            "title": "Residente de obra electrica",
            "company": "Constructora Delta",
            "location": "CDMX",
        },
        {
            "title": "Residente de obra electrica",
            "company": "Constructora Delta",
            "location": "Ciudad de Mexico",
        },
    ]

    assert dedupe_jobs(jobs) == [jobs[0]]


def test_dedupe_jobs_merges_same_title_company_and_similar_salary_across_locations():
    jobs = [
        {
            "title": "Supervisor de Obra Electrica",
            "company": "Acme",
            "location": "Tlalnepantla",
            "salary_min": 20000,
            "salary_max": 25000,
            "requirements": ["obra electrica"],
        },
        {
            "title": "Supervisor de Obra Electrica",
            "company": "Acme",
            "location": "Naucalpan",
            "salary_min": 21000,
            "salary_max": 25000,
            "requirements": ["AutoCAD"],
        },
    ]

    result = dedupe_jobs(jobs)

    assert len(result) == 1
    assert result[0]["requirements"] == ["obra electrica", "AutoCAD"]


def test_dedupe_jobs_prefers_direct_apply_url_over_google_jobs_url():
    jobs = [
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
            "salary_min": 20000,
            "salary_max": 25000,
            "source": "SerpAPI Google Jobs",
            "apply_url": "https://www.google.com/search?ibp=htl;jobs&q=supervisor",
        },
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "Ciudad de Mexico",
            "salary_min": 20500,
            "salary_max": 24800,
            "source": "Adzuna API",
            "apply_url": "https://empresa.example/jobs/123",
        },
    ]

    result = dedupe_jobs(jobs)

    assert len(result) == 1
    assert result[0]["apply_url"] == "https://empresa.example/jobs/123"
    assert result[0]["source"] == "Adzuna API"


def test_dedupe_jobs_keeps_same_title_company_with_different_salary_as_distinct():
    jobs = [
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
            "salary_min": 18000,
            "salary_max": 20000,
        },
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "Monterrey",
            "salary_min": 35000,
            "salary_max": 40000,
        },
    ]

    assert dedupe_jobs(jobs) == jobs


def test_dedupe_jobs_keeps_same_location_with_clearly_different_salary_as_distinct():
    jobs = [
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
            "salary_min": 18000,
            "salary_max": 20000,
        },
        {
            "title": "Supervisor Electrico",
            "company": "Acme",
            "location": "CDMX",
            "salary_min": 35000,
            "salary_max": 40000,
        },
    ]

    assert dedupe_jobs(jobs) == jobs
