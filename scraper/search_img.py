import urllib.request, urllib.parse, json, os, ssl

ssl._create_default_https_context = ssl._create_unverified_context

def search_ddg(query):
    try:
        url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        import re
        links = re.findall(r'src="(//external-content\.duckduckgo\.com/[^"]+)"', html)
        if not links: print("No links found"); return
        for i, link in enumerate(links[:1]):
            img_url = "https:" + link
            print(f"Downloading {img_url}")
            data = urllib.request.urlopen(urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})).read()
            with open(f'app/src/main/res/drawable/icon_endfield.png', 'wb') as f:
                f.write(data)
            print(f"Saved icon_endfield.png")
    except Exception as e:
        print(f"Failed: {e}")

search_ddg('arknights endfield app icon png')
