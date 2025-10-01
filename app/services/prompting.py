
import typing
from app.services.google_client import google_generate_content

async def select_best_article_with_gemini(query: str, summaries: list[dict]) -> typing.Optional[dict]:
    if not summaries:
        return None
    # Build prompt for Gemini
    articles_list = "\n".join([
        f"{i+1}. {s.get('short_description','') or s.get('text','')[:100]}" for i, s in enumerate(summaries)
    ])
    prompt = (
        f"Given the following user query and a list of knowledge articles, "
        f"choose the most relevant article and return ONLY its index (starting from 1).\n"
        f"User query: {query}\n"
        f"Articles:\n{articles_list}"
    )
    try:
        idx_str = await google_generate_content(prompt)
        idx = int(''.join(filter(str.isdigit, idx_str))) - 1
        if 0 <= idx < len(summaries):
            return summaries[idx]
    except Exception as e:
        # Fallback: if Gemini quota exceeded or any error, return the first article
        import sys
        print(f"[Gemini fallback] {type(e).__name__}: {e}", file=sys.stderr)
        return summaries[0]
    # Fallback: return the first article
    return summaries[0]
import typing

# TEMP: Async stub for category extraction. Replace with Gemini logic as needed.
async def get_category_from_query(query: str) -> typing.Optional[str]:
    # TODO: Replace with Gemini/LLM-based category extraction and kb_category.json mapping
    # For now, always return 'Policies' for testing
    return "Policies"
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
