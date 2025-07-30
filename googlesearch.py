from googleapiclient.discovery import build

from config import Config

config = Config()


def google_search(query, api_key, cx, num=10):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cx, num=num).execute()
    return res.get("items", [])


search_query = "site:50safe.pl inurl:kontakt"
results = google_search(search_query, config.GOOGLE_SEARCH_API_KEY, config.SEARCH_ENGINE_ID)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Link: {result['link']}")
    print(f"Snippet: {result.get('snippet', 'No snippet available')}\n")
