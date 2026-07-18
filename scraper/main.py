import json
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import uuid

def parse_date(date_str):
    try:
        # Menghapus akhiran ordinal seperti st, nd, rd, th dari tanggal jika ada
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        dt = datetime.strptime(date_str, '%B %d, %Y')
        return dt.isoformat()
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        return datetime.now().isoformat()

def scrape_genshin_events():
    url = "https://genshin-impact.fandom.com/api.php"
    params = {
        "action": "parse",
        "page": "Event",
        "format": "json",
        "prop": "text"
    }
    headers = {'User-Agent': 'Gachalendar-Bot/1.0'}
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
                        
                        # Cari dua format tanggal: "Month DD, YYYY"
                        dates = re.findall(r'([A-Z][a-z]+ \d{2}, \d{4})', duration_text)
                        if len(dates) >= 2:
                            start_time = parse_date(dates[0])
                            end_time = parse_date(dates[1])
                        else:
                            continue # Skip jika format tanggal tidak dikenali
                            
                        # Tentukan tipe event
                        type_enum = "IN_GAME_EVENT"
                        if "Banner" in event_type_text or "Character Selection" in event_type_text:
                            type_enum = "BANNER"
                            
                        # Cari URL Gambar dan Detail
                        image_url = None
                        detail_url = None
                        img_tag = cols[0].find('img')
                        if img_tag:
                            image_url = img_tag.get('src') or img_tag.get('data-src')
                            # Membersihkan URL gambar agar ukurannya asli (bukan thumbnail)
                            if image_url and '/revision/latest' in image_url:
                                image_url = image_url.split('/revision/latest')[0] + '/revision/latest'
                                
                        a_tag = cols[0].find('a')
                        if a_tag and a_tag.get('href'):
                            detail_url = "https://genshin-impact.fandom.com" + a_tag.get('href')
                            
                        event = {
                            "id": f"gi_{uuid.uuid4().hex[:8]}",
                            "gameId": "gi",
                            "title": name,
                            "description": event_type_text,
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
    # Fungsi ini untuk game lain yang belum memiliki scraper real-time (sebagai contoh)
    now = datetime.now()
    return [
        {
            "id": f"hsr_{uuid.uuid4().hex[:8]}",
            "gameId": "hsr",
            "title": "Character Banner: Acheron (Dummy)",
            "description": "Boosted drop rate for Acheron",
            "startTime": now.isoformat(),
            "endTime": now.isoformat(),
            "type": "BANNER",
            "imageUrl": None,
            "detailUrl": None
        },
        {
            "id": f"wuwa_{uuid.uuid4().hex[:8]}",
            "gameId": "wuwa",
            "title": "Resonator Convene: Yinlin (Dummy)",
            "description": "Featured resonator Yinlin",
            "startTime": now.isoformat(),
            "endTime": now.isoformat(),
            "type": "BANNER",
            "imageUrl": None,
            "detailUrl": None
        }
    ]

def main():
    print("Mulai mengambil data jadwal event dari internet...")
    
    # 1. Scrape Genshin Impact (Real-time)
    genshin_events = scrape_genshin_events()
    print(f"Berhasil mendapatkan {len(genshin_events)} event Genshin Impact.")
    
    # 2. Ambil dummy data untuk HSR & WuWa sementara waktu
    other_events = get_dummy_events()
    
    # Gabungkan semua event
    all_events = genshin_events + other_events

    # Simpan ke dalam file events.json
    output_file = "events.json"
    with open(output_file, 'w') as f:
        json.dump(all_events, f, indent=4)
        
    print(f"Berhasil menyimpan {len(all_events)} event ke dalam {output_file}")

if __name__ == "__main__":
    main()
