import csv
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.jobfit.agents.multi_source_agent import search_jobs_from_all_sources
from src.jobfit.scoring import analyze_job, normalize_text
from examples.sample_profile import candidate_profile




SEARCH_QUERIES = [
    "supervisor elÃ©ctrico",
    "supervisor de obra elÃ©ctrica",
    "residente de obra elÃ©ctrica",
    "supervisor instalaciones elÃ©ctricas",
    "residente instalaciones MEP",
    "supervisor MEP",
    "coordinador de obra elÃ©ctrica",
    "ingeniero elÃ©ctrico campo",
    "ingeniero de instalaciones",
    "jefe de obra elÃ©ctrica",
    "mantenimiento elÃ©ctrico",
]


SEARCH_LOCATIONS = [
    "Ciudad de MÃ©xico",
    "Estado de MÃ©xico",
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
    "Metepec",
]


TOP_RESULTS_TO_PRINT = 25


def build_career_track(result):
    title = normalize_text(result["job_title"])
    role_category = normalize_text(result.get("role_category", ""))
    cv_route = normalize_text(result.get("cv_route", ""))

    if "baja relevancia" in role_category:
        return "BAJA_RELEVANCIA"

    if "mantenimiento" in title or "mantenimiento" in cv_route:
        return "MANTENIMIENTO_ELECTRICO"

    if "mep" in title or "mep" in cv_route:
        return "OBRA_MEP"

    if "residente" in title or "obra electrica" in title:
        return "OBRA_ELECTRICA"

    if "supervisor electrico" in title:
        return "SUPERVISION_ELECTRICA"

    if "tecnico" in title:
        return "TECNICO_OPERATIVO"

    return "GENERAL_ELECTRICO"


def build_priority_rank(result):
    career_track = result.get("career_track", "")
    final_score = result.get("final_score", 0)
    location_status = result.get("location_status", "")
    recommendation = result.get("recommendation", "")
    salary_range = result.get("salary_range", "")

    priority = 0

    if career_track in ["OBRA_MEP", "OBRA_ELECTRICA", "SUPERVISION_ELECTRICA"]:
        priority += 40

    if career_track == "MANTENIMIENTO_ELECTRICO":
        priority += 25

    if "local" in location_status.lower():
        priority += 25

    if "$0 - $0" not in salary_range:
        priority += 15

    if "Aplicar" in recommendation:
        priority += 10

    priority += final_score * 0.3

    return round(priority, 2)


def print_executive_summary(results):
    total = len(results)

    recommended = [item for item in results if item["recommendation"] == "Aplicar"]
    apply_with_adjustments = [item for item in results if "Aplicar con" in item["recommendation"]]
    manual_review = [item for item in results if "Guardar" in item["recommendation"]]
    discard = [item for item in results if "Descartar" in item["recommendation"]]

    no_salary = [item for item in results if "$0 - $0" in item["salary_range"]]
    out_of_zone = [item for item in results if "fuera de zona" in item["location_status"]]
    critical = [item for item in results if item["critical_warnings"]]

    tracks = {}

    for item in results:
        track = item.get("career_track", "SIN_TRACK")
        tracks[track] = tracks.get(track, 0) + 1

    print("=" * 90)
    print("RESUMEN EJECUTIVO JOBFIT MULTI-FUENTE")
    print("=" * 90)
    print(f"Vacantes analizadas: {total}")
    print(f"Aplicar directo: {len(recommended)}")
    print(f"Aplicar con ajustes / advertencia: {len(apply_with_adjustments)}")
    print(f"Guardar y revisar manualmente: {len(manual_review)}")
    print(f"Descartar: {len(discard)}")
    print(f"Sin salario publicado: {len(no_salary)}")
    print(f"Fuera de zona objetivo: {len(out_of_zone)}")
    print(f"Con red flags crÃ­ticos: {len(critical)}")
    print()

    print("DistribuciÃ³n por ruta profesional:")
    for track, count in sorted(tracks.items(), key=lambda x: x[1], reverse=True):
        print(f"  {track}: {count}")

    if results:
        best = results[0]
        print()
        print("Mejor opciÃ³n detectada:")
        print(f"  {best['job_title']} - {best['company']}")
        print(f"  Fuente: {best['source']}")
        print(f"  Career track: {best['career_track']}")
        print(f"  Score final: {best['final_score']}%")
        print(f"  Priority rank: {best['priority_rank']}")
        print(f"  UbicaciÃ³n: {best['location']}")
        print(f"  Sueldo: {best['salary_range']}")
        print(f"  RecomendaciÃ³n: {best['recommendation']}")

    print()


def print_job_result(index, result):
    print("=" * 90)
    print(f"TOP {index}: {result['job_title']} - {result['company']}")
    print("=" * 90)

    print(f"Fuente: {result['source']}")
    print(f"Ruta profesional: {result['career_track']}")
    print(f"Priority rank: {result['priority_rank']}")
    print(f"UbicaciÃ³n: {result['location']}")
    print(f"Estado ubicaciÃ³n: {result['location_status']}")
    print(f"Sueldo mensual estimado: {result['salary_range']}")
    print(f"URL: {result['source_url']}")
    print(f"Aplicar en: {result['apply_url']}")
    print()

    print(f"Match tÃ©cnico: {result['technical_score']}%")
    print(f"Score econÃ³mico: {result['economic_score']}%")
    print(f"Relevancia del puesto: {result['role_relevance_score']}%")
    print(f"Score ubicaciÃ³n: {result['location_score']}%")
    print(f"Score base: {result['base_final_score']}%")
    print()

    print(f"PenalizaciÃ³n crÃ­tica: -{result['critical_penalty']} pts")
    print(f"PenalizaciÃ³n herramientas: -{result['tools_penalty']} pts")
    print(f"PenalizaciÃ³n sueldo: -{result['salary_penalty']} pts")
    print(f"PenalizaciÃ³n ubicaciÃ³n: -{result['location_penalty']} pts")
    print(f"PenalizaciÃ³n tÃ­tulo/rol: -{result['bad_title_penalty']} pts")
    print(f"Score final: {result['final_score']}%")
    print()

    print(f"CategorÃ­a del puesto: {result['role_category']}")
    print(f"CV recomendado: {result['cv_route']}")
    print(f"RecomendaciÃ³n: {result['recommendation']}")
    print(f"Comentario econÃ³mico: {result['economic_comment']}")
    print()

    print("Coincidencias directas:")
    if result["matched_requirements"]:
        for item in result["matched_requirements"][:12]:
            print(f"  âœ… {item}")
        if len(result["matched_requirements"]) > 12:
            print(f"  ... y {len(result['matched_requirements']) - 12} mÃ¡s")
    else:
        print("  Sin coincidencias directas")

    print()

    print("Relaciones parciales:")
    if result["partial_matches"]:
        for item in result["partial_matches"][:8]:
            print(f"  ðŸŸ¡ {item['requirement']} relacionado con {item['matched_by']}")
        if len(result["partial_matches"]) > 8:
            print(f"  ... y {len(result['partial_matches']) - 8} mÃ¡s")
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
        for item in result["missing_requirements"][:10]:
            print(f"  âš ï¸ {item}")
        if len(result["missing_requirements"]) > 10:
            print(f"  ... y {len(result['missing_requirements']) - 10} mÃ¡s")
    else:
        print("  No se detectaron faltantes principales")

    print()


def save_json_results(results, file_path):
    export_data = {
        "candidate": candidate_profile["name"],
        "total_results": len(results),
        "results": results,
    }

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(export_data, file, ensure_ascii=False, indent=2)

    print(f"[EXPORT] JSON guardado en: {file_path}")


def save_csv_results(results, file_path):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "priority_rank",
        "final_score",
        "career_track",
        "recommendation",
        "job_title",
        "company",
        "location",
        "location_status",
        "salary_range",
        "source",
        "source_url",
        "apply_url",
        "technical_score",
        "economic_score",
        "role_relevance_score",
        "location_score",
        "critical_penalty",
        "tools_penalty",
        "salary_penalty",
        "location_penalty",
        "bad_title_penalty",
        "cv_route",
        "economic_comment",
    ]

    with file_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for result in results:
            row = {column: result.get(column, "") for column in columns}
            writer.writerow(row)

    print(f"[EXPORT] CSV guardado en: {file_path}")


def main():
    print("=" * 90)
    print("JOBFIT AI - MULTI SOURCE JOB SEARCH AGENT")
    print("=" * 90)
    print("Modo: bÃºsqueda por APIs permitidas. No postula a vacantes.")
    print(f"Candidato: {candidate_profile['name']}")
    print(f"FormaciÃ³n: {candidate_profile['education']}")
    print(f"Estado acadÃ©mico: {candidate_profile['education_status']}")
    print(f"Movilidad: {candidate_profile['mobility']}")
    print(f"Sueldo objetivo mensual: ${candidate_profile['target_salary_mxn']:,} MXN")
    print()

    jobs = search_jobs_from_all_sources(
        queries=SEARCH_QUERIES,
        locations=SEARCH_LOCATIONS,
        use_adzuna=True,
        use_serpapi=True,
        max_jobs_total=80,
    )

    print()
    print("=" * 90)
    print(f"VACANTES ÃšNICAS RECIBIDAS: {len(jobs)}")
    print("=" * 90)

    if not jobs:
        print("No llegaron vacantes desde las APIs.")
        print("Revisa credenciales, queries, ubicaciones o lÃ­mites de las APIs.")
        return

    results = []

    for job in jobs:
        analysis = analyze_job(candidate_profile, job)

        analysis["raw_salary_min"] = job.get("raw_salary_min")
        analysis["raw_salary_max"] = job.get("raw_salary_max")
        analysis["salary_period_guess"] = job.get("salary_period_guess")
        analysis["external_id"] = job.get("external_id")
        analysis["raw_description"] = job.get("raw_description")
        analysis["posted_at"] = job.get("posted_at", "")
        analysis["via"] = job.get("via", "")

        analysis["career_track"] = build_career_track(analysis)
        analysis["priority_rank"] = build_priority_rank(analysis)

        results.append(analysis)

    results = sorted(
        results,
        key=lambda item: (
            item["priority_rank"],
            item["final_score"],
            item["role_relevance_score"],
            item["location_score"],
        ),
        reverse=True,
    )

    print_executive_summary(results)

    print(f"Mostrando TOP {min(TOP_RESULTS_TO_PRINT, len(results))} de {len(results)} vacantes.")
    print()

    for index, result in enumerate(results[:TOP_RESULTS_TO_PRINT], start=1):
        print_job_result(index, result)

    output_dir = project_root / "output"
    save_json_results(results, output_dir / "multi_source_jobfit_results.json")
    save_csv_results(results, output_dir / "multi_source_jobfit_results.csv")

    print("=" * 90)
    print("FIN DEL ANÃLISIS MULTI-FUENTE")
    print("=" * 90)


if __name__ == "__main__":
    main()
