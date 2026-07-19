import urllib.request, urllib.parse, re, ssl

ssl._create_default_https_context = ssl._create_unverified_context

def search_ddg(query):
    try:
        url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        links = re.findall(r'src="(//external-content\.duckduckgo\.com/[^"]+)"', html)
        if links:
            print(f"Found: https:{links[0]}")
        else:
            print("Not found")
    except Exception as e:
        print(f"Failed: {e}")

search_ddg('Neverness to Everness icon')
