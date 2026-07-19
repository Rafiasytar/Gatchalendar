import urllib.request, re
try:
    url = 'https://www.taptap.io/app/232454'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    match = re.search(r'"(https://img\.tapimg\.com/[^"]+\.png[^"]*)"', html)
    if match:
        print('Found:', match.group(1))
    else:
        print('Not found')
except Exception as e:
    print(e)
