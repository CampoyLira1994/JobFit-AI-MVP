import pytest

from src.jobfit.scoring import (
    analyze_job,
    assess_location,
    assess_location_details,
    detect_critical_warnings,
    detect_tools_to_confirm,
    normalize_text,
)


@pytest.fixture
def candidate_in_title_process():
    return {
        "education_status": "Egresado con titulacion en tramite",
        "mobility": "Solo opciones locales en CDMX, Estado de Mexico y zona metropolitana",
        "experience": [],
    }


@pytest.mark.parametrize(
    "location",
    [
        "Ciudad de Mexico, CDMX",
        "Naucalpan de Juarez, Mex.",
        "Tlalnepantla, Mex.",
    ],
)
def test_local_locations_are_cdmx_or_edomex(location):
    score, status, penalty = assess_location({"location": location})

    assert score == 100
    assert status == "local CDMX/Edomex"
    assert penalty == 0


@pytest.mark.parametrize(
    "location",
    [
        "Tlacotepec de Benito Juarez, Pue.",
        "Veracruz",
        "Queretaro",
    ],
)
def test_out_of_zone_locations_are_not_local(location):
    score, status, penalty = assess_location({"location": location})

    assert score < 100
    assert status != "local CDMX/Edomex"
    assert penalty > 0


def test_location_details_keeps_zmvm_as_local(candidate_in_title_process):
    score, status, penalty, category = assess_location_details(
        {"location": "Naucalpan de Juarez, Mex."},
        candidate_in_title_process,
    )

    assert score == 100
    assert status == "local CDMX/Edomex"
    assert penalty == 0
    assert category == "local_zmvm"


@pytest.mark.parametrize(
    "location",
    [
        "Jilotepec de Molina Enriquez, Mex.",
        "Villa de Almoloya de Juarez, Mex.",
        "Toluca, Estado de Mexico",
    ],
)
def test_strict_zmvm_preference_penalizes_far_edomex(location, candidate_in_title_process):
    score, status, penalty, category = assess_location_details(
        {"location": location},
        candidate_in_title_process,
    )

    assert score == 65
    assert status == "local Edomex amplio: validar distancia"
    assert penalty == 12
    assert category == "local_edomex_amplio"


def test_location_details_marks_queretaro_out_of_zone(candidate_in_title_process):
    score, status, penalty, category = assess_location_details(
        {"location": "Queretaro"},
        candidate_in_title_process,
    )

    assert score == 20
    assert status == "fuera de zona objetivo"
    assert penalty == 25
    assert category == "fuera_de_zona"


def test_analyze_job_includes_location_category_without_removing_status(candidate_in_title_process):
    result = analyze_job(
        candidate_in_title_process,
        {
            "title": "Supervisor electrico",
            "company": "Acme",
            "location": "Toluca, Estado de Mexico",
            "requirements": ["instalaciones electricas"],
            "salary_min": 25000,
            "salary_max": 30000,
            "raw_description": "",
        },
    )

    assert result["location_status"] == "local Edomex amplio: validar distancia"
    assert result["location_category"] == "local_edomex_amplio"


def test_professional_license_requirement_generates_critical_warning(candidate_in_title_process):
    warnings, penalty = detect_critical_warnings(
        candidate_in_title_process,
        {
            "title": "Supervisor electrico",
            "location": "CDMX",
            "requirements": ["cedula profesional"],
            "raw_description": "",
        },
    )

    assert penalty >= 10
    assert any("cedula profesional" in normalize_text(warning) for warning in warnings)


def test_titled_requirement_warns_when_candidate_has_title_in_process(candidate_in_title_process):
    warnings, penalty = detect_critical_warnings(
        candidate_in_title_process,
        {
            "title": "Residente de obra electrica",
            "location": "CDMX",
            "requirements": ["titulado"],
            "raw_description": "",
        },
    )

    assert penalty == 3
    assert any("titulacion en tramite" in normalize_text(warning) for warning in warnings)


def test_conversational_english_requirement_generates_warning(candidate_in_title_process):
    warnings, penalty = detect_critical_warnings(
        candidate_in_title_process,
        {
            "title": "Supervisor electrico",
            "location": "CDMX",
            "requirements": ["ingles conversacional"],
            "raw_description": "",
        },
    )

    assert penalty >= 8
    assert any("ingles conversacional" in normalize_text(warning) for warning in warnings)


def test_software_requirements_are_flagged_to_confirm_not_invented():
    tools = detect_tools_to_confirm(
        {
            "title": "Supervisor de obra electrica",
            "requirements": ["Project", "OPUS", "Neodata", "ERP", "SAP PM"],
            "raw_description": "Se solicita dominio de Project, OPUS, Neodata, ERP y SAP PM.",
        }
    )

    assert {"Project", "OPUS", "Neodata", "ERP", "SAP PM"}.issubset(set(tools))
