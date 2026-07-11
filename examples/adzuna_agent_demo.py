import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.jobfit.agents.adzuna_agent import search_adzuna_jobs
from src.jobfit.scoring import analyze_job
from examples.sample_profile import candidate_profile




SEARCH_QUERIES = [
    "supervisor elÃ©ctrico",
    "supervisor electrico",
    "supervisor de obra elÃ©ctrica",
    "supervisor de obra electrica",
    "residente elÃ©ctrico",
    "residente electrico",
    "residente de obra elÃ©ctrica",
    "residente de obra electrica",
    "residente instalaciones",
    "residente instalaciones MEP",
    "supervisor instalaciones",
    "supervisor instalaciones elÃ©ctricas",
    "supervisor instalaciones electricas",
    "supervisor MEP",
    "coordinador elÃ©ctrico",
    "coordinador electrico",
    "coordinador de obra elÃ©ctrica",
    "coordinador de obra electrica",
    "ingeniero elÃ©ctrico campo",
    "ingeniero electrico campo",
    "ingeniero de instalaciones",
    "obra elÃ©ctrica",
    "obra electrica",
    "instalaciones elÃ©ctricas",
    "instalaciones electricas",
    "mantenimiento elÃ©ctrico",
    "mantenimiento electrico",
    "electromecÃ¡nico",
    "electromecanico",
    "MEP",
]


SEARCH_LOCATIONS = [
    "Ciudad de MÃ©xico",
    "CDMX",
    "Estado de MÃ©xico",
    "MÃ©xico",
    "Tlalnepantla",
    "Naucalpan",
    "Miguel Hidalgo",
    "CuauhtÃ©moc",
    "Iztapalapa",
    "Gustavo A. Madero",
    "Ecatepec",
    "AtizapÃ¡n",
    "CuautitlÃ¡n",
    "TultitlÃ¡n",
    "Toluca",
    "QuerÃ©taro",
]


TOP_RESULTS_TO_PRINT = 20


def print_job_result(index, result):
    print("=" * 90)
    print(f"TOP {index}: {result['job_title']} - {result['company']}")
    print("=" * 90)

    print(f"UbicaciÃ³n: {result['location']}")
    print(f"Fuente: {result['source']}")
    print(f"URL: {result['source_url']}")
    print(f"Aplicar en: {result['apply_url']}")
    print(f"Sueldo mensual estimado: {result['salary_range']}")
    print(f"Match tÃ©cnico: {result['technical_score']}%")
    print(f"Score econÃ³mico: {result['economic_score']}%")
    print(f"Score base: {result['base_final_score']}%")
    print(f"PenalizaciÃ³n crÃ­tica: -{result['critical_penalty']} pts")
    print(f"PenalizaciÃ³n herramientas: -{result['tools_penalty']} pts")
    print(f"Score final: {result['final_score']}%")
    print(f"CV recomendado: {result['cv_route']}")
    print(f"RecomendaciÃ³n: {result['recommendation']}")
    print(f"Comentario econÃ³mico: {result['economic_comment']}")
    print()

    print("Coincidencias directas:")
    if result["matched_requirements"]:
        for item in result["matched_requirements"]:
            print(f"  âœ… {item}")
    else:
        print("  Sin coincidencias directas")

    print()
    print("Equivalencias fuertes:")
    if result["strong_equivalent_matches"]:
        for item in result["strong_equivalent_matches"]:
            print(f"  ðŸ” {item['requirement']} â‰ˆ {item['matched_by']}")
    else:
        print("  Sin equivalencias fuertes detectadas")

    print()
    print("Relaciones parciales:")
    if result["partial_matches"]:
        for item in result["partial_matches"]:
            print(f"  ðŸŸ¡ {item['requirement']} relacionado con {item['matched_by']}")
    else:
        print("  Sin relaciones parciales detectadas")

    print()
    print("Restricciones crÃ­ticas / red flags:")
    if result["critical_warnings"]:
        for item in result["critical_warnings"]:
            print(f"  ðŸš¨ {item}")
    else:
        print("  Sin restricciones crÃ­ticas detectadas")

    print()
    print("Herramientas a confirmar:")
    if result["tools_to_confirm"]:
        for item in result["tools_to_confirm"]:
            print(f"  ðŸ§© {item}")
    else:
        print("  Sin herramientas pendientes")

    print()
    print("Faltantes:")
    if result["missing_requirements"]:
        for item in result["missing_requirements"]:
            print(f"  âš ï¸ {item}")
    else:
        print("  No se detectaron faltantes principales")

    print()


def save_results(results, file_path):
    export_data = {
        "candidate": candidate_profile["name"],
        "total_results": len(results),
        "results": results,
    }

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(export_data, file, ensure_ascii=False, indent=2)

    print(f"[EXPORT] Resultados guardados en: {file_path}")


def main():
    print("=" * 90)
    print("JOBFIT AI - ADZUNA API AGENT")
    print("=" * 90)
    print("Modo: bÃºsqueda por API permitida. No postula a vacantes.")
    print(f"Candidato: {candidate_profile['name']}")
    print(f"FormaciÃ³n: {candidate_profile['education']}")
    print(f"Estado acadÃ©mico: {candidate_profile['education_status']}")
    print(f"Movilidad: {candidate_profile['mobility']}")
    print(f"Sueldo objetivo mensual: ${candidate_profile['target_salary_mxn']:,} MXN")
    print()

    jobs = search_adzuna_jobs(
        queries=SEARCH_QUERIES,
        locations=SEARCH_LOCATIONS,
        max_jobs_total=50,
        results_per_page=20,
        pages_per_search=2,
        salary_min=None,
        delay_seconds=0.5,
        max_search_calls=120,
    )

    print()
    print("=" * 90)
    print(f"VACANTES RECIBIDAS DESDE API: {len(jobs)}")
    print("=" * 90)

    if not jobs:
        print("No llegaron vacantes desde la API.")
        print("Revisa ADZUNA_APP_ID, ADZUNA_APP_KEY, ADZUNA_COUNTRY o cambia queries/ubicaciÃ³n.")
        return

    results = []

    for job in jobs:
        analysis = analyze_job(candidate_profile, job)

        # Metadatos extra de Adzuna para depurar.
        analysis["raw_salary_min"] = job.get("raw_salary_min")
        analysis["raw_salary_max"] = job.get("raw_salary_max")
        analysis["salary_period_guess"] = job.get("salary_period_guess")
        analysis["external_id"] = job.get("external_id")
        analysis["raw_description"] = job.get("raw_description")

        results.append(analysis)

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    print(f"Mostrando TOP {min(TOP_RESULTS_TO_PRINT, len(results))} de {len(results)} vacantes.")
    print()

    for index, result in enumerate(results[:TOP_RESULTS_TO_PRINT], start=1):
        print_job_result(index, result)

    export_path = project_root / "output" / "adzuna_jobfit_results.json"
    save_results(results, export_path)

    print("=" * 90)
    print("FIN DEL ANÃLISIS CON ADZUNA API")
    print("=" * 90)


if __name__ == "__main__":
    main()