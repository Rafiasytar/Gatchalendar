import urllib.request, urllib.parse, re, ssl

ssl._create_default_https_context = ssl._create_unverified_context

def search_images(query):
    try:
        url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # find image src or hrefs
        links = re.findall(r'src="(//external-content\.duckduckgo\.com/[^"]+)"', html)
        print(f"Query '{query}':")
        for idx, link in enumerate(links[:5]):
            print(f"  {idx}: https:{link}")
    except Exception as e:
        print(f"Failed: {e}")

search_images('Neverness to Everness wallpaper')
search_images('Persona 5 The Phantom X banner')
