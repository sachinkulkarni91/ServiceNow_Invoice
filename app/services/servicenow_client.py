
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
    import json
    import os
    import httpx
    from fastapi import HTTPException
    from app.core.config import SERVICENOW_AUTH, SERVICENOW_INSTANCE_URL
    from app.services.prompting import get_category_from_query, select_best_article_with_gemini

    # Map user query to category using Gemini and kb_category.json
    mapped_category = await get_category_from_query(query)
    if not mapped_category:
        raise HTTPException(status_code=404, detail="No matching category found.")

    # Load all articles from local file
    import json
    try:
        with open('all_articles.json', 'r', encoding='utf-8') as f:
            all_articles = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not load local articles file.")

    # Optionally filter by category and require non-empty text
    articles = [
        a for a in all_articles
        if a.get('category') == mapped_category and a.get('text') and a.get('text').strip()
    ]
    # Fallback: if no articles in category, use all articles with non-empty text
    if not articles:
        articles = [
            a for a in all_articles
            if a.get('text') and a.get('text').strip()
        ]
    if not articles:
        raise HTTPException(status_code=404, detail="No articles with content found.")

    # Prepare summaries for Gemini selection
    summaries = [
        {
            'short_description': a.get('short_description', ''),
            'text': a.get('text', ''),
            'sys_id': a.get('sys_id', ''),
        }
        for a in articles
    ]

    # Use Gemini to select the best article
    best_article = await select_best_article_with_gemini(query, summaries)
    if not best_article:
        raise HTTPException(status_code=404, detail="No relevant article found.")

    # Add ServiceNow link if sys_id is present
    from app.core.config import SERVICENOW_INSTANCE_URL
    sys_id = best_article.get('sys_id')
    link = f"{SERVICENOW_INSTANCE_URL}/kb_view.do?sys_kb_id={sys_id}" if sys_id else None
    best_article['link'] = link
    return best_article
