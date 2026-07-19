import urllib.request, re

def get_taptap_img(app_id):
    try:
        url = f'https://www.taptap.io/app/{app_id}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        match = re.search(r'property="og:image" content="(https://img\.tapimg\.com/[^"]+)"', html)
        if match:
            print(f"App {app_id}: {match.group(1)}")
        else:
            print(f"App {app_id}: Not found")
    except Exception as e:
        print(f"App {app_id} Error: {e}")

get_taptap_img(336214)
