import requests

def search_fandom_images(wiki, query):
    url = f"https://{wiki}.fandom.com/api.php"
    # Try searching for pages first
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }
    headers = {"User-Agent": "Gachalendar-Bot/1.0"}
    try:
        r = requests.get(url, params=params, headers=headers).json()
        search_results = r.get("query", {}).get("search", [])
        print(f"Results for '{query}' on {wiki}:")
        for res in search_results:
            title = res["title"]
            print(f"  Page: {title}")
            # Get images on this page
            img_params = {
                "action": "query",
                "prop": "images",
                "titles": title,
                "format": "json"
            }
            img_res = requests.get(url, params=img_params, headers=headers).json()
            pages = img_res.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                images = pdata.get("images", [])
                for img in images:
                    img_title = img["title"]
                    # Get actual URL of the image
                    info_params = {
                        "action": "query",
                        "prop": "imageinfo",
                        "iiprop": "url",
                        "titles": img_title,
                        "format": "json"
                    }
                    info_res = requests.get(url, params=info_params, headers=headers).json()
                    ipages = info_res.get("query", {}).get("pages", {})
                    for ipid, ipdata in ipages.items():
                        info = ipdata.get("imageinfo", [])
                        if info:
                            print(f"    Image '{img_title}': {info[0]['url']}")
    except Exception as e:
        print(f"Failed: {e}")

search_fandom_images("megamitensei", "Minami Miyashita")
search_fandom_images("megamitensei", "Shirosato Beach")
search_fandom_images("megamitensei", "Lufel")
