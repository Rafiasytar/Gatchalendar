import urllib.request, re

def get_qooapp_img(app_id):
    try:
        url = f'https://apps.qoo-app.com/en/app/{app_id}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        match = re.search(r'property="og:image" content="(https://[^"]+)"', html)
        if match:
            print(f"App {app_id}: {match.group(1)}")
        else:
            print(f"App {app_id}: Not found")
    except Exception as e:
        print(f"App {app_id} Error: {e}")

get_qooapp_img(35707) # NTE
get_qooapp_img(31952) # P5X global maybe? Let's check a few
get_qooapp_img(33355) # P5X KR/TW
get_qooapp_img(30154) # P5X CN
