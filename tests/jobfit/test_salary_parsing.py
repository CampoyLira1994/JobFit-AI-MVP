import pytest

from src.jobfit.agents.serpapi_jobs_agent import parse_salary_from_text


@pytest.mark.parametrize(
    ("text", "expected_min", "expected_max"),
    [
        ("Sueldo $20,000 - $25,000 mensual", 20000, 25000),
        ("Sueldo $300,000 anual", 25000, 25000),
        ("Pago $2,500 semanal", 10825, 10825),
        ("Pago $150 por hora", 25950, 25950),
    ],
)
def test_parse_salary_periods_to_monthly_amounts(text, expected_min, expected_max):
    salary_min, salary_max = parse_salary_from_text(text)

    assert salary_min == pytest.approx(expected_min, abs=1)
    assert salary_max == pytest.approx(expected_max, abs=1)


@pytest.mark.parametrize(
    "text",
    [
        "Oferta con identificador $3,114,000 sin salario real",
        "Referencia externa $6,055,000 no corresponde a sueldo mensual",
    ],
)
def test_parse_salary_rejects_absurd_numbers(text):
    assert parse_salary_from_text(text) == (0, 0)


def test_parse_salary_uses_nearby_period_not_far_away_words():
    text = (
        "La semana de induccion se agenda despues de la contratacion. "
        "Se piden 5 anos de experiencia. "
        "El pago de viaticos puede ser quincenal segun el proyecto. "
        "Sueldo base $20,000 - $25,000 mensual."
    )

    assert parse_salary_from_text(text) == (20000, 25000)
