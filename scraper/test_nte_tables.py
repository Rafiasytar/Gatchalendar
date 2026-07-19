import urllib.request, re, ssl

ssl._create_default_https_context = ssl._create_unverified_context

url = 'https://game8.co/games/Neverness-to-Everness/archives/607032'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    # search for the event list table
    # tables are usually in <table>...</table>
    tables = re.findall(r'<table[^>]*>.*?</table>', html, re.DOTALL)
    print("Found", len(tables), "tables")
    for i, t in enumerate(tables):
        # clean table html tags to read text
        cleaned = re.sub(r'<[^>]+>', ' ', t)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned_safe = cleaned.encode('ascii', 'ignore').decode('ascii')
        print(f"Table {i}: {cleaned_safe[:200]}...")
except Exception as e:
    print("Error:", e)
