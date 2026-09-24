"""
Builds assets/CV_EN.pdf and assets/CV_ES.pdf from one shared layout, so the
two language versions are a genuinely matched set rather than two documents
that happen to look similar. Content lives in DATA below — edit that, not
the layout code, for routine updates (a new job, a reworded bullet, etc.).

Requires: reportlab (`pip install reportlab`)
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
BLUE = colors.HexColor("#1F4E79")
LINK_COLOR = "#0563C1"
FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"

styles = {
    "name": ParagraphStyle("name", fontName=FONT_BOLD, fontSize=20, leading=24,
                           alignment=TA_CENTER, spaceAfter=4),
    "contact": ParagraphStyle("contact", fontName=FONT, fontSize=9.5, leading=13,
                              alignment=TA_CENTER, spaceAfter=2, textColor=colors.HexColor("#333333")),
    "tagline": ParagraphStyle("tagline", fontName=FONT, fontSize=9.5, leading=13,
                              alignment=TA_CENTER, spaceAfter=14, textColor=colors.HexColor("#444444")),
    "header": ParagraphStyle("header", fontName=FONT_BOLD, fontSize=12, leading=16,
                             spaceBefore=12, spaceAfter=2, textColor=colors.black),
    "body": ParagraphStyle("body", fontName=FONT, fontSize=9.7, leading=13.5, spaceAfter=5),
    "job": ParagraphStyle("job", fontName=FONT, fontSize=9.7, leading=13.5,
                          spaceBefore=8, spaceAfter=3),
    "bullet": ParagraphStyle("bullet", fontName=FONT, fontSize=9.7, leading=13.5,
                             leftIndent=14, firstLineIndent=-11, spaceAfter=3),
    "skill": ParagraphStyle("skill", fontName=FONT, fontSize=9.7, leading=13.5, spaceAfter=3),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def section_header(story, text):
    story.append(Paragraph(esc(text).upper(), styles["header"]))
    story.append(HRFlowable(width="100%", thickness=1.3, color=BLUE, spaceAfter=6, spaceBefore=0))


def job_header(story, title, org, dept, dates):
    parts = [f"<b>{esc(title)}</b>"]
    if org:
        parts.append(f" | {esc(org)}")
    if dept:
        parts.append(f" — <i>{esc(dept)}</i>")
    parts.append(f" | {esc(dates)}")
    story.append(Paragraph("".join(parts), styles["job"]))


def bullet(story, text):
    story.append(Paragraph(f"•&nbsp;&nbsp;{esc(text)}", styles["bullet"]))


def skill_line(story, label, items):
    story.append(Paragraph(f"<b>{esc(label)}:</b> {esc(items)}", styles["skill"]))


def build(lang, d, out_path):
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
    )
    story = []

    story.append(Paragraph(esc(d["name"]), styles["name"]))
    story.append(Paragraph(
        f'{esc(d["city"])} • <link href="mailto:{d["email"]}" color="{LINK_COLOR}"><u>{esc(d["email"])}</u></link>'
        f' • {esc(d["phone"])} • '
        f'<link href="{d["linkedin_url"]}" color="{LINK_COLOR}"><u>{esc(d["linkedin_label"])}</u></link>',
        styles["contact"],
    ))
    story.append(Paragraph(esc(d["tagline"]), styles["tagline"]))

    section_header(story, d["headers"]["profile"])
    story.append(Paragraph(esc(d["profile"]), styles["body"]))

    section_header(story, d["headers"]["skills"])
    for label, items in d["skills"]:
        skill_line(story, label, items)

    section_header(story, d["headers"]["experience"])
    for job in d["experience"]:
        job_header(story, job["title"], job["org"], job.get("dept"), job["dates"])
        for b in job["bullets"]:
            bullet(story, b)

    section_header(story, d["headers"]["education"])
    for ed in d["education"]:
        job_header(story, ed["title"], ed["org"], None, ed["dates"])
        if ed.get("line"):
            story.append(Paragraph(esc(ed["line"]), styles["body"]))
        if ed.get("subhead"):
            story.append(Paragraph(f'<b>{esc(ed["subhead"])}</b>', styles["body"]))
        for b in ed.get("bullets", []):
            bullet(story, b)

    section_header(story, d["headers"]["certifications"])
    for c in d["certifications"]:
        bullet(story, c)

    section_header(story, d["headers"]["languages"])
    story.append(Paragraph(esc(d["languages"]), styles["body"]))

    doc.build(story)
    print(f"wrote {out_path}")


CONTACT = {
    "city": "Madrid",
    "email": "gideondavinsky@gmail.com",
    "phone": "+34 652 628 678",
    "linkedin_label": "www.linkedin.com/in/gideon-davinsky",
    "linkedin_url": "https://www.linkedin.com/in/gideon-davinsky",
}

DATA = {
    "es": {
        **CONTACT,
        "name": "GIDEON DAVINSKY",
        "tagline": "Inglés nativo • español C1 • Buscando oportunidades en SIG, movilidad y ciudades inteligentes",
        "headers": {
            "profile": "Perfil profesional", "skills": "Habilidades técnicas", "experience": "Experiencia profesional",
            "education": "Formación académica", "certifications": "Formación complementaria y certificaciones",
            "languages": "Idiomas",
        },
        "profile": (
            "Técnico SIG y analista de movilidad urbana con experiencia práctica en ArcGIS Pro, QGIS y Python, "
            "actualmente desarrollando análisis espacial aplicado a la accesibilidad y la movilidad sostenible "
            "en la Subdirección de Innovación e Información Urbana del Ayuntamiento de Madrid. Candidato a "
            "Máster en Ciudades Inteligentes y Sostenibles en la UCM."
        ),
        "skills": [
            ("SIG y análisis espacial", "ArcGIS Pro, QGIS, GTFS, análisis ráster y vectorial, cartografía técnica"),
            ("Datos y programación", "Python, Excel avanzado, SQL, gestión de bases de datos espaciales, modelado de datos climáticos"),
            ("Diseño y comunicación", "Adobe Illustrator y Photoshop, PowerPoint, Canva, redacción técnica bilingüe (EN/ES)"),
            ("Nivel iniciación", "AutoCAD, Revit, Bentley iTwin"),
        ],
        "experience": [
            {
                "title": "Becario SIG", "org": "Ayuntamiento de Madrid",
                "dept": "Subdirección de Innovación e Información Urbana", "dates": "Abr 2026 – Jul 2026",
                "bullets": [
                    "Modelizar corredores peatonales desde 12 centros de trabajo municipales mediante Network Analyst en ArcGIS Pro, optimizando por variables ambientales y morfologías urbanas.",
                    "Construir una capa de clasificación viaria integrando rásteres de pendiente e insolación solar, generando índices de accesibilidad física adoptados directamente en las propuestas de política de movilidad del departamento.",
                    "Procesar y validar una base de datos espacial de variables (MDT de orientación y radiación, NDVI) a escala municipal, permitiendo identificar y priorizar zonas de intervención urbana.",
                    "Desarrollar un modelo multicriterio de selección de ubicaciones para nuevos alcorques, integrando capas de sombra, pendiente y cobertura arbórea.",
                    "Elaborar productos cartográficos técnicos de escala avanzada empleados como evidencia en decisiones de política pública sobre accesibilidad universal y movilidad sostenible; ponente invitado en la Jornada de Geodatos (noviembre de 2026, Ayuntamiento de Madrid).",
                    "Trabajar en entorno ArcGIS Enterprise (Server, Portal, geodatabase corporativa), además de ArcGIS Online, Experience Builder y Survey123 para la recogida de datos de campo.",
                ],
            },
            {
                "title": "Auxiliar de Conversación (inglés)", "org": "Comunidad de Madrid",
                "dept": "IES Alonso Quijano / Colegio Santa María la Blanca", "dates": "Oct 2022 – Jun 2025",
                "bullets": [
                    "Diseñar e impartir de forma autónoma programas de inglés oral a grupos de hasta 15 alumnos de primaria y secundaria, logrando mejoras medibles en tasas de participación oral.",
                    "Codesarrollar unidades didácticas bilingües adoptadas a nivel de centro para el curso académico siguiente, en colaboración con el equipo docente de 4 asignaturas.",
                ],
            },
            {
                "title": "Supervisor de Equipo de Campaña", "org": "Georgia CAN", "dept": "Atlanta, GA",
                "dates": "May – Jul 2022",
                "bullets": [
                    "Dirigir un equipo de 15-25 encuestadores en Atlanta, contactando y encuestando a más de 8.000 votantes registrados; equipo reconocido como el más productivo de EE. UU. por la organización nacional.",
                    "Utilizar bases de datos georreferenciadas de votantes para diseñar una estrategia de captación por zonas de alto impacto electoral; el candidato ganó las elecciones por 2.000 votos.",
                ],
            },
            {
                "title": "Becario de Investigación", "org": "CARE Corporate Partnerships Team", "dept": "Washington, DC",
                "dates": "Ago – Dic 2021",
                "bullets": [
                    "Desarrollar y presentar un informe sectorial sobre la industria del cacao ante equipos en tres continentes, fundamentando directamente la posición de CARE ante la Comisión Europea en materia de sostenibilidad en la cadena de suministro.",
                    "Elaborar mapas geoespaciales de los programas de intervención de CARE en África Occidental para presentaciones ante grandes donantes internacionales.",
                    "Interactuar con partes interesadas corporativas en múltiples jurisdicciones, consolidando relaciones institucionales en un contexto de desarrollo internacional.",
                ],
            },
        ],
        "education": [
            {
                "title": "Máster en Ciudades Inteligentes y Sostenibles", "org": "Universidad Complutense de Madrid",
                "dates": "2025 – 2026",
                "line": "Materias relevantes: Movilidad urbana y transporte inteligente · Resiliencia en ciudades inteligentes · Análisis de datos geoespaciales",
                "subhead": "Trabajos académicos:",
                "bullets": [
                    "Análisis de riesgo de inundación fluvial y resiliencia urbana — Logroño, España (ArcGIS Pro, modelización hidrológica)",
                    "Diagnóstico de accesibilidad hospitalario en Atlanta, GA — análisis de reparto modal e índices de accesibilidad espacial",
                ],
            },
            {
                "title": "Doble Grado en Ciencias Políticas y Relaciones Internacionales",
                "org": "Universidad de Georgia, EE. UU.", "dates": "2018 – 2022",
            },
        ],
        "certifications": [
            "Certificado TEFL — CIEE (Council on International Educational Exchange)",
            "QGIS y GRASS — 80 horas, Grupo TYC GIS Formación (feb – abr 2025): análisis ráster/vectorial con librerías GDAL/OGR, integración con GRASS para procesamiento digital de imágenes y análisis geoespacial avanzado",
        ],
        "languages": "inglés — Nativo | español — C1 (competencia profesional plena)",
    },

    "en": {
        **CONTACT,
        "name": "GIDEON DAVINSKY",
        "tagline": "English (native) • Spanish (C1) • Seeking opportunities in GIS, mobility, and smart cities",
        "headers": {
            "profile": "Profile", "skills": "Technical skills", "experience": "Professional experience",
            "education": "Education", "certifications": "Certifications & training", "languages": "Languages",
        },
        "profile": (
            "Policy researcher and urban data analyst with experience producing data-backed analysis for "
            "government institutions, international development organizations, and public administrations. "
            "Background spans geospatial analysis applied to urban mobility and environmental sustainability, "
            "international policy research contributing to European Commission submissions, and academic work "
            "on urban resilience, climate risk, and city governance. Bilingual English–Spanish with strong "
            "written and oral communication skills for both specialist and non-specialist audiences."
        ),
        "skills": [
            ("GIS & spatial analysis", "ArcGIS Pro (advanced), QGIS (advanced), Network Analyst, GRASS, GDAL/OGR, raster/vector analysis, ArcGIS Online, ArcGIS Enterprise (working knowledge), Survey123, Experience Builder, GTFS"),
            ("Data & programming", "Python (competent), Excel (advanced), R, spatial database management, environmental data modelling"),
            ("Design & communication", "Adobe Illustrator, Photoshop, PowerPoint — bilingual technical report writing (English/Spanish)"),
            ("Beginner", "AutoCAD, Revit, Bentley iTwin"),
        ],
        "experience": [
            {
                "title": "GIS & Urban Data Analyst (Internship)", "org": "Ayuntamiento de Madrid",
                "dept": "Subdirección de Innovación e Información Urbana", "dates": "Apr 2026 – Jul 2026",
                "bullets": [
                    "Conducted spatial analysis and modelling for urban mobility policy, including pedestrian network optimization across 12 municipal work centers (ArcGIS Pro, Network Analyst), producing route recommendations adopted in sustainability policy proposals.",
                    "Built a Seasonal Pedestrian Accessibility Index integrating slope, solar radiation and sidewalk width data across the full Madrid street network, translating multi-variable spatial databases into a composite indicator for policy decision-making.",
                    "Performed NDVI vegetation analysis of Parque del Retiro using multitemporal satellite imagery to assess urban green cover change — directly applicable to nature-based solutions and urban environmental monitoring.",
                    "Developed a multicriteria spatial evaluation framework for new urban tree pit locations integrating shadow, slope and coverage layers — a methodology applicable to urban biodiversity assessments.",
                    "Produced technical reports and cartographic outputs used as evidence in accessibility and sustainable mobility policy decisions at municipal level; invited to present findings at the Jornada de Geodatos (November 2026) hosted by the Ayuntamiento de Madrid.",
                    "Worked within ArcGIS Enterprise environment (Server, Portal, enterprise geodatabase); hands-on use of ArcGIS Online, Experience Builder, and Survey123 for field data management.",
                ],
            },
            {
                "title": "English Language Assistant", "org": "Comunidad de Madrid",
                "dept": "IES Alonso Quijano / Colegio Santa María la Blanca", "dates": "Oct 2022 – Jun 2025",
                "bullets": [
                    "Designed and delivered English curriculum to groups of up to 15 students; co-developed bilingual frameworks adopted school-wide — demonstrating capacity to organize and present complex material to diverse audiences.",
                ],
            },
            {
                "title": "Canvass Supervisor", "org": "Georgia CAN", "dept": "Atlanta, GA", "dates": "May – Jul 2022",
                "bullets": [
                    "Led a team of 15–25 field surveyors contacting over 8,000 registered voters using geo-targeted voter databases to direct field strategy. Team recognized as most productive nationally; candidate won by 2,000 votes.",
                ],
            },
            {
                "title": "Research Intern, Corporate Partnerships", "org": "CARE USA", "dept": "Washington, DC",
                "dates": "Aug – Dec 2021",
                "bullets": [
                    "Produced a cross-sector analysis of the cocoa supply chain industry presented to teams across three continents, directly informing CARE's position paper submitted to the European Commission on supply chain sustainability.",
                    "Created geospatial maps of CARE intervention programs across West Africa for major international donor presentations, demonstrating experience communicating complex data to non-specialist policymaker audiences.",
                    "Engaged with corporate stakeholders across multiple jurisdictions, building institutional relationships in an international development context.",
                ],
            },
        ],
        "education": [
            {
                "title": "Master's in Smart and Sustainable Cities", "org": "Universidad Complutense de Madrid",
                "dates": "2025 – 2026 (pending thesis)",
                "line": "Relevant coursework: Urban mobility and transport · Climate resilience and city governance · Geospatial data analysis · Sustainability indicators and reporting · Urban environmental policy",
                "subhead": "Research:",
                "bullets": [
                    "Flood risk and urban resilience analysis, Logroño, Spain (ArcGIS Pro, hydrological modelling)",
                    "Hospital accessibility diagnostic, Atlanta, GA (modal split analysis, spatial accessibility indices)",
                ],
            },
            {
                "title": "Double B.A. Political Science & International Affairs",
                "org": "University of Georgia, Athens, GA, USA", "dates": "2018 – 2022",
                "line": "Coursework in comparative politics, international development, environmental policy, and quantitative research methods.",
            },
        ],
        "certifications": [
            "QGIS & GRASS – 80-hour professional course, Grupo TYC GIS Formación (Feb–Apr 2025): raster/vector analysis via GDAL/OGR libraries, GRASS integration for digital image processing and advanced geospatial analysis",
            "TEFL Certificate – CIEE (Council on International Educational Exchange)",
        ],
        "languages": "English — Native | Spanish — C1 (full professional proficiency)",
    },
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for lang in ("es", "en"):
        out_path = os.path.join(OUT_DIR, f"CV_{lang.upper()}.pdf")
        build(lang, DATA[lang], out_path)


if __name__ == "__main__":
    main()
