import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.jobfit.scoring import analyze_job
from examples.sample_profile import candidate_profile




test_jobs = [
    {
        "title": "Supervisor de obra elÃ©ctrica",
        "company": "Gemex",
        "location": "Tlalnepantla, Estado de MÃ©xico",
        "source": "Indeed",
        "source_url": "Pendiente pegar link real de Indeed",
        "apply_url": "Pendiente pegar link real de Indeed",
        "salary_min": 25000,
        "salary_max": 30000,
        "requirements": [
            "supervisiÃ³n de obra elÃ©ctrica",
            "instalaciones elÃ©ctricas de media tensiÃ³n",
            "subestaciones elÃ©ctricas",
            "cumplimiento de planos",
            "especificaciones tÃ©cnicas",
            "normatividad aplicable",
            "seguridad industrial",
            "control presupuestal",
            "tiempos de entrega",
            "cronogramas",
            "gestiÃ³n de contratistas",
            "logÃ­stica de suministros",
            "supervisiÃ³n de calidad en campo",
            "identificaciÃ³n de riesgos operativos",
            "manejo avanzado de herramientas digitales",
        ],
    },
    {
        "title": "Ingeniero ElÃ©ctrico en Campo",
        "company": "Fazt",
        "location": "Gustavo A. Madero, CDMX",
        "source": "Indeed",
        "source_url": "Pendiente pegar link real de Indeed",
        "apply_url": "Pendiente pegar link real de Indeed",
        "salary_min": 24000,
        "salary_max": 25000,
        "requirements": [
            "titulado",
            "obra elÃ©ctrica",
            "distribuciÃ³n de energÃ­a",
            "seguimiento diario de obra",
            "coordinaciÃ³n de contratistas elÃ©ctricos",
            "control de avances",
            "calidad",
            "seguridad",
            "supervisiÃ³n conforme a planos",
            "supervisiÃ³n de cuadrillas elÃ©ctricas",
            "media y baja tensiÃ³n",
            "canalizaciones",
            "cableado",
            "validaciÃ³n de materiales",
            "normas bÃ¡sicas de seguridad elÃ©ctrica",
        ],
    },
    {
        "title": "Residente de Instalaciones MEP",
        "company": "GDC Desarrollos",
        "location": "Ciudad de MÃ©xico, CDMX",
        "source": "Indeed",
        "source_url": "Pendiente pegar link real de Indeed",
        "apply_url": "Pendiente pegar link real de Indeed",
        "salary_min": 25657,
        "salary_max": 28489,
        "requirements": [
            "instalaciones electromecÃ¡nicas",
            "instalaciones especiales",
            "construcciÃ³n de vivienda vertical",
            "cruce de ingenierÃ­as",
            "supervisiÃ³n de contratistas",
            "seguimiento de cronograma",
            "interpretaciÃ³n de planos",
            "Excel",
            "Project",
            "AutoCAD",
            "planos As-Built",
            "memorias de cÃ¡lculo",
            "RFIs",
            "supervisiÃ³n de instalaciones elÃ©ctricas",
            "instalaciones hidrosanitarias",
            "gas natural",
            "HVAC",
            "NOM-001-SEDE",
            "estimaciones",
            "generadores",
            "presupuestos",
            "Neodata",
            "OPUS",
            "ERP",
        ],
    },
    {
        "title": "Supervisor MEP",
        "company": "Grupo MARQ",
        "location": "CuauhtÃ©moc, CDMX",
        "source": "Indeed / Talenteca",
        "source_url": "https://www.talenteca.com/anuncio?j_id=6a2074e343000031008575de&source=indeed",
        "apply_url": "https://www.talenteca.com/anuncio?j_id=6a2074e343000031008575de&source=indeed",
        "salary_min": 20000,
        "salary_max": 23000,
        "requirements": [
            "experiencia en obra y construcciÃ³n",
            "sistemas de iluminaciÃ³n",
            "tableros elÃ©ctricos",
            "subestaciones",
            "cableado",
            "puesta a tierra",
            "pararrayos",
            "instalaciones hidrosanitarias",
            "instalaciones pluviales",
            "voz y datos",
            "CCTV",
            "HVAC",
            "cierres administrativos",
            "control de obra",
            "manejo de personal",
            "MS Office",
            "MS Project",
            "AutoCAD",
            "titulado",
        ],
    },
    {
        "title": "Residente MEP para Guatemala",
        "company": "KIN ENERGY INTERNACIONAL",
        "location": "Ciudad de los Deportes, CDMX / Proyecto en Guatemala",
        "source": "Indeed",
        "source_url": "Pendiente pegar link real de Indeed",
        "apply_url": "Pendiente pegar link real de Indeed",
        "salary_min": 30000,
        "salary_max": 30000,
        "requirements": [
            "residente MEP",
            "seguimiento de obra",
            "cronograma de obra",
            "estimaciones",
            "generadores de obra",
            "documentaciÃ³n de obra",
            "Submittals",
            "RFI",
            "boletines",
            "planos",
            "comunicaciÃ³n con cliente",
            "contratista general",
            "subcontratistas",
            "instalaciones MEP",
            "inglÃ©s conversacional",
            "disponibilidad para proyecto fuera de MÃ©xico",
        ],
    },
]


def main():
    print("=" * 80)
    print("JOBFIT AI - MVP CON VACANTES REALES")
    print("=" * 80)

    print(f"Candidato: {candidate_profile['name']}")
    print(f"FormaciÃ³n: {candidate_profile['education']}")
    print(f"Estado acadÃ©mico: {candidate_profile['education_status']}")
    print(f"Movilidad: {candidate_profile['mobility']}")
    print(f"Sueldo objetivo: ${candidate_profile['target_salary_mxn']:,} MXN")
    print()

    results = []

    for job in test_jobs:
        analysis = analyze_job(candidate_profile, job)
        results.append(analysis)

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    for index, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"TOP {index}: {result['job_title']} - {result['company']}")
        print("=" * 80)

        print(f"UbicaciÃ³n: {result['location']}")
        print(f"Fuente: {result['source']}")
        print(f"URL de vacante: {result['source_url']}")
        print(f"Aplicar en: {result['apply_url']}")
        print(f"Sueldo: {result['salary_range']}")
        print(f"Match tÃ©cnico: {result['technical_score']}%")
        print(f"Score econÃ³mico: {result['economic_score']}%")
        print(f"Score base: {result['base_final_score']}%")
        print(f"PenalizaciÃ³n crÃ­tica: -{result['critical_penalty']} pts")
        print(f"PenalizaciÃ³n por herramientas a confirmar: -{result['tools_penalty']} pts")
        print(f"Score final ajustado: {result['final_score']}%")
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
        print("Relaciones parciales / habilidades a reforzar:")
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
        print("Herramientas o conocimientos a confirmar:")
        if result["tools_to_confirm"]:
            for item in result["tools_to_confirm"]:
                print(f"  ðŸ§© {item}")
        else:
            print("  Sin herramientas crÃ­ticas pendientes de confirmar")

        print()
        print("Habilidades/requisitos faltantes:")
        if result["missing_requirements"]:
            for item in result["missing_requirements"]:
                print(f"  âš ï¸ {item}")
        else:
            print("  No se detectaron faltantes principales")

        print()

    print("=" * 80)
    print("FIN DEL ANÃLISIS")
    print("=" * 80)


if __name__ == "__main__":
    main()