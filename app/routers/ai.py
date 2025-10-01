
from ..services.servicenow_client import search_servicenow_knowledge
from fastapi import APIRouter, HTTPException, Body
from ..models.schemas import IncidentIn, SummaryOut, TextOut
from ..services.google_client import google_generate_content
from ..services.prompting import compose_incident_text, build_summary_prompt, build_worknotes_prompt, build_resolution_prompt

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

@router.post("/summarize-knowledge")
async def summarize_knowledge(query: str = Body(..., embed=True)):
    article = await search_servicenow_knowledge(query)
    if not article or not article.get("text"):
        raise HTTPException(status_code=404, detail="No relevant knowledge article found.")
    prompt = f"Summarize the following ServiceNow knowledge article in 2-3 sentences. Do not include any URLs or links or [https://kpmgadvisory5.service-now.com/kb_view.do?sys_kb_id=26bf9e4f8732aa50765dea483cbb359a](https://kpmgadvisory5.service-now.com/kb_view.do?sys_kb_id=26bf9e4f8732aa50765dea483cbb359a)\ in your answer.\n\nArticle: {article['text']}"
    import re
    summary = await google_generate_content(prompt)
    # Remove any URLs or 'Link:' lines from the summary
    summary = re.sub(r'Link:.*', '', summary)
    summary = re.sub(r'https?://[^\s)]+', '', summary)
    summary = re.sub(r'\(\s*\)', '', summary)
    summary = re.sub(r'\[\s*\]', '', summary)
    summary = re.sub(r'\n+', '\n', summary)
    summary = summary.strip()
    return {"summary": summary, "link": article.get("link")}

@router.post("/summarize-incident", response_model=SummaryOut)
async def summarize_incident_endpoint(incident: IncidentIn):
    try:
        text = compose_incident_text(incident.number, incident.short_description, incident.description, incident.latest_comments)
        prompt = build_summary_prompt(text)
        result = await google_generate_content(prompt)
        # Try to extract summary and key_facts from result (if JSON-like)
        import json
        summary = ""
        key_facts = []
        try:
            parsed = json.loads(result)
            summary = parsed.get("summary", "")
            key_facts = parsed.get("key_facts", [])
        except Exception:
            summary = result
        if not summary:
            raise HTTPException(status_code=502, detail="Failed to generate summary")
        return SummaryOut(summary=summary, key_facts=key_facts)
    except Exception as e:
        import traceback
        print(f"[EXCEPTION] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))

@router.post("/work-notes", response_model=TextOut)
async def work_notes_endpoint(incident: IncidentIn):
    try:
        text = compose_incident_text(incident.number, incident.short_description, incident.description, incident.latest_comments)
        prompt = build_worknotes_prompt(text)
        out = await google_generate_content(prompt)
        if not out:
            raise HTTPException(status_code=502, detail="Failed to generate work notes")
        return TextOut(text=out)
    except Exception as e:
        import traceback
        print(f"[EXCEPTION] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))

@router.post("/resolution-note", response_model=TextOut)
async def resolution_note_endpoint(incident: IncidentIn):
    try:
        text = compose_incident_text(incident.number, incident.short_description, incident.description, incident.latest_comments)
        prompt = build_resolution_prompt(text)
        out = await google_generate_content(prompt)
        if not out:
            raise HTTPException(status_code=502, detail="Failed to generate resolution note")
        return TextOut(text=out)
    except Exception as e:
        import traceback
        print(f"[EXCEPTION] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
