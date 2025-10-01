import os
import httpx
import json
from app.core.config import SERVICENOW_INSTANCE_URL, SERVICENOW_AUTH

async def fetch_all_servicenow_articles(category=None, limit=1000):
    """
    Fetch all ServiceNow knowledge articles (optionally by category) and save to all_articles.json.
    """
    servicenow_url = f"{SERVICENOW_INSTANCE_URL}/api/now/table/kb_knowledge"
    params = {
        'active': 'true',
        'workflow_state': 'published',
        'sysparm_limit': limit
    }
    if category:
        params['category'] = category
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Basic {SERVICENOW_AUTH}'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(servicenow_url, params=params, headers=headers)
        response.raise_for_status()
        articles = response.json().get('result', [])
    # Save to file
    with open('all_articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(articles)} articles to all_articles.json")

# Usage example (in an async context):
# import asyncio
# asyncio.run(fetch_all_servicenow_articles())

# Allow running as a script
if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_all_servicenow_articles())
