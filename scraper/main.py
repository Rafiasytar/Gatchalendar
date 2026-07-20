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

def scrape_zzz_events():
    headers = {'User-Agent': 'Gachalendar-Bot/2.0'}
    events = []
    
    # 1. Scrape Events Page
    try:
        print("Fetching ZZZ events...")
        url = "https://zenless-zone-zero.fandom.com/api.php"
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
                table = h.find_next_sibling('table')
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all(['th', 'td'])
                        if len(cols) >= 3:
                            name_td = cols[0]
                            a_tags = name_td.find_all('a')
                            title = a_tags[-1].text.strip() if a_tags else name_td.text.strip()
                            
                            duration_text = cols[1].text.strip()
                            
                            # Matches "June 17, 2026", "TBA"
                            dates = re.findall(r'([A-Z][a-z]+ \d{1,2}, \d{4}|TBA)', duration_text)
                            start_time, end_time = None, None
                            if len(dates) >= 1:
                                start_time = parse_date(dates[0]) if dates[0] != "TBA" else None
                            if len(dates) >= 2:
                                end_time = parse_date(dates[1]) if dates[1] != "TBA" else None
                            
                            if not start_time or not end_time:
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
                                "id": f"zzz_{uuid.uuid4().hex[:8]}",
                                "gameId": "zzz",
                                "title": title,
                                "description": "Zenless Zone Zero Event",
                                "longDescription": f"{title} is a Zenless Zone Zero event.",
                                "startTime": start_time,
                                "endTime": end_time,
                                "type": type_enum,
                                "imageUrl": image_url,
                                "detailUrl": None
                            }
                            events.append(event)
    except Exception as e:
        print(f"Failed to scrape ZZZ events: {e}")
        
    # 2. Scrape Exclusive Channels
    try:
        print("Fetching ZZZ banners...")
        url = "https://zenless-zone-zero.fandom.com/api.php"
        params = {
            "action": "parse",
            "page": "Exclusive_Channel",
            "format": "json",
            "prop": "text"
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for h in soup.find_all(['h2', 'h3']):
            span = h.find('span', class_='mw-headline')
            if span and 'Current' in span.text:
                for node in h.find_next_siblings():
                    if node.name in ['h2', 'h3']:
                        break
                    if node.name == 'div' and 'hatnote' in node.get('class', []):
                        a_tag = node.find('a')
                        if a_tag:
                            title_text = a_tag.text.strip()
                            if "/" in title_text:
                                title, start_date = title_text.split("/", 1)
                            else:
                                title = title_text
                                start_date = None
                            
                            start_time = None
                            if start_date:
                                try:
                                    start_time = datetime.strptime(start_date, "%Y-%m-%d").isoformat()
                                except:
                                    pass
                                    
                            next_node = node.find_next_sibling('div', class_='countdownevent')
                            end_time = None
                            if next_node:
                                asia_span = next_node.find('span', class_='countdowndate')
                                if asia_span:
                                    end_str = asia_span.text.strip()
                                    try:
                                        match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', end_str)
                                        if match:
                                            end_time = parse_date(match.group(1))
                                    except:
                                        pass
                                        
                            if not start_time or not end_time:
                                continue
                                        
                            image_url = None
                            try:
                                print(f"Fetching fallback image for ZZZ Banner: {title}")
                                url_query = "https://zenless-zone-zero.fandom.com/api.php"
                                params_query = {
                                    "action": "query",
                                    "prop": "pageimages",
                                    "titles": title,
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
                                pass
                                
                            event = {
                                "id": f"zzz_{uuid.uuid4().hex[:8]}",
                                "gameId": "zzz",
                                "title": title,
                                "description": "Exclusive Channel",
                                "longDescription": f"{title} is a Zenless Zone Zero Exclusive Channel (Banner).",
                                "startTime": start_time,
                                "endTime": end_time,
                                "type": "BANNER",
                                "imageUrl": image_url,
                                "detailUrl": None
                            }
                            events.append(event)
    except Exception as e:
        print(f"Failed to scrape ZZZ convenes: {e}")
        
    return events

def scrape_endfield_events():
    print("Fetching Arknights Endfield events...")
    events = [
        {
            "id": f"endfield_{uuid.uuid4().hex[:8]}",
            "gameId": "endfield",
            "title": "Version 1.4 Update: Homecoming",
            "description": "6-Month Anniversary",
            "longDescription": "Celebrate the six-month anniversary with the new 'Homecoming' update. Conclude the Wuling story arc and explore Yinglung Pass!",
            "startTime": "2026-07-16T12:00:00",
            "endTime": "2026-08-20T03:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/endfield/images/a/a9/Locations_Talos-II_Cinematic.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"endfield_{uuid.uuid4().hex[:8]}",
            "gameId": "endfield",
            "title": "HEAT RAGE! MEGA ARENA!",
            "description": "Challenge Event",
            "longDescription": "Test your combat tactics in the Mega Arena. Complete challenge stages to earn Oroberyl x1200 and a special portrait frame.",
            "startTime": "2026-07-30T12:00:00",
            "endTime": "2026-08-13T04:00:00",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/endfield/images/2/2a/Location_Jinlong.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"endfield_{uuid.uuid4().hex[:8]}",
            "gameId": "endfield",
            "title": "Blueprint Submission: Industrial Revolution",
            "description": "Community Event",
            "longDescription": "Share your AIC industrial complex layout blueprints with the community for a chance to win exclusive physical merchandise.",
            "startTime": "2026-07-17T12:00:00",
            "endTime": "2026-08-20T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/endfield/images/1/10/Bronzer_The_Hub.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"endfield_{uuid.uuid4().hex[:8]}",
            "gameId": "endfield",
            "title": "Headhunting Banner: Arcane & Liino",
            "description": "Rate-up Banner",
            "longDescription": "Increased drop rate for new 6-star Operators: Arcane (Nature Caster) and Liino (Electric Supporter).",
            "startTime": "2026-07-16T12:00:00",
            "endTime": "2026-07-30T03:59:59",
            "type": "BANNER",
            "imageUrl": "https://static.wikia.nocookie.net/endfield/images/4/40/AvywennaSplashart.png/revision/latest",
            "detailUrl": None
        }
    ]
    return events

def scrape_nte_events():
    print("Fetching Neverness to Everness events...")
    events = [
        # === Banners (Rate Up) ===
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Shinku Perks (Before the Dawn)",
            "description": "Character Banner",
            "longDescription": "Rate up banner for the new 5-star Cosmos Esper, Shinku! Play her trial stage and unlock her signature weapon.",
            "startTime": "2026-07-08T12:00:00",
            "endTime": "2026-07-29T23:59:59",
            "type": "BANNER",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/2/23/Shinku_-_Board.jpg/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Iroi Perks (The Lifeline)",
            "description": "Character Banner",
            "longDescription": "Rate up banner for the new 5-star Sunward Island Esper, Iroi! Deploy her on the battlefield alongside her loyal companions.",
            "startTime": "2026-07-29T12:00:00",
            "endTime": "2026-08-19T23:59:59",
            "type": "BANNER",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/5/55/Iroi_Introduction.png/revision/latest",
            "detailUrl": None
        },
        # === Limited Time Events ===
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "999 Nights Tabletop Mode",
            "description": "Version 1.2 Main Event",
            "longDescription": "Explore the supernatural urban city in a new tabletop board game mode. Gather tokens to redeem exclusive rewards, dye, and upgrade items.",
            "startTime": "2026-07-08T12:00:00",
            "endTime": "2026-08-19T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/d/dc/ETD6_999_Nights.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Stamina Recharge Event",
            "description": "Limited Resource Buff",
            "longDescription": "Get double reward drops from select Anomaly Hunts and simulation challenges daily up to 3 times.",
            "startTime": "2026-07-13T04:00:00",
            "endTime": "2026-07-20T03:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/c/cb/Version_1.2_Event_Calendar_Wallpaper_%28Desktop%29.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Beyond the Rails (Blazing Circle)",
            "description": "Limited Time Event",
            "longDescription": "Challenge special city tracks using your customizable vehicles. Beat the target time to earn Annulith and car dyes.",
            "startTime": "2026-07-16T12:00:00",
            "endTime": "2026-07-30T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/1/15/Version_1.2_Event_Calendar_Wallpaper_%28Mobile%29.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Gold Clash Challenge",
            "description": "Limited Time Event",
            "longDescription": "Fight waves of enemies within a time limit. Earn high scores to unlock rewards including Annulith and leveling guides.",
            "startTime": "2026-07-20T12:00:00",
            "endTime": "2026-08-03T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/f/f1/Version_1.2_Preview_Special_Program_Premiere_Announcement.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Shadow-n-Seek",
            "description": "Asymmetric PvP Event",
            "longDescription": "Participate in hide and seek matches in the neon city. Hunter and Hider roles earn special event currency for the exchange shop.",
            "startTime": "2026-07-25T12:00:00",
            "endTime": "2026-08-08T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/b/b5/MP_-_Shinku.jpg/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Fishing Frenzy Tournament",
            "description": "Limited Time Event",
            "longDescription": "Catch rare Anomalous fish in Hethereau's waters. Place trophies in your garage or trade them for premium items.",
            "startTime": "2026-08-03T12:00:00",
            "endTime": "2026-08-19T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/3/38/Iroi.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Pixel Surge Mini-game",
            "description": "Retro Arcade Event",
            "longDescription": "Play classic arcade cabinets at Eibon antique shop and complete daily high score challenges.",
            "startTime": "2026-08-03T12:00:00",
            "endTime": "2026-08-10T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/5/5a/Shinku_Dawn_Patrol_Portrait.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Warren Lucky Flip",
            "description": "Card Flip Event",
            "longDescription": "Spend event tickets to flip cards and match matching pairs. Jackpot board rewards character and vehicle cosmetics.",
            "startTime": "2026-08-05T12:00:00",
            "endTime": "2026-08-19T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/2/20/999_Nights_-_Shinku.jpg/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Fons Rush Event",
            "description": "Double Drops Event",
            "longDescription": "Claim double rewards from Leyline-style Fons extractors for 7 days.",
            "startTime": "2026-08-10T04:00:00",
            "endTime": "2026-08-17T03:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/c/cb/Version_1.2_Event_Calendar_Wallpaper_%28Desktop%29.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Going, Going, Gone Auction",
            "description": "Auction Event",
            "longDescription": "Bid on antique relics and oddities with other anomaly hunters to win exclusive home furniture blueprints.",
            "startTime": "2026-08-12T12:00:00",
            "endTime": "2026-08-26T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/f/f1/Version_1.2_Preview_Special_Program_Premiere_Announcement.png/revision/latest",
            "detailUrl": None
        },
        # === Endgame Content ===
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Anomaly Hunt: Weekly Boss Challenge",
            "description": "Weekly Reset Endgame",
            "longDescription": "Defeat Level 5+ Anomaly bosses to earn high-tier upgrading materials and currency. Adjust your team element composition to exploit weekly boss weaknesses.",
            "startTime": "2026-07-13T04:00:00",
            "endTime": "2026-07-20T03:59:59",
            "type": "ENDGAME",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/d/d8/Anomaly_Sighting_Records_-_Sighting_1.2.jpg/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Anomaly Hunt: Weekly Boss Challenge (Upcoming)",
            "description": "Weekly Reset Endgame",
            "longDescription": "Defeat Level 5+ Anomaly bosses to earn high-tier upgrading materials and currency.",
            "startTime": "2026-07-20T04:00:00",
            "endTime": "2026-07-27T03:59:59",
            "type": "ENDGAME",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/d/d8/Anomaly_Sighting_Records_-_Sighting_1.2.jpg/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Dreamwalk Corridor: Season 1",
            "description": "Bi-weekly Abyss Reset",
            "longDescription": "Conquer deep dreams in the Corridor to earn Annulith and character ascension resources. Floors reset bi-weekly with varying elemental buffs.",
            "startTime": "2026-07-15T04:00:00",
            "endTime": "2026-07-29T03:59:59",
            "type": "ENDGAME",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/3/39/Iroi_-_Dreamwalk.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"nte_{uuid.uuid4().hex[:8]}",
            "gameId": "nte",
            "title": "Dreamwalk Corridor: Season 2",
            "description": "Bi-weekly Abyss Reset",
            "longDescription": "Floors reset bi-weekly with varying elemental buffs. Conquer deep dreams in the Corridor to earn Annulith.",
            "startTime": "2026-07-29T04:00:00",
            "endTime": "2026-08-12T03:59:59",
            "type": "ENDGAME",
            "imageUrl": "https://static.wikia.nocookie.net/neverness-to-everness/images/3/39/Iroi_-_Dreamwalk.png/revision/latest",
            "detailUrl": None
        }
    ]
    return events

def scrape_p5x_events():
    print("Fetching Persona 5: The Phantom X events (SEA Server)...")
    events = [
        {
            "id": f"p5x_{uuid.uuid4().hex[:8]}",
            "gameId": "p5x",
            "title": "Haunted Beach Shack: The Curse of Shirosato Beach",
            "description": "Version 4.5 Event",
            "longDescription": "Explore Shirosato Beach and complete event missions for exclusive summer rewards.",
            "startTime": "2026-07-16T12:00:00",
            "endTime": "2026-07-30T03:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/megamitensei/images/7/7f/P5X_Minami_Miyashita_Marian_Summer_Background.png/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"p5x_{uuid.uuid4().hex[:8]}",
            "gameId": "p5x",
            "title": "Character Banner: Beachflower Minami",
            "description": "Featured Phantom Thief",
            "longDescription": "Boosted drop rate for 5-star Phantom Thief 'Beachflower Minami' in the limited summer banner.",
            "startTime": "2026-07-16T12:00:00",
            "endTime": "2026-07-30T03:59:59",
            "type": "BANNER",
            "imageUrl": "https://static.wikia.nocookie.net/megamitensei/images/7/75/P5X_Minami_Summer_wallpaper.jpeg/revision/latest",
            "detailUrl": None
        },
        {
            "id": f"p5x_{uuid.uuid4().hex[:8]}",
            "gameId": "p5x",
            "title": "1st Anniversary Party",
            "description": "Anniversary Event",
            "longDescription": "Collect Wish Candy and Scratch-Off Packs to earn a 5☆ Thief Select Ticket and other anniversary rewards.",
            "startTime": "2026-06-26T12:00:00",
            "endTime": "2026-07-26T23:59:59",
            "type": "IN_GAME_EVENT",
            "imageUrl": "https://static.wikia.nocookie.net/megamitensei/images/a/a2/P5X_Wallpaper_3.jpeg/revision/latest",
            "detailUrl": None
        }
    ]
    return events

def main():
    print("Mulai mengambil data jadwal event dari internet...")
    genshin_events = scrape_genshin_events()
    print(f"Berhasil mendapatkan {len(genshin_events)} event Genshin Impact.")
    
    hsr_events = scrape_hsr_events()
    print(f"Berhasil mendapatkan {len(hsr_events)} event Honkai Star Rail.")
    
    wuwa_events = scrape_wuwa_events()
    print(f"Berhasil mendapatkan {len(wuwa_events)} event Wuthering Waves.")
    
    zzz_events = scrape_zzz_events()
    print(f"Berhasil mendapatkan {len(zzz_events)} event Zenless Zone Zero.")
    
    endfield_events = scrape_endfield_events()
    print(f"Berhasil mendapatkan {len(endfield_events)} event Arknights Endfield.")
    
    nte_events = scrape_nte_events()
    print(f"Berhasil mendapatkan {len(nte_events)} event Neverness to Everness.")
    
    p5x_events = scrape_p5x_events()
    print(f"Berhasil mendapatkan {len(p5x_events)} event Persona 5: The Phantom X.")
    
    all_events = genshin_events + hsr_events + wuwa_events + zzz_events + endfield_events + nte_events + p5x_events
    
    # Filter event yang sudah berakhir berdasarkan waktu Indonesia (WIB / UTC+7)
    indo_tz = timezone(timedelta(hours=7))
    now_indo = datetime.now(indo_tz).replace(tzinfo=None)
    
    active_events = []
    for event in all_events:
        # Classify Event Type based on title keywords
        title_lower = event.get("title", "").lower()
        if any(kw in title_lower for kw in ["abyss", "theatre", "theater", "shiyu defense", "memory of chaos", "pure fiction", "apocalyptic shadow", "tower of adversity", "divergent universe", "simulated universe", "anomaly hunt", "dreamwalk corridor"]):
            event["type"] = "ENDGAME"
        elif any(kw in title_lower for kw in ["banner", "convene", "headhunting", "gaze north to the rift hh permit"]):
            event["type"] = "BANNER"

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
