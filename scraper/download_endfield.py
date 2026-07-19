import urllib.request, re, os
url = 'https://endfield.hypergryph.global/en'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Search for anything that looks like an image
links = re.findall(r'(https?://[^\s"\'\>]+?(?:png|jpg|webp))', html)
for link in links:
    if 'logo' in link.lower() or 'icon' in link.lower():
        print("Found:", link)
        # Download it to app/src/main/res/drawable/endfield_logo.png
        try:
            req_img = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            img_data = urllib.request.urlopen(req_img).read()
            with open('app/src/main/res/drawable/endfield_logo.png', 'wb') as f:
                f.write(img_data)
            print("Successfully downloaded!")
            break
        except Exception as e:
            print("Download failed:", e)
