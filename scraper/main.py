import json
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta, timezone
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
                            
                        # Attempt to fetch character card for Test Run if no image
                        if not image_url and "Test Run -" in name:
                            try:
                                chars = name.split("Test Run -")[1].strip()
                                first_char = chars.split(",")[0].strip()
                                print(f"Fetching character card for: {first_char}")
                                char_url = f"https://genshin-impact.fandom.com/api.php?action=query&prop=pageimages&titles={first_char}&pithumbsize=1000&format=json"
                                char_res = requests.get(char_url, headers={'User-Agent': 'Gachalendar-Bot/1.0'}).json()
                                pages = char_res.get('query', {}).get('pages', {})
                                for page_id, page_data in pages.items():
                                    if 'thumbnail' in page_data:
                                        raw_thumb = page_data['thumbnail']['source']
                                        if '/revision/latest' in raw_thumb:
                                            image_url = raw_thumb.split('/revision/latest')[0] + '/revision/latest'
                                        else:
                                            image_url = raw_thumb
                                        break
                            except Exception as e:
                                print(f"Failed to fetch char card: {e}")
                            
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

def scrape_hsr_events():
    url = "https://honkai-star-rail.fandom.com/api.php"
    params = {
        "action": "parse",
        "page": "Events",
        "format": "json",
        "prop": "text"
    }
    headers = {'User-Agent': 'Gachalendar-Bot/2.0'}
    events = []
    
    try:
        print("Fetching Honkai Star Rail events...")
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        tables = soup.find_all('table', class_='wikitable')
        if tables:
            rows = tables[0].find_all('tr')[1:] # Current events table
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 3:
                    name_td = cols[0]
                    a_tags = name_td.find_all('a')
                    title = a_tags[-1].text.strip() if a_tags else name_td.text.strip()
                    
                    duration_text = cols[1].text.strip()
                    type_text = cols[2].text.strip()
                    
                    dates = re.findall(r'([A-Z][a-z]+ \d{1,2}, \d{4})', duration_text)
                    if len(dates) >= 2:
                        start_time = parse_date(dates[0])
                        end_time = parse_date(dates[1])
                    else:
                        continue
                        
                    type_enum = "IN_GAME_EVENT"
                    if "Warp" in title or "Warp" in type_text or "Character Event" in title:
                        type_enum = "BANNER"
                        
                    image_url = None
                    img = name_td.find('img')
                    if img:
                        image_url = img.get('data-src') or img.get('src')
                        if image_url and image_url.startswith("data:image"):
                            image_url = None
                        if image_url and '/revision/latest' in image_url:
                            image_url = image_url.split('/revision/latest')[0] + '/revision/latest'
                            
                    if not image_url and a_tags:
                        page_title = a_tags[-1].get('title')
                        if page_title:
                            if "/" in page_title:
                                page_title = page_title.split("/")[0]
                            try:
                                print(f"Fetching fallback image for HSR: {page_title}")
                                url_query = "https://honkai-star-rail.fandom.com/api.php"
                                params_query = {
                                    "action": "query",
                                    "prop": "pageimages",
                                    "titles": page_title,
                                    "pithumbsize": 500,
                                    "redirects": 1,
                                    "format": "json"
                                }
                                res_query = requests.get(url_query, params=params_query, headers=headers).json()
                                pages = res_query.get('query', {}).get('pages', {})
                                for page_id, page_data in pages.items():
                                    if 'thumbnail' in page_data and 'source' in page_data['thumbnail']:
                                        image_url = page_data['thumbnail']['source']
                                        if image_url and '/revision/latest' in image_url:
                                            image_url = image_url.split('/revision/latest')[0] + '/revision/latest'
                                        break
                                time.sleep(0.5)
                            except Exception as e:
                                print(f"Failed to get fallback image for HSR {page_title}: {e}")
                            
                    event = {
                        "id": f"hsr_{uuid.uuid4().hex[:8]}",
                        "gameId": "hsr",
                        "title": title,
                        "description": type_text,
                        "longDescription": f"{title} is a Honkai Star Rail event of type {type_text}.",
                        "startTime": start_time,
                        "endTime": end_time,
                        "type": type_enum,
                        "imageUrl": image_url,
                        "detailUrl": None
                    }
                    events.append(event)
    except Exception as e:
        print(f"Failed to scrape HSR events: {e}")
        
    return events

def scrape_wuwa_events():
    headers = {'User-Agent': 'Gachalendar-Bot/2.0'}
    events = []
    
    # 1. Scrape Events Page
    try:
        print("Fetching Wuthering Waves events...")
        url = "https://wutheringwaves.fandom.com/api.php"
        params = {
            "action": "parse",
            "page": "Event",
            "format": "json",
            "prop": "text"
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for h in soup.find_all(['h2', 'h3']):
            span = h.find('span', class_='mw-headline')
            if span and span.text == 'Current':
                table = h.find_next_sibling('table', class_='article-table')
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all(['th', 'td'])
                        if len(cols) >= 3:
                            name_td = cols[0]
                            a_tags = name_td.find_all('a')
                            title = a_tags[-1].text.strip() if a_tags else name_td.text.strip()
                            
                            duration_text = cols[1].text.strip()
                            version_text = cols[2].text.strip()
                            
                            dates = re.findall(r'([A-Z][a-z]+ \d{1,2}, \d{4})', duration_text)
                            if len(dates) >= 2:
                                start_time = parse_date(dates[0])
                                end_time = parse_date(dates[1])
                            else:
                                continue
                                
                            type_enum = "IN_GAME_EVENT"
                                
                            image_url = None
                            img = name_td.find('img')
                            if img:
                                image_url = img.get('data-src') or img.get('src')
                                if image_url and image_url.startswith("data:image"):
                                    image_url = None
                                if image_url and '/revision/latest' in image_url:
                                    image_url = image_url.split('/revision/latest')[0] + '/revision/latest'
                                    
                            event = {
                                "id": f"wuwa_{uuid.uuid4().hex[:8]}",
                                "gameId": "wuwa",
                                "title": title,
                                "description": f"Version {version_text}",
                                "longDescription": f"{title} is a Wuthering Waves event in Version {version_text}.",
                                "startTime": start_time,
                                "endTime": end_time,
                                "type": type_enum,
                                "imageUrl": image_url,
                                "detailUrl": None
                            }
                            events.append(event)
    except Exception as e:
        print(f"Failed to scrape WuWa events: {e}")
        
    # 2. Scrape Convene Banners Page
    try:
        print("Fetching Wuthering Waves convenes...")
        url = "https://wutheringwaves.fandom.com/api.php"
        params = {
            "action": "parse",
            "page": "Featured_Resonator_Convene",
            "format": "json",
            "prop": "text"
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for h in soup.find_all(['h2', 'h3']):
            span = h.find('span', class_='mw-headline')
            if span and span.text == 'List of Featured Resonator Convenes':
                table = h.find_next_sibling('table')
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all(['th', 'td'])
                        # Format is typically Image, Name, Start, End, Version
                        if len(cols) >= 4:
                            name_td = cols[1]
                            a_tags = name_td.find_all('a')
                            title = a_tags[-1].text.strip() if a_tags else name_td.text.strip()
                            
                            start_text = cols[2].text.strip()
                            end_text = cols[3].text.strip()
                            
                            start_time = parse_date(start_text)
                            end_time = parse_date(end_text)
                            
                            if not start_time or not end_time:
                                continue
                                
                            image_url = None
                            img = cols[0].find('img')
                            if img:
                                image_url = img.get('data-src') or img.get('src')
                                if image_url and image_url.startswith("data:image"):
                                    image_url = None
                                if image_url and '/revision/latest' in image_url:
                                    image_url = image_url.split('/revision/latest')[0] + '/revision/latest'
                                    
                            event = {
                                "id": f"wuwa_{uuid.uuid4().hex[:8]}",
                                "gameId": "wuwa",
                                "title": title,
                                "description": "Resonator Convene",
                                "longDescription": f"{title} is a Wuthering Waves Resonator Convene (Banner).",
                                "startTime": start_time,
                                "endTime": end_time,
                                "type": "BANNER",
                                "imageUrl": image_url,
                                "detailUrl": None
                            }
                            events.append(event)
    except Exception as e:
        print(f"Failed to scrape WuWa convenes: {e}")
        
    return events

def main():
    print("Mulai mengambil data jadwal event dari internet...")
    genshin_events = scrape_genshin_events()
    print(f"Berhasil mendapatkan {len(genshin_events)} event Genshin Impact.")
    
    hsr_events = scrape_hsr_events()
    print(f"Berhasil mendapatkan {len(hsr_events)} event Honkai Star Rail.")
    
    wuwa_events = scrape_wuwa_events()
    print(f"Berhasil mendapatkan {len(wuwa_events)} event Wuthering Waves.")
    
    all_events = genshin_events + hsr_events + wuwa_events
    
    # Filter event yang sudah berakhir berdasarkan waktu Indonesia (WIB / UTC+7)
    indo_tz = timezone(timedelta(hours=7))
    now_indo = datetime.now(indo_tz).replace(tzinfo=None)
    
    active_events = []
    for event in all_events:
        if event.get("endTime"):
            try:
                # dt berbentuk datetime naif misal 2026-03-05 00:00:00
                dt = datetime.fromisoformat(event["endTime"])
                # Tambahkan toleransi 1 hari (karena end_date bisa jadi hari H sampai 23:59)
                end_time_plus_1 = dt + timedelta(days=1)
                if end_time_plus_1 < now_indo:
                    print(f"Skipping expired event: {event['title']} (Ended: {dt})")
                    continue
            except Exception as e:
                pass
        active_events.append(event)

    output_file = "events.json"
    with open(output_file, 'w') as f:
        json.dump(active_events, f, indent=4)
        
    print(f"Berhasil menyimpan {len(active_events)} event aktif ke dalam {output_file}")

if __name__ == "__main__":
    main()
