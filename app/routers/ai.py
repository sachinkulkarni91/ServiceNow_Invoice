
from ..services.servicenow_client import search_servicenow_knowledge
from fastapi import APIRouter, HTTPException, Body
from ..models.schemas import IncidentIn, TextOut, WorkNotesOut, IncidentSummaryOut, ResolutionNoteOut
from ..services.google_client import google_generate_content
from ..services.prompting import compose_incident_text, build_summary_prompt, build_worknotes_prompt, build_resolution_prompt

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

@router.post("/summarize-knowledge")
async def summarize_knowledge(query: str = Body(..., embed=True)):
    article = await search_servicenow_knowledge(query)
    if not article or not article.get("text"):
        raise HTTPException(status_code=404, detail="No relevant knowledge article found.")
    prompt = f"Summarize the following ServiceNow knowledge article in 2-3 sentences. Do not include any URLs or links or [https://kpmgadvisory5.service-now.com/kb_view.do?sys_kb_id=26bf9e4f8732aa50765dea483cbb359a](https://kpmgadvisory5.service-now.com/kb_view.do?sys_kb_id=26bf9e4f8732aa50765dea483cbb359a) in your answer.\n\nArticle: {article['text']}"
    import re
    try:
        summary = await google_generate_content(prompt)
    except Exception as e:
        # Fallback for Gemini 429 or other errors
        import sys
        print(f"[Gemini fallback in summarize_knowledge] {type(e).__name__}: {e}", file=sys.stderr)
        summary = article['text'][:400] + ("..." if len(article['text']) > 400 else "")
    # Remove any URLs or 'Link:' lines from the summary
    summary = re.sub(r'Link:.*', '', summary)
    summary = re.sub(r'https?://[^\s)]+', '', summary)
    summary = re.sub(r'\(\s*\)', '', summary)
    summary = re.sub(r'\[\s*\]', '', summary)
    summary = re.sub(r'\n+', '\n', summary)
    summary = summary.strip()
    # Always return the link field from the selected article (if present)
    link = article.get("link")
    if not link and article.get("sys_id"):
        from app.core.config import SERVICENOW_INSTANCE_URL
        link = f"{SERVICENOW_INSTANCE_URL}/kb_view.do?sys_kb_id={article['sys_id']}"
    return {"summary": summary, "link": link}

@router.post("/summarize-incident", response_model=IncidentSummaryOut)
async def summarize_incident_endpoint(incident: IncidentIn):
    try:
        text = compose_incident_text(incident.number, incident.short_description, incident.description, incident.latest_comments)
        # Explicit prompt for structured JSON output
        prompt = (
            f"""
Given the following incident details, extract:
- issue: a concise description of the main problem only (do not include actions or resolutions)
- actions_taken: a list of actions or steps performed to address the issue (as a JSON array of strings)
Return only a valid JSON object with these two fields: {{\n  \"issue\": string, \"actions_taken\": [string, ...]\n}}

Incident details:\n{text}
"""
        )
        result = await google_generate_content(prompt)
        import json, re
        issue = ""
        actions_taken = []
        try:
            parsed = json.loads(result)
            # Use only the short_description or description for issue
            issue = incident.short_description or incident.description or parsed.get("issue", "")
            actions_taken = parsed.get("actions_taken", [])
        except Exception:
            # Fallback: try to extract actions as bullet points, filter out number/short_description/comments
            issue = incident.short_description or incident.description or ""
            # Try to extract actions as bullet points
            actions = re.findall(r'\*\s*(.+)', result)
            if not actions:
                # Try splitting by newlines or dashes
                actions = [line.strip('- ').strip() for line in result.split('\n') if line.strip().startswith('-') or line.strip().startswith('*')]
            # Remove lines that repeat number, short_description, or comments
            filter_phrases = [
                f"Number: {incident.number}" if incident.number else None,
                f"Short description: {incident.short_description}" if incident.short_description else None,
                f"Description: {incident.description}" if incident.description else None,
                "Latest comments:",
            ]
            filter_phrases = [p for p in filter_phrases if p]
            actions_taken = [a for a in actions if not any(p in a for p in filter_phrases)]
        if not issue:
            raise HTTPException(status_code=502, detail="Failed to generate summary")
        return {"issue": issue, "actions_taken": actions_taken}
    except Exception as e:
        import traceback
        print(f"[EXCEPTION] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))

@router.post("/work-notes", response_model=WorkNotesOut)
async def work_notes_endpoint(incident: IncidentIn):
    try:
        text = compose_incident_text(incident.number, incident.short_description, incident.description, incident.latest_comments)
        prompt = build_worknotes_prompt(text)
        out = await google_generate_content(prompt)
        if not out:
            raise HTTPException(status_code=502, detail="Failed to generate work notes")
        # Split actions_taken into a list by bullet points or asterisks
        import re
        # Replace newlines with spaces for consistent splitting
        out_clean = out.replace('\r', ' ').replace('\n', ' ')
        # Split on '*', '-', or numbered bullets, and remove empty entries
        steps = re.split(r'\*|\s*-\s+|\d+\.\s+', out_clean)
        steps = [s.strip() for s in steps if s.strip()]
        # Use short_description or description for issue
        issue = incident.short_description or incident.description or ""
        return {"issue": issue, "actions_taken": steps}
    except Exception as e:
        import traceback
        print(f"[EXCEPTION] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))

@router.post("/resolution-note", response_model=ResolutionNoteOut)
async def resolution_note_endpoint(incident: IncidentIn):
    try:
        text = compose_incident_text(incident.number, incident.short_description, incident.description, incident.latest_comments)
        prompt = (
            f"""
Given the following incident details, extract and return only a valid JSON object with these fields:
- root_cause: the underlying cause of the issue
- fix_applied: the fix or solution implemented
- validation: how the fix was validated
- preventive_action: steps taken to prevent recurrence
Format: {{\n  \"root_cause\": string, \"fix_applied\": string, \"validation\": string, \"preventive_action\": string\n}}

Incident details:\n{text}
"""
        )
        out = await google_generate_content(prompt)
        import json, re
        try:
            parsed = json.loads(out)
            root_cause = parsed.get("root_cause", "")
            fix_applied = parsed.get("fix_applied", "")
            validation = parsed.get("validation", "")
            preventive_action = parsed.get("preventive_action", "")
        except Exception:
            # Fallback: try to extract with regex or return empty fields
            root_cause = fix_applied = validation = preventive_action = ""
            match = re.search(r'root[_ ]cause[:\-]?\s*(.+?)(?:\n|$)', out, re.IGNORECASE)
            if match:
                root_cause = match.group(1).strip()
            match = re.search(r'fix[_ ]applied[:\-]?\s*(.+?)(?:\n|$)', out, re.IGNORECASE)
            if match:
                fix_applied = match.group(1).strip()
            match = re.search(r'validation[:\-]?\s*(.+?)(?:\n|$)', out, re.IGNORECASE)
            if match:
                validation = match.group(1).strip()
            match = re.search(r'preventive[_ ]action[:\-]?\s*(.+?)(?:\n|$)', out, re.IGNORECASE)
            if match:
                preventive_action = match.group(1).strip()
        if not (root_cause or fix_applied or validation or preventive_action):
            raise HTTPException(status_code=502, detail="Failed to generate resolution note")
        return {
            "root_cause": root_cause,
            "fix_applied": fix_applied,
            "validation": validation,
            "preventive_action": preventive_action
        }
    except Exception as e:
        import traceback
        print(f"[EXCEPTION] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
