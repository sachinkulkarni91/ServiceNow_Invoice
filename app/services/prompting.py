def compose_incident_text(number: str | None, short_description: str | None, description: str | None, latest_comments: list[str]) -> str:
    lines = []
    if number: lines.append(f"Number: {number}")
    if short_description: lines.append(f"Short description: {short_description}")
    if description: lines.append(f"Description: {description}")
    if latest_comments:
        lines.append("Latest comments:")
        lines.extend([f"- {c}" for c in latest_comments[:3]])
    return "\n".join(lines)

def build_summary_prompt(incident_text: str) -> str:
    return (
        "Create a 4–6 line summary for an L1/L2 analyst. "
        "Prioritize: symptoms, impact, affected resources, what's been tried. "
        "Keep it factual. No PII. No hallucinations.\n\n"
        f"Incident:\n{incident_text}\n\nReturn: {{\"summary\": \"...\"}}"
    )

def build_worknotes_prompt(incident_text: str) -> str:
    return (
        "Draft concise technician work notes as bullet points (max 8). "
        "Include checks performed, findings, approvals. No PII. Return plain text.\n\n"
        f"{incident_text}"
    )

def build_resolution_prompt(incident_text: str) -> str:
    return (
        "Draft a final resolution note with: Root cause, Fix applied, Validation, Preventive action. "
        "6–10 lines, plain text. No PII.\n\n"
        f"{incident_text}"
    )
