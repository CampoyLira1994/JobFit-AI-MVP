import re
import unicodedata
from typing import Any, Dict, List, Tuple


STOPWORDS = {
    "de",
    "del",
    "la",
    "el",
    "los",
    "las",
    "y",
    "en",
    "para",
    "con",
    "sin",
    "por",
    "a",
    "al",
    "un",
    "una",
    "o",
    "u",
    "que",
    "se",
    "su",
    "sus",
}


TOOLS_TO_CONFIRM = [
    "Project",
    "MS Project",
    "OPUS",
    "Neodata",
    "ERP",
    "Revit",
    "SAP",
    "SAP PM",
]


STRONG_EQUIVALENCES = {
    "supervision de contratistas": ["coordinacion de personal", "manejo de personal"],
    "gestion de contratistas": ["coordinacion de personal", "manejo de personal"],
    "coordinacion de contratistas": ["coordinacion de personal", "manejo de personal"],
    "supervision de cuadrillas": ["manejo de personal", "supervision operativa"],
    "normatividad aplicable": ["NOM", "seguridad e higiene"],
    "nom-001-sede": ["NOM"],
    "seguridad industrial": ["seguridad e higiene"],
    "identificacion de riesgos operativos": ["seguridad e higiene"],
    "tiempos de entrega": ["reportes de avance", "seguimiento fisico financiero"],
    "cronogramas": ["reportes de avance", "seguimiento fisico financiero"],
    "seguimiento de cronograma": ["reportes de avance", "seguimiento fisico financiero"],
    "control de avances": ["reportes de avance", "seguimiento fisico financiero"],
    "logistica de suministros": ["requisiciones de material", "compras de materiales"],
    "control de materiales": ["control de almacen", "requisiciones de material"],
    "validacion de materiales": ["control de almacen", "requisiciones de material"],
    "especificaciones tecnicas": ["memorias de calculo", "lectura de planos"],
    "interpretacion de planos": ["lectura de planos"],
    "planos": ["lectura de planos", "maquetacion de planos", "planos As-Built"],
    "planos as-built": ["planos As-Built", "reingenieria de planos"],
    "instalaciones electromecanicas": ["instalaciones electricas", "instalaciones especiales"],
    "instalaciones mep": ["instalaciones especiales", "instalaciones hidrosanitarias", "HVAC"],
    "subestaciones electricas": ["subestaciones"],
    "media tension": ["media y baja tension"],
    "baja tension": ["media y baja tension"],
    "tableros electricos": ["tableros eléctricos"],
    "diagnostico de fallas": ["diagnostico de fallas electricas"],
    "mantenimiento preventivo": ["mantenimiento electrico"],
    "mantenimiento correctivo": ["mantenimiento electrico"],
    "manejo avanzado de herramientas digitales": [
        "AutoCAD",
        "Office avanzado",
        "Excel avanzado",
        "herramientas digitales de obra",
        "reportes de avance",
        "planos As-Built",
    ],
}


PARTIAL_EQUIVALENCES = {
    "project": ["reportes de avance", "seguimiento fisico financiero"],
    "ms project": ["reportes de avance", "seguimiento fisico financiero"],
    "opus": ["presupuestos", "analisis de costos"],
    "neodata": ["presupuestos", "analisis de costos"],
    "erp": ["control de almacen", "requisiciones de material"],
    "rfi": ["reportes de avance"],
    "rfis": ["reportes de avance"],
    "submittals": ["reportes de avance"],
    "gas natural": ["instalaciones especiales"],
    "construccion de vivienda vertical": ["residencia de obra", "supervision de obra"],
    "cruce de ingenierias": ["lectura de planos", "interpretacion de planos"],
}


LOCAL_LOCATION_TERMS = [
    "ciudad de mexico",
    "cdmx",
    "estado de mexico",
    "edomex",
    "tlalnepantla",
    "naucalpan",
    "miguel hidalgo",
    "cuauhtemoc",
    "iztapalapa",
    "gustavo a. madero",
    "gustavo a madero",
    "ecatepec",
    "atizapan",
    "cuautitlan",
    "tultitlan",
    "toluca",
    "metepec",
    "tecamac",
    "coacalco",
    "azcapotzalco",
    "benito juarez",
    "coyoacan",
    "alvaro obregon",
    "venustiano carranza",
    "nezahualcoyotl",
]


ZMVM_LOCATION_TERMS = [
    "ciudad de mexico",
    "cdmx",
    "mexico city",
    "cdad. de mexico",
    "tlalnepantla",
    "naucalpan",
    "miguel hidalgo",
    "cuauhtemoc",
    "iztapalapa",
    "gustavo a. madero",
    "gustavo a madero",
    "ecatepec",
    "atizapan",
    "cuautitlan",
    "tultitlan",
    "tecamac",
    "coacalco",
    "azcapotzalco",
    "benito juarez",
    "coyoacan",
    "alvaro obregon",
    "venustiano carranza",
    "nezahualcoyotl",
    "chalco",
    "valle de chalco",
    "chimalhuacan",
    "cuautitlan izcalli",
]


EDOMEX_AMPLIO_LOCATION_TERMS = [
    "estado de mexico",
    "edomex",
    "mex.",
    "toluca",
    "metepec",
    "jilotepec",
    "jilotepec de molina enriquez",
    "almoloya",
    "almoloya de juarez",
    "villa de almoloya",
]


OUT_OF_ZONE_LOCATION_TERMS = [
    "puebla",
    "pue",
    "jalisco",
    "jal",
    "guadalajara",
    "zapopan",
    "tlaquepaque",
    "tlajomulco",
    "queretaro",
    "qro",
    "el marques",
    "tamaulipas",
    "tamps",
    "tampico",
    "veracruz",
    "ver",
    "yucatan",
    "merida",
    "chiapas",
    "monterrey",
    "nuevo leon",
    "nl",
    "guanajuato",
    "gto",
    "san luis potosi",
    "slp",
]


BAD_ROLE_KEYWORDS = [
    "limpieza",
    "ventas",
    "vendedor",
    "call center",
    "cajero",
    "almacenista",
    "administrativo",
    "recursos humanos",
    "compras",
    "material electrico",
    "supervisor de seguridad",
    "seguridad obra",
]


def strip_accents(text: str) -> str:
    if text is None:
        return ""

    normalized = unicodedata.normalize("NFKD", str(text))
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_text(text: Any) -> str:
    if text is None:
        return ""

    text = strip_accents(str(text))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\.\-]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_meaningful_words(text: str) -> List[str]:
    normalized = normalize_text(text)
    words = normalized.split()

    return [
        word
        for word in words
        if word not in STOPWORDS and len(word) >= 3
    ]


def has_enough_word_overlap(requirement: str, candidate_skill: str) -> bool:
    req_words = set(get_meaningful_words(requirement))
    skill_words = set(get_meaningful_words(candidate_skill))

    if not req_words or not skill_words:
        return False

    overlap = req_words.intersection(skill_words)

    if len(req_words) == 1:
        return bool(overlap)

    required_overlap = max(1, round(len(req_words) * 0.60))

    return len(overlap) >= required_overlap


def candidate_has_skill(candidate_skills: List[str], expected_skill: str) -> bool:
    expected_norm = normalize_text(expected_skill)

    for skill in candidate_skills:
        skill_norm = normalize_text(skill)

        if expected_norm and expected_norm in skill_norm:
            return True

        if skill_norm and skill_norm in expected_norm:
            return True

        if has_enough_word_overlap(expected_norm, skill_norm):
            return True

    return False


def candidate_has_title_in_process(candidate_profile: Dict[str, Any]) -> bool:
    education_status = normalize_text(candidate_profile.get("education_status", ""))

    return (
        "titulacion en tramite" in education_status
        or "titulo en tramite" in education_status
        or "tramite" in education_status
        or "egresado" in education_status
    )


def candidate_already_titled(candidate_profile: Dict[str, Any]) -> bool:
    education_status = normalize_text(candidate_profile.get("education_status", ""))

    return (
        "titulado" in education_status
        and "tramite" not in education_status
    )


def is_title_requirement(requirement: str) -> bool:
    req_norm = normalize_text(requirement)

    title_terms = [
        "titulado",
        "titulo profesional",
        "titulo universitario",
        "licenciatura concluida",
        "ingenieria concluida",
        "carrera concluida",
    ]

    return any(term in req_norm for term in title_terms)


def requirement_matches_candidate(
    requirement: str,
    candidate_skills: List[str],
) -> Tuple[str, Any]:
    req_norm = normalize_text(requirement)

    for skill in candidate_skills:
        skill_norm = normalize_text(skill)

        if req_norm and req_norm in skill_norm:
            return "direct", skill

        if skill_norm and skill_norm in req_norm:
            return "direct", skill

        if has_enough_word_overlap(req_norm, skill_norm):
            return "direct", skill

    for equivalent_requirement, equivalent_skills in STRONG_EQUIVALENCES.items():
        equivalent_requirement_norm = normalize_text(equivalent_requirement)

        if req_norm == equivalent_requirement_norm or has_enough_word_overlap(req_norm, equivalent_requirement_norm):
            for equivalent_skill in equivalent_skills:
                if candidate_has_skill(candidate_skills, equivalent_skill):
                    return "strong", equivalent_skill

    for partial_requirement, partial_skills in PARTIAL_EQUIVALENCES.items():
        partial_requirement_norm = normalize_text(partial_requirement)

        if req_norm == partial_requirement_norm or partial_requirement_norm in req_norm:
            for partial_skill in partial_skills:
                if candidate_has_skill(candidate_skills, partial_skill):
                    return "partial", partial_skill

    return "missing", None


def detect_critical_warnings(candidate_profile: Dict[str, Any], job: Dict[str, Any]) -> Tuple[List[str], int]:
    warnings = []
    penalty = 0

    job_text = normalize_text(
        f"{job.get('title', '')} "
        f"{job.get('location', '')} "
        f"{' '.join(job.get('requirements', []))} "
        f"{job.get('raw_description', '')}"
    )

    mobility = normalize_text(candidate_profile.get("mobility", ""))

    has_title_in_process = candidate_has_title_in_process(candidate_profile)
    already_titled = candidate_already_titled(candidate_profile)

    job_asks_titled = (
        "titulado" in job_text
        or "titulo profesional" in job_text
        or "titulo universitario" in job_text
        or "licenciatura concluida" in job_text
        or "ingenieria concluida" in job_text
        or "carrera concluida" in job_text
    )

    job_asks_license = (
        "cedula" in job_text
        or "cedula profesional" in job_text
    )

    if job_asks_titled:
        if already_titled:
            pass
        elif has_title_in_process:
            warnings.append(
                "La vacante pide titulado o carrera concluida. El candidato tiene titulación en trámite; aplicar validando si aceptan título en proceso."
            )
            penalty += 3
        else:
            warnings.append(
                "La vacante pide titulado. No afirmar titulación si aún no está concluida."
            )
            penalty += 8

    if job_asks_license:
        warnings.append(
            "La vacante menciona cédula profesional. No inventar cédula; validar si es requisito obligatorio o si aceptan cédula en trámite."
        )
        penalty += 10

    if "ingles conversacional" in job_text or "advanced english" in job_text or "business english" in job_text:
        warnings.append(
            "La vacante parece pedir inglés conversacional. No afirmarlo si no está confirmado."
        )
        penalty += 8

    if "guatemala" in job_text or "fuera de mexico" in job_text:
        if "local" in mobility or "zona metropolitana" in mobility:
            warnings.append(
                "La vacante implica movilidad fuera de México o fuera de la zona objetivo. Validar antes de aplicar."
            )
            penalty += 12

    return warnings, penalty


def detect_tools_to_confirm(job: Dict[str, Any]) -> List[str]:
    job_text = normalize_text(
        f"{job.get('title', '')} "
        f"{' '.join(job.get('requirements', []))} "
        f"{job.get('raw_description', '')}"
    )

    tools = []

    for tool in TOOLS_TO_CONFIRM:
        if normalize_text(tool) in job_text:
            if tool not in tools:
                tools.append(tool)

    normalized_tools = []

    for tool in tools:
        if normalize_text(tool) == "ms project":
            if "Project" not in normalized_tools:
                normalized_tools.append("Project")
        else:
            if tool not in normalized_tools:
                normalized_tools.append(tool)

    return normalized_tools


def calculate_technical_match(
    candidate_profile: Dict[str, Any],
    job: Dict[str, Any],
) -> Dict[str, Any]:
    candidate_skills = candidate_profile.get("experience", [])
    requirements = job.get("requirements", [])

    matched_requirements = []
    strong_equivalent_matches = []
    partial_matches = []
    missing_requirements = []

    if not requirements:
        return {
            "technical_score": 0.0,
            "matched_requirements": [],
            "strong_equivalent_matches": [],
            "partial_matches": [],
            "missing_requirements": [],
        }

    total_points = 0.0
    max_points = len(requirements)

    has_title_in_process = candidate_has_title_in_process(candidate_profile)
    already_titled = candidate_already_titled(candidate_profile)

    for requirement in requirements:
        if is_title_requirement(requirement):
            if already_titled:
                total_points += 1.0
                matched_requirements.append(requirement)
                continue

            if has_title_in_process:
                total_points += 0.50
                partial_matches.append(
                    {
                        "requirement": requirement,
                        "matched_by": "titulación en trámite",
                    }
                )
                continue

        match_type, matched_by = requirement_matches_candidate(requirement, candidate_skills)

        if match_type == "direct":
            total_points += 1.0
            matched_requirements.append(requirement)

        elif match_type == "strong":
            total_points += 0.85
            strong_equivalent_matches.append(
                {
                    "requirement": requirement,
                    "matched_by": matched_by,
                }
            )

        elif match_type == "partial":
            total_points += 0.50
            partial_matches.append(
                {
                    "requirement": requirement,
                    "matched_by": matched_by,
                }
            )

        else:
            missing_requirements.append(requirement)

    technical_score = round((total_points / max_points) * 100, 2)

    return {
        "technical_score": technical_score,
        "matched_requirements": matched_requirements,
        "strong_equivalent_matches": strong_equivalent_matches,
        "partial_matches": partial_matches,
        "missing_requirements": missing_requirements,
    }


def calculate_economic_score(candidate_profile: Dict[str, Any], job: Dict[str, Any]) -> Tuple[int, str, int]:
    target_salary = int(candidate_profile.get("target_salary_mxn", 0) or 0)

    salary_min = int(job.get("salary_min", 0) or 0)
    salary_max = int(job.get("salary_max", 0) or 0)

    if salary_min <= 0 and salary_max <= 0:
        return 40, "La vacante no muestra salario. Revisar antes de aplicar.", 12

    if salary_min <= 0:
        average_salary = salary_max
    elif salary_max <= 0:
        average_salary = salary_min
    else:
        average_salary = round((salary_min + salary_max) / 2)

    if target_salary <= 0:
        return 50, "No hay sueldo objetivo configurado.", 0

    if average_salary >= target_salary:
        return 90, "El sueldo promedio está en o por arriba del objetivo.", 0

    if average_salary >= target_salary * 0.90:
        return 70, "El sueldo está cerca del objetivo; puede valer la pena negociar.", 4

    if average_salary >= target_salary * 0.80:
        return 55, "El sueldo está debajo del objetivo, pero podría revisarse si la vacante es muy buena.", 8

    if average_salary >= 18000:
        return 45, "El sueldo parece bajo contra el objetivo del candidato.", 14

    return 35, "El sueldo es bajo contra el objetivo del candidato.", 20


def candidate_prefers_strict_zmvm(candidate_profile: Dict[str, Any]) -> bool:
    mobility = normalize_text(candidate_profile.get("mobility", ""))
    restrictions = normalize_text(" ".join(candidate_profile.get("restrictions", [])))
    target_locations = normalize_text(" ".join(candidate_profile.get("target_locations", [])))
    text = f"{mobility} {restrictions} {target_locations}"

    strict_terms = [
        "solo opciones locales",
        "solo cdmx",
        "zona metropolitana",
        "zmvm",
        "sin reubicacion",
        "no reubicacion",
    ]

    return any(term in text for term in strict_terms)


def assess_location_details(
    job: Dict[str, Any],
    candidate_profile: Dict[str, Any] = None,
) -> Tuple[int, str, int, str]:
    location = normalize_text(job.get("location", ""))
    candidate_profile = candidate_profile or {}

    if not location:
        return 50, "ubicación no disponible", 5, "ubicacion_no_disponible"

    # Primero descartamos estados fuera de zona.
    # Esto evita errores como "Tlacotepec de Benito Juárez, Pue.",
    # que antes podía marcarse local por contener "Benito Juárez".
    for term in OUT_OF_ZONE_LOCATION_TERMS:
        if normalize_text(term) in location:
            return 20, "fuera de zona objetivo", 25, "fuera_de_zona"

    for term in ZMVM_LOCATION_TERMS:
        if normalize_text(term) in location:
            return 100, "local CDMX/Edomex", 0, "local_zmvm"

    for term in EDOMEX_AMPLIO_LOCATION_TERMS:
        if normalize_text(term) in location:
            if candidate_prefers_strict_zmvm(candidate_profile):
                return 65, "local Edomex amplio: validar distancia", 12, "local_edomex_amplio"

            return 75, "local Edomex amplio: validar distancia", 8, "local_edomex_amplio"

    return 20, "fuera de zona objetivo", 25, "fuera_de_zona"


def assess_location(
    job: Dict[str, Any],
    candidate_profile: Dict[str, Any] = None,
) -> Tuple[int, str, int]:
    score, status, penalty, _category = assess_location_details(job, candidate_profile)

    return score, status, penalty


def assess_role_relevance(job: Dict[str, Any]) -> Tuple[int, str, int]:
    title = normalize_text(job.get("title", ""))
    requirements_text = normalize_text(" ".join(job.get("requirements", [])))
    raw_description = normalize_text(job.get("raw_description", ""))

    full_text = f"{title} {requirements_text} {raw_description}"

    has_electrical = any(
        keyword in full_text
        for keyword in [
            "electrico",
            "electrica",
            "electricidad",
            "electromecanico",
            "electromecanica",
            "mep",
            "media tension",
            "baja tension",
            "alta tension",
            "tablero",
            "subestacion",
            "instalaciones electricas",
        ]
    )

    has_target_role = any(
        keyword in title
        for keyword in [
            "supervisor",
            "residente",
            "coordinador",
            "ingeniero",
            "jefe",
        ]
    )

    has_obra_or_project = any(
        keyword in full_text
        for keyword in [
            "obra",
            "instalaciones",
            "proyecto",
            "proyectos",
            "mep",
        ]
    )

    if "obra civil" in title and not any(keyword in title for keyword in ["electrica", "electrico", "mep"]):
        return 30, "baja relevancia: obra civil sin enfoque eléctrico en el título", 22

    for bad_keyword in BAD_ROLE_KEYWORDS:
        bad_norm = normalize_text(bad_keyword)

        if bad_norm in title:
            if bad_norm in ["compras", "material electrico"]:
                return 35, "baja relevancia: compras/materiales, no obra eléctrica directa", 22

            if "seguridad" in bad_norm and has_electrical:
                return 55, "media-baja relevancia: seguridad eléctrica, no ejecución de obra", 14

            return 15, f"baja relevancia por título: {bad_keyword}", 35

    if ("elevador" in title or "elevadores" in title or "escalera" in title or "escaleras" in title) and has_electrical:
        return 70, "relevancia media: elevadores/escaleras eléctricas, más mantenimiento que obra", 8

    if "mantenimiento" in title and has_electrical:
        return 75, "relevancia media: mantenimiento eléctrico", 6

    if has_target_role and has_electrical and has_obra_or_project:
        return 100, "alta relevancia: puesto eléctrico/obra/MEP", 0

    if has_target_role and has_electrical:
        return 90, "alta relevancia: puesto eléctrico", 0

    if "tecnico" in title and has_electrical:
        return 60, "relevancia media-baja: técnico eléctrico", 12

    if "mecanico" in title and not has_electrical:
        return 30, "baja relevancia: mecánico general sin enfoque eléctrico", 25

    if has_electrical:
        return 65, "relevancia media: menciona electricidad pero el puesto no es objetivo claro", 10

    return 25, "baja relevancia: no se detecta enfoque eléctrico/MEP suficiente", 25


def format_salary_range(job: Dict[str, Any]) -> str:
    salary_min = int(job.get("salary_min", 0) or 0)
    salary_max = int(job.get("salary_max", 0) or 0)

    return f"${salary_min:,} - ${salary_max:,} MXN"


def recommend_cv_route(job: Dict[str, Any], role_category: str) -> str:
    title = normalize_text(job.get("title", ""))
    requirements_text = normalize_text(" ".join(job.get("requirements", [])))
    full_text = f"{title} {requirements_text} {role_category}"

    if "mep" in full_text or "hidrosanitaria" in full_text or "hvac" in full_text:
        return "CV residente/supervisor de instalaciones MEP"

    if "residente" in title or "supervisor de obra" in title or "obra electrica" in full_text:
        return "CV supervisor/residente de obra eléctrica"

    if "mantenimiento" in full_text or "elevador" in full_text or "escalera" in full_text:
        return "CV mantenimiento eléctrico / supervisor técnico"

    if "autocad" in full_text or "planos" in full_text or "proyectista" in full_text:
        return "CV proyectista eléctrico / AutoCAD"

    if "tecnico" in title:
        return "CV general técnico-operativo"

    return "CV supervisor/residente de obra eléctrica"


def build_recommendation(
    final_score: float,
    critical_warnings: List[str],
    location_status: str,
    role_category: str,
    economic_comment: str,
) -> str:
    no_salary = "no muestra salario" in normalize_text(economic_comment)

    if "fuera de zona" in location_status:
        return "Descartar por ubicación o aplicar solo si acepta reubicación"

    if "baja relevancia" in role_category and final_score < 70:
        return "Descartar por baja relevancia del puesto"

    if final_score >= 82:
        if no_salary:
            return "Aplicar con ajustes: confirmar sueldo antes"

        if critical_warnings:
            return "Aplicar con advertencia: validar requisito crítico"

        return "Aplicar"

    if final_score >= 68:
        if critical_warnings:
            return "Aplicar con advertencia: validar requisito crítico"

        return "Aplicar con ajustes al CV"

    if final_score >= 55:
        return "Guardar y revisar manualmente"

    return "Descartar por ahora"


def analyze_job(candidate_profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    technical_result = calculate_technical_match(candidate_profile, job)

    economic_score, economic_comment, salary_penalty = calculate_economic_score(candidate_profile, job)
    critical_warnings, critical_penalty = detect_critical_warnings(candidate_profile, job)
    tools_to_confirm = detect_tools_to_confirm(job)
    tools_penalty = min(10, len(tools_to_confirm) * 3)

    location_score, location_status, location_penalty, location_category = assess_location_details(
        job,
        candidate_profile,
    )
    role_relevance_score, role_category, bad_title_penalty = assess_role_relevance(job)

    technical_score = technical_result["technical_score"]

    base_final_score = round(
        technical_score * 0.45
        + economic_score * 0.20
        + role_relevance_score * 0.25
        + location_score * 0.10,
        2,
    )

    final_score = round(
        base_final_score
        - critical_penalty
        - tools_penalty
        - salary_penalty
        - location_penalty
        - bad_title_penalty,
        2,
    )

    final_score = max(0, min(100, final_score))

    cv_route = recommend_cv_route(job, role_category)

    recommendation = build_recommendation(
        final_score=final_score,
        critical_warnings=critical_warnings,
        location_status=location_status,
        role_category=role_category,
        economic_comment=economic_comment,
    )

    return {
        "job_title": job.get("title", "Título no disponible"),
        "company": job.get("company", "Empresa no disponible"),
        "location": job.get("location", "Ubicación no disponible"),
        "source": job.get("source", "Fuente no disponible"),
        "source_url": job.get("source_url", "URL no disponible"),
        "apply_url": job.get("apply_url", "URL no disponible"),
        "salary_range": format_salary_range(job),

        "technical_score": technical_score,
        "economic_score": economic_score,
        "role_relevance_score": role_relevance_score,
        "location_score": location_score,

        "base_final_score": base_final_score,
        "critical_penalty": critical_penalty,
        "tools_penalty": tools_penalty,
        "salary_penalty": salary_penalty,
        "location_penalty": location_penalty,
        "bad_title_penalty": bad_title_penalty,
        "final_score": final_score,

        "role_category": role_category,
        "location_status": location_status,
        "location_category": location_category,
        "cv_route": cv_route,
        "recommendation": recommendation,
        "economic_comment": economic_comment,

        "matched_requirements": technical_result["matched_requirements"],
        "strong_equivalent_matches": technical_result["strong_equivalent_matches"],
        "partial_matches": technical_result["partial_matches"],
        "missing_requirements": technical_result["missing_requirements"],
        "critical_warnings": critical_warnings,
        "tools_to_confirm": tools_to_confirm,
    }
