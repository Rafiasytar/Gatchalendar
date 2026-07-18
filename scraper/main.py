import json
from datetime import datetime, timedelta

def generate_events():
    now = datetime.now()
    
    events = [
        {
            "id": "gi_banner_1",
            "gameId": "gi",
            "title": "Character Banner: Venti & Neuvillette",
            "description": "Boosted drop rate for Venti and Neuvillette",
            "startTime": (now - timedelta(days=2)).isoformat(),
            "endTime": (now + timedelta(days=14)).isoformat(),
            "type": "BANNER"
        },
        {
            "id": "gi_event_1",
            "gameId": "gi",
            "title": "Lantern Rite Festival",
            "description": "Annual Liyue festival with minigames and rewards.",
            "startTime": (now + timedelta(days=1)).isoformat(),
            "endTime": (now + timedelta(days=20)).isoformat(),
            "type": "IN_GAME_EVENT"
        },
        {
            "id": "hsr_banner_1",
            "gameId": "hsr",
            "title": "Character Banner: Acheron",
            "description": "Boosted drop rate for Acheron",
            "startTime": (now - timedelta(days=5)).isoformat(),
            "endTime": (now + timedelta(days=10)).isoformat(),
            "type": "BANNER"
        },
        {
            "id": "wuwa_banner_1",
            "gameId": "wuwa",
            "title": "Resonator Convene: Yinlin",
            "description": "Featured resonator Yinlin",
            "startTime": (now + timedelta(days=3)).isoformat(),
            "endTime": (now + timedelta(days=24)).isoformat(),
            "type": "BANNER"
        }
    ]
    
    # In a real scenario, this script would use requests and BeautifulSoup/Playwright 
    # to scrape data from Fandom wikis or prydwen.gg, and then parse the dates.
    
    with open('events.json', 'w') as f:
        json.dump(events, f, indent=4)
        
    print("events.json has been generated successfully!")

if __name__ == "__main__":
    generate_events()
