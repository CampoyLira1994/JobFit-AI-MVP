import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.jobfit.scoring import analyze_job
from examples.sample_profile import candidate_profile




def load_manual_jobs(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        jobs = json.load(file)

    if not isinstance(jobs, list):
        raise ValueError("El archivo manual_jobs.json debe contener una lista de vacantes.")

    return jobs


def print_job_result(index, result):
    print("=" * 90)
    print(f"TOP {index}: {result['job_title']} - {result['company']}")
    print("=" * 90)

    print(f"UbicaciÃ³n: {result['location']}")
    print(f"Fuente: {result['source']}")
    print(f"URL: {result['source_url']}")
    print(f"Aplicar en: {result['apply_url']}")
    print(f"Sueldo: {result['salary_range']}")
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


def main():
    jobs_file = project_root / "jobs" / "manual_jobs.json"

    print("=" * 90)
    print("JOBFIT AI - MANUAL JOBS AGENT")
    print("=" * 90)
    print("Modo: vacantes pegadas manualmente. No postula a vacantes.")
    print(f"Candidato: {candidate_profile['name']}")
    print(f"FormaciÃ³n: {candidate_profile['education']}")
    print(f"Estado acadÃ©mico: {candidate_profile['education_status']}")
    print(f"Movilidad: {candidate_profile['mobility']}")
    print(f"Sueldo objetivo: ${candidate_profile['target_salary_mxn']:,} MXN")
    print(f"Archivo de vacantes: {jobs_file}")
    print()

    jobs = load_manual_jobs(jobs_file)

    print("=" * 90)
    print(f"VACANTES CARGADAS: {len(jobs)}")
    print("=" * 90)

    results = []

    for job in jobs:
        analysis = analyze_job(candidate_profile, job)
        results.append(analysis)

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    for index, result in enumerate(results, start=1):
        print_job_result(index, result)

    print("=" * 90)
    print("FIN DEL ANÃLISIS MANUAL")
    print("=" * 90)


if __name__ == "__main__":
    main()