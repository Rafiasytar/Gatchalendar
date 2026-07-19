import urllib.request, re
url = 'https://endfield.hypergryph.global/en'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
links = re.findall(r'(https?://[^\s\"\']+\.(?:png|jpg|webp))', html)
print('\n'.join(links))
