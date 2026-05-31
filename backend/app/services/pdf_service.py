import html
from app.models.resume import TailoredResume


def _e(text: str | None) -> str:
    """HTML-escape a string, return empty string if None."""
    return html.escape(text or "")


def _bullets(items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{_e(b)}</li>" for b in items)
    return f"<ul>{lis}</ul>"


def build_html(tailored: TailoredResume) -> str:
    s = tailored.sections
    contact = s.get("contact", {})
    parts = []

    # Contact line
    contact_bits = [
        _e(contact.get("email")),
        _e(contact.get("phone")),
        _e(contact.get("location")),
        _e(contact.get("linkedin")),
        _e(contact.get("github")),
    ]
    contact_line = " &nbsp;|&nbsp; ".join(b for b in contact_bits if b)

    # Summary
    if s.get("summary"):
        parts.append(f"""
        <section>
          <h2>Summary</h2>
          <p>{_e(s["summary"])}</p>
        </section>""")

    # Experience
    experience = s.get("experience", [])
    if experience:
        entries = ""
        for exp in experience:
            date_range = " – ".join(filter(None, [exp.get("start_date"), exp.get("end_date") or "Present"]))
            location = f", {_e(exp.get('location'))}" if exp.get("location") else ""
            entries += f"""
            <div class="entry">
              <div class="entry-header">
                <span class="entry-title">{_e(exp.get("role"))}</span>
                <span class="entry-date">{_e(date_range)}</span>
              </div>
              <div class="entry-subtitle">{_e(exp.get("company"))}{location}</div>
              {_bullets(exp.get("bullets", []))}
            </div>"""
        parts.append(f"<section><h2>Experience</h2>{entries}</section>")

    # Projects
    projects = s.get("projects", [])
    if projects:
        entries = ""
        for proj in projects:
            techs = ", ".join(_e(t) for t in proj.get("technologies", []))
            tech_line = f'<span class="entry-tech"> &mdash; {techs}</span>' if techs else ""
            entries += f"""
            <div class="entry">
              <div class="entry-header">
                <span class="entry-title">{_e(proj.get("name"))}{tech_line}</span>
              </div>
              {f'<div class="entry-subtitle">{_e(proj.get("description"))}</div>' if proj.get("description") else ""}
              {_bullets(proj.get("bullets", []))}
            </div>"""
        parts.append(f"<section><h2>Projects</h2>{entries}</section>")

    # Skills
    skills = s.get("skills", {})
    skill_rows = [
        ("Languages", skills.get("languages", [])),
        ("Frameworks", skills.get("frameworks", [])),
        ("Tools", skills.get("tools", [])),
        ("Other", skills.get("other", [])),
    ]
    skill_lines = "".join(
        f'<div class="skill-row"><span class="skill-label">{label}:</span> {", ".join(_e(x) for x in items)}</div>'
        for label, items in skill_rows if items
    )
    if skill_lines:
        parts.append(f"<section><h2>Skills</h2>{skill_lines}</section>")

    # Education
    education = s.get("education", [])
    if education:
        entries = ""
        for edu in education:
            degree_line = ", ".join(filter(None, [edu.get("degree"), edu.get("field")]))
            gpa = f" &nbsp;GPA: {_e(edu.get('gpa'))}" if edu.get("gpa") else ""
            entries += f"""
            <div class="entry">
              <div class="entry-header">
                <span class="entry-title">{_e(edu.get("institution"))}</span>
                <span class="entry-date">{_e(edu.get("graduation_date"))}</span>
              </div>
              {f'<div class="entry-subtitle">{_e(degree_line)}{gpa}</div>' if degree_line else ""}
            </div>"""
        parts.append(f"<section><h2>Education</h2>{entries}</section>")

    # Certifications
    certs = s.get("certifications", [])
    if certs:
        cert_list = "".join(f"<li>{_e(c)}</li>" for c in certs)
        parts.append(f"<section><h2>Certifications</h2><ul>{cert_list}</ul></section>")

    body = "\n".join(parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #111;
    padding: 36pt 42pt;
  }}
  h1 {{
    font-size: 20pt;
    font-weight: bold;
    letter-spacing: -0.3px;
    margin-bottom: 2pt;
  }}
  .contact-line {{
    font-size: 9pt;
    color: #444;
    margin-bottom: 16pt;
  }}
  section {{
    margin-bottom: 14pt;
  }}
  h2 {{
    font-size: 9.5pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #555;
    border-bottom: 0.75pt solid #ccc;
    padding-bottom: 2pt;
    margin-bottom: 7pt;
  }}
  p {{
    font-size: 10pt;
    color: #222;
  }}
  .entry {{
    margin-bottom: 9pt;
  }}
  .entry-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }}
  .entry-title {{
    font-weight: bold;
    font-size: 10.5pt;
  }}
  .entry-tech {{
    font-weight: normal;
    font-size: 9.5pt;
    color: #555;
  }}
  .entry-date {{
    font-size: 9pt;
    color: #555;
    white-space: nowrap;
  }}
  .entry-subtitle {{
    font-size: 10pt;
    color: #333;
    margin-top: 1pt;
  }}
  ul {{
    margin-top: 4pt;
    padding-left: 14pt;
  }}
  li {{
    margin-bottom: 2pt;
    font-size: 10pt;
  }}
  .skill-row {{
    font-size: 10pt;
    margin-bottom: 3pt;
  }}
  .skill-label {{
    font-weight: bold;
  }}
</style>
</head>
<body>
  <h1>{_e(contact.get("name", ""))}</h1>
  <div class="contact-line">{contact_line}</div>
  {body}
</body>
</html>"""


def render_pdf(tailored: TailoredResume) -> bytes:
    from weasyprint import HTML
    html_content = build_html(tailored)
    return HTML(string=html_content).write_pdf()
