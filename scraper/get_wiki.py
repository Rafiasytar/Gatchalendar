import urllib.request, re
try:
    url = 'https://wiki.biligame.com/endfield/%E9%A6%96%E9%A1%B5' # Homepage
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    links = re.findall(r'(https?://[^\s"\'\>]+?(?:png|jpg|webp))', html)
    for link in links:
        print(link)
except Exception as e:
    print(e)
