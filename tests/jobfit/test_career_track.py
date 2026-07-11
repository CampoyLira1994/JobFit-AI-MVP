import pytest

from examples.multi_source_jobfit_demo import build_career_track


@pytest.mark.parametrize(
    ("result", "expected_track"),
    [
        (
            {
                "job_title": "Supervisor de Mantenimiento Electrico",
                "role_category": "alta relevancia: puesto electrico/obra/MEP",
                "cv_route": "CV mantenimiento electrico / supervisor tecnico",
            },
            "MANTENIMIENTO_ELECTRICO",
        ),
        (
            {
                "job_title": "Residente de obra electrica",
                "role_category": "alta relevancia: puesto electrico/obra/MEP",
                "cv_route": "CV supervisor/residente de obra electrica",
            },
            "OBRA_ELECTRICA",
        ),
        (
            {
                "job_title": "Supervisor MEP",
                "role_category": "alta relevancia: puesto electrico/obra/MEP",
                "cv_route": "CV residente/supervisor de instalaciones MEP",
            },
            "OBRA_MEP",
        ),
        (
            {
                "job_title": "Supervisor electrico",
                "role_category": "alta relevancia: puesto electrico/obra/MEP",
                "cv_route": "CV supervisor/residente de obra electrica",
            },
            "SUPERVISION_ELECTRICA",
        ),
        (
            {
                "job_title": "Encargado de compras material electrico",
                "role_category": "baja relevancia: compras/materiales, no obra electrica directa",
                "cv_route": "CV supervisor/residente de obra electrica",
            },
            "BAJA_RELEVANCIA",
        ),
    ],
)
def test_build_career_track_classifies_expected_paths(result, expected_track):
    assert build_career_track(result) == expected_track
