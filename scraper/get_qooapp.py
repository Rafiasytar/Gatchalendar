import urllib.request, re
try:
    url = 'https://apps.qoo-app.com/en/app/19933'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    match = re.search(r'property="og:image" content="(https://[^"]+)"', html)
    if match:
        img_url = match.group(1)
        print("Found:", img_url)
        data = urllib.request.urlopen(urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})).read()
        with open('app/src/main/res/drawable/icon_endfield.png', 'wb') as f:
            f.write(data)
        print("Saved!")
    else:
        print("Not found")
except Exception as e:
    print(e)
