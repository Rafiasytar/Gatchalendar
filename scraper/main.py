import json
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import uuid
import time

def parse_date(date_str):
    try:
        # Menghapus akhiran ordinal seperti st, nd, rd, th dari tanggal jika ada
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        dt = datetime.strptime(date_str, '%B %d, %Y')
        return dt.isoformat()
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        return datetime.now().isoformat()

def get_event_details(page_title):
    details = {
        'image_url': None,
        'long_description': None
    }
    
    headers = {'User-Agent': 'Gachalendar-Bot/2.0'}
    
    # 1. Get fallback image via action=query&prop=pageimages
    try:
        url_query = "https://genshin-impact.fandom.com/api.php"
        params_query = {
            "action": "query",
            "prop": "pageimages",
            "titles": page_title,
            "pithumbsize": 500,
            "redirects": 1,
            "format": "json"
        }
        res_query = requests.get(url_query, params=params_query, headers=headers)
        data_query = res_query.json()
        pages = data_query.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if 'thumbnail' in page_data and 'source' in page_data['thumbnail']:
                details['image_url'] = page_data['thumbnail']['source']
                # Bersihkan URL image
                if details['image_url'] and '/revision/latest' in details['image_url']:
                    details['image_url'] = details['image_url'].split('/revision/latest')[0] + '/revision/latest'
                break
    except Exception as e:
        print(f"Failed to get image for {page_title}: {e}")

    # 2. Get detailed description via action=parse
    try:
        url_parse = "https://genshin-impact.fandom.com/api.php"
        params_parse = {
            "action": "parse",
            "page": page_title,
            "redirects": 1,
            "format": "json",
            "prop": "text"
        }
        res_parse = requests.get(url_parse, params=params_parse, headers=headers)
        data_parse = res_parse.json()
        if 'parse' in data_parse:
            html_content = data_parse['parse']['text']['*']
            soup = BeautifulSoup(html_content, 'html.parser')
            content_div = soup.find('div', class_='mw-parser-output')
            if content_div:
                paragraphs = content_div.find_all('p', recursive=False)
                description_parts = []
                for p in paragraphs:
                    text = p.text.strip()
                    if len(text) > 10:
                        description_parts.append(text)
                    if len(" ".join(description_parts)) > 150 or len(description_parts) >= 2:
                        break
                if description_parts:
                    details['long_description'] = " ".join(description_parts)
    except Exception as e:
        print(f"Failed to get description for {page_title}: {e}")

    return details

def scrape_genshin_events():
    url = "https://genshin-impact.fandom.com/api.php"
    params = {
        "action": "parse",
        "page": "Event",
        "format": "json",
        "prop": "text"
    }
    headers = {'User-Agent': 'Gachalendar-Bot/2.0'}
    events = []
    
    try:
        print("Fetching Genshin Impact events...")
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        current_span = soup.find('span', id='Current')
        if current_span:
            table = current_span.parent.find_next_sibling('table', class_='wikitable')
            if table:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if len(cols) >= 3:
                        name = cols[0].text.strip()
                        duration_text = cols[1].text.strip()
                        event_type_text = cols[2].text.strip()
                        
                        dates = re.findall(r'([A-Z][a-z]+ \d{2}, \d{4})', duration_text)
                        if len(dates) >= 2:
                            start_time = parse_date(dates[0])
                            end_time = parse_date(dates[1])
                        else:
                            continue
                            
                        type_enum = "IN_GAME_EVENT"
                        if "Banner" in event_type_text or "Character Selection" in event_type_text or "Test Run" in event_type_text or "Epitome Invocation" in event_type_text or "Wishes" in event_type_text:
                            type_enum = "BANNER"
                            
                        image_url = None
                        detail_url = None
                        page_title = None
                        
                        # Cek link halaman detail
                        a_tag = cols[0].find('a')
                        if a_tag and a_tag.get('href'):
                            detail_url = "https://genshin-impact.fandom.com" + a_tag.get('href')
                            page_title = a_tag.get('title')
                            if "/" in page_title: # Terkadang titlenya "Event Name/2024-10-10"
                                page_title = page_title.split("/")[0]
                                
                        # Cek gambar dari tabel
                        img_tag = cols[0].find('img')
                        if img_tag:
                            image_url = img_tag.get('data-src') or img_tag.get('src')
                            if image_url and image_url.startswith("data:image"):
                                image_url = None
                            if image_url and '/revision/latest' in image_url:
                                image_url = image_url.split('/revision/latest')[0] + '/revision/latest'
                                
                        long_desc = None
                        
                        # Jika page_title ditemukan, ambil deskripsi panjang dan fallback gambar
                        if page_title:
                            print(f"Scraping details for: {page_title}")
                            details = get_event_details(page_title)
                            long_desc = details['long_description']
                            if not image_url and details['image_url']:
                                image_url = details['image_url']
                            time.sleep(0.5) # Jeda ringan agar tidak di-block
                            
                        event = {
                            "id": f"gi_{uuid.uuid4().hex[:8]}",
                            "gameId": "gi",
                            "title": name,
                            "description": event_type_text,
                            "longDescription": long_desc,
                            "startTime": start_time,
                            "endTime": end_time,
                            "type": type_enum,
                            "imageUrl": image_url,
                            "detailUrl": detail_url
                        }
                        events.append(event)
    except Exception as e:
        print(f"Failed to scrape Genshin events: {e}")
        
    return events

def get_dummy_events():
    now = datetime.now()
    return [
        {
            "id": f"hsr_{uuid.uuid4().hex[:8]}",
            "gameId": "hsr",
            "title": "Character Banner: Acheron (Dummy)",
            "description": "Boosted drop rate for Acheron",
            "longDescription": "This is a placeholder long description for the dummy Acheron banner. Real data will be fetched when Honkai Star Rail parser is implemented.",
            "startTime": now.isoformat(),
            "endTime": now.isoformat(),
            "type": "BANNER",
            "imageUrl": "https://static.wikia.nocookie.net/houkai-star-rail/images/c/c8/Item_Star_Rail_Special_Pass.png",
            "detailUrl": None
        },
        {
            "id": f"wuwa_{uuid.uuid4().hex[:8]}",
            "gameId": "wuwa",
            "title": "Resonator Convene: Yinlin (Dummy)",
            "description": "Featured resonator Yinlin",
            "longDescription": "This is a placeholder long description for Wuthering Waves event.",
            "startTime": now.isoformat(),
            "endTime": now.isoformat(),
            "type": "BANNER",
            "imageUrl": None,
            "detailUrl": None
        }
    ]

def main():
    print("Mulai mengambil data jadwal event dari internet...")
    genshin_events = scrape_genshin_events()
    print(f"Berhasil mendapatkan {len(genshin_events)} event Genshin Impact.")
    
    other_events = get_dummy_events()
    all_events = genshin_events + other_events

    output_file = "events.json"
    with open(output_file, 'w') as f:
        json.dump(all_events, f, indent=4)
        
    print(f"Berhasil menyimpan {len(all_events)} event ke dalam {output_file}")

if __name__ == "__main__":
    main()
