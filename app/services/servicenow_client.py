
from dotenv import load_dotenv
load_dotenv()
import httpx
import os

SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "https://your_instance.service-now.com")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME", "your_username")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "your_password")

async def search_servicenow_knowledge(query: str):
    from .google_client import google_generate_content
    import sys
    url = f"{SERVICENOW_INSTANCE_URL}/api/now/table/kb_knowledge"
    sysparm_query = f"short_descriptionLIKE{query}^ORtextLIKE{query}"
    params = {
        "sysparm_query": sysparm_query,
        "sysparm_limit": 400  # Fetch up to 400 articles for best semantic selection
    }
    auth = (SERVICENOW_USERNAME, SERVICENOW_PASSWORD)
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, params=params, auth=auth)
        r.raise_for_status()
        data = r.json()
        print("[DEBUG] ServiceNow API result:", data.get("result"), file=sys.stderr)
        if data.get("result"):
            # Log all fields for each article
            for idx, a in enumerate(data["result"]):
                print(f"[DEBUG] Article {idx+1} fields: {a}", file=sys.stderr)

            # Try to find a usable content field for each article
            def get_article_text(article):
                # Try common ServiceNow knowledge content fields
                for field in ["text", "article_body", "content", "kb_content", "description"]:
                    val = article.get(field)
                    if val and isinstance(val, str) and val.strip():
                        return val
                return None

            articles = [a for a in data["result"] if get_article_text(a)]
            if not articles:
                return None
            # Use Gemini to pick the most relevant article
            prompt = (
                f"Given the following user query and a list of knowledge articles, "
                f"choose the most relevant article and return ONLY its index (starting from 1).\n"
                f"User query: {query}\n"
                f"Articles:\n" + "\n".join([f"{i+1}. {a.get('short_description','')}" for i,a in enumerate(articles)])
            )
            try:
                idx_str = await google_generate_content(prompt)
                idx = int(''.join(filter(str.isdigit, idx_str))) - 1
                if 0 <= idx < len(articles):
                    article = articles[idx]
                    text = get_article_text(article) or ""
                    sys_id = article.get("sys_id", "")
                    link = f"{SERVICENOW_INSTANCE_URL}/kb_view.do?sys_kb_id={sys_id}" if sys_id else None
                    return {"text": text, "link": link}
            except Exception:
                pass
            # If Gemini cannot select, return the first article with content
            article = articles[0]
            text = get_article_text(article) or ""
            sys_id = article.get("sys_id", "")
            link = f"{SERVICENOW_INSTANCE_URL}/kb_view.do?sys_kb_id={sys_id}" if sys_id else None
            return {"text": text, "link": link}
        return None
