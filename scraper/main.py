"""
Gachalendar scraper.

Mengambil jadwal event & banner yang BENAR-BENAR berjalan (dan yang akan datang)
untuk setiap game, lalu menyimpannya ke events.json.

Sumber data (diurutkan dari yang paling akurat):
  - Genshin Impact, Honkai: Star Rail, Zenless Zone Zero
        -> API pengumuman resmi in-game HoYoverse (server Asia, UTC+8)
  - Arknights: Endfield -> endfield.wiki.gg (timer server Asia, UTC)
  - Wuthering Waves      -> Game8 (event) + Fandom "Featured Resonator Convene" (banner)
  - Neverness to Everness, Persona 5: The Phantom X -> Game8 (tanggal server Asia/SEA)

Semua waktu ditulis dalam ISO-8601 DENGAN offset (mis. 2026-11-04T11:00:00+08:00)
sehingga aplikasi bisa mengonversinya ke zona waktu perangkat.
"""
import hashlib
import html as htmllib
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

TZ8 = timezone(timedelta(hours=8))  # Server Asia / SEA
NOW = datetime.now(timezone.utc)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; GachalendarBot/3.0)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "events.json")

# Event yang lebih lama dari ini di riwayat akan dibuang
HISTORY_DAYS = 365
# Pengumuman yang durasinya lebih dari ini dianggap permanen (bukan event)
MAX_EVENT_DAYS = 150

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}


# ---------------------------------------------------------------------------
# Helper umum
# ---------------------------------------------------------------------------

def http_get(url, params=None, retries=3, timeout=30):
    last = None
    for attempt in range(retries):
        try:
            r = SESSION.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last


def iso(dt):
    return dt.astimezone(TZ8).isoformat(timespec="seconds")


def clean_text(s):
    s = htmllib.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


def norm_title(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def make_id(game_id, title, start):
    key = f"{game_id}|{norm_title(title)}|{start.astimezone(TZ8).date().isoformat()}"
    return f"{game_id}-{hashlib.sha1(key.encode()).hexdigest()[:12]}"


ENDGAME_KW = ["spiral abyss", "imaginarium theater", "stygian onslaught", "memory of chaos", "pure fiction",
              "apocalyptic shadow", "shiyu defense", "deadly assault", "tower of adversity",
              "whimpering wastes", "anomaly arbitration", "threshold of"]
BANNER_KW = ["event wish", "wish ", "warp", "signal search", "channel", "convene", "headhunting", "banner",
             "contract", "issue"]


def classify(title, default="IN_GAME_EVENT"):
    t = title.lower()
    if any(k in t for k in ENDGAME_KW):
        return "ENDGAME"
    if default == "BANNER" or any(k in t for k in BANNER_KW):
        return "BANNER"
    return default


def make_event(game_id, title, start, end, type_, description="", image=None, detail=None, long_desc=None):
    title = re.sub(r"\s+", " ", title).strip()
    return {
        "id": make_id(game_id, title, start),
        "gameId": game_id,
        "title": title,
        "description": description or "",
        "longDescription": long_desc,
        "startTime": iso(start),
        "endTime": iso(end),
        "type": type_,
        "imageUrl": image,
        "detailUrl": detail,
    }


def parse_month_date(text):
    """'Oct. 14, 2026' / 'October 14, 2026' / 'Sept 4, 2026' -> date atau None."""
    m = re.search(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", text or "")
    if not m:
        return None
    mon = MONTHS.get(m.group(1)[:3].lower())
    if not mon:
        return None
    try:
        return datetime(int(m.group(3)), mon, int(m.group(2))).date()
    except ValueError:
        return None


def day_start(d):
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=TZ8)


def day_end(d):
    return datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=TZ8)


# ---------------------------------------------------------------------------
# HoYoverse: Genshin Impact, Honkai: Star Rail, Zenless Zone Zero
# ---------------------------------------------------------------------------

HOYO_GAMES = {
    "gi": {
        "name": "Genshin Impact",
        "base": "https://sg-hk4e-api.hoyoverse.com/common/hk4e_global/announcement/api/",
        "query": {"game": "hk4e", "game_biz": "hk4e_global", "lang": "en", "bundle_id": "hk4e_global",
                  "platform": "pc", "region": "os_asia", "level": "55", "uid": "100000000"},
    },
    "hsr": {
        "name": "Honkai: Star Rail",
        "base": "https://sg-hkrpg-api.hoyoverse.com/common/hkrpg_global/announcement/api/",
        "query": {"game": "hkrpg", "game_biz": "hkrpg_global", "lang": "en", "bundle_id": "hkrpg_global",
                  "platform": "pc", "region": "prod_official_asia", "level": "70", "uid": "100000000",
                  "channel_id": "1"},
    },
    "zzz": {
        "name": "Zenless Zone Zero",
        "base": "https://sg-announcement-static.hoyoverse.com/common/nap_global/announcement/api/",
        "query": {"game": "nap", "game_biz": "nap_global", "lang": "en", "bundle_id": "nap_global",
                  "platform": "pc", "region": "prod_gf_jp", "level": "60", "uid": "1300000000",
                  "channel_id": "1"},
    },
}

VERSION_DAYS = 42  # Siklus patch HoYoverse: 6 minggu

HOYO_SKIP = re.compile(
    r"fair use|fair gaming|survey|top-up|community|social media|phishing|known issues|optimization|"
    r"compatib|faq|gameplay rules|invitation to join|trailer|highlights page|maintenance|update details|"
    r"now available|what's new|new content overview|store update|new stock|check-in|new stages?\b|"
    r"mission description|^version \d+\.\d+ update$|preview|livestream|creator contest|wonderland treasures",
    re.I)

DATE_NUM = r"(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?"
DATE_WORD = r"([A-Z][a-z]+ \d{1,2}, \d{4}),?\s+(\d{1,2}):(\d{2})(?::(\d{2}))?"
DURATION_KEY = re.compile(
    r"(Event Wish Duration|Wish Duration|Event Duration|Season Duration|Specified Duration|Event Period|"
    r"Warp period|Signal Search Event period|Discount Period|Collection Time|Duration|Period)", re.I)


def hoyo_plain(content):
    # Pertahankan isi tag <t> (waktu), buang tag lain
    # Beberapa game mengirim tag <t> dalam bentuk ter-escape (&lt;t&gt;), jadi unescape dulu
    text = htmllib.unescape(htmllib.unescape(content or ""))
    return clean_text(re.sub(r"</?t\b[^>]*>", " ", text))


def find_dates(text):
    """Kembalikan list (posisi, datetime UTC+8) yang muncul di text, terurut."""
    found = []
    for m in re.finditer(DATE_NUM, text):
        y, mo, d, h, mi, s = m.groups()
        try:
            found.append((m.start(), datetime(int(y), int(mo), int(d), int(h), int(mi), int(s or 0), tzinfo=TZ8)))
        except ValueError:
            pass
    for m in re.finditer(DATE_WORD, text):
        d = parse_month_date(m.group(1))
        if d:
            found.append((m.start(), datetime(d.year, d.month, d.day, int(m.group(2)), int(m.group(3)),
                                              int(m.group(4) or 0), tzinfo=TZ8)))
    return sorted(found, key=lambda x: x[0])


def parse_list_time(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ8)
    except Exception:  # noqa: BLE001
        return None


def hoyo_fetch(cfg):
    """
    Ambil daftar pengumuman + kontennya.
    Catatan: CDN HoYoverse kadang mengembalikan start_time/end_time dalam zona waktu server lain
    (UTC-5 / UTC+1) walaupun field timezone=8. Karena UTC+8 adalah zona paling timur, kita ambil
    beberapa kali dan pakai nilai jam TERBESAR. Konten pengumuman (sumber utama) tidak terpengaruh.
    """
    items = {}
    for i in range(4):
        q = dict(cfg["query"], t=str(int(time.time() * 1000) + i))
        data = http_get(cfg["base"] + "getAnnList", params=q).json().get("data") or {}
        groups = (data.get("list") or []) + (data.get("pic_list") or [])
        stack = list(groups)
        while stack:
            g = stack.pop()
            stack.extend(g.get("type_list") or [])
            for a in g.get("list") or []:
                aid = a.get("ann_id")
                st, en = parse_list_time(a.get("start_time")), parse_list_time(a.get("end_time"))
                if aid not in items:
                    items[aid] = dict(a, _st=st, _en=en)
                else:
                    prev = items[aid]
                    if st and (prev["_st"] is None or st > prev["_st"]):
                        prev["_st"] = st
                    if en and (prev["_en"] is None or en > prev["_en"]):
                        prev["_en"] = en
        time.sleep(0.3)

    content = http_get(cfg["base"] + "getAnnContent", params=cfg["query"]).json().get("data") or {}
    contents = {c["ann_id"]: c for c in (content.get("list") or []) + (content.get("pic_list") or [])}
    return items, contents


def next_wednesday_11(dt):
    dt = dt.astimezone(TZ8)
    days = (2 - dt.weekday()) % 7  # 2 = Rabu (patch HoYoverse selalu Rabu)
    d = (dt + timedelta(days=days)).date()
    return datetime(d.year, d.month, d.day, 11, 0, tzinfo=TZ8)


MAINT_CTX = re.compile(r"(maintenance on|maintenance will begin(?: at| on)?|begins? at|or above by|before)$", re.I)


def hoyo_version_starts(items, contents):
    """Petakan 'X.Y' -> waktu game tersedia setelah maintenance update versi tsb (UTC+8)."""
    explicit, fallback = {}, {}
    for aid, c in contents.items():
        title = clean_text(c.get("title", "")) + " " + clean_text((items.get(aid) or {}).get("subtitle", ""))
        mv = re.search(r"Version (\d+\.\d+)", title)
        if not mv or not re.search(r"update|maintenance|now available", title, re.I):
            continue
        ver = mv.group(1)
        text = hoyo_plain(c.get("content"))
        # Maintenance update HoYoverse dimulai 06:00 UTC+8 dan berlangsung ~5 jam.
        # Hanya tanggal yang jelas merujuk ke maintenance (bukan "until <tanggal>").
        for pos, d in find_dates(text):
            ctx = text[max(0, pos - 70):pos].strip()
            if (d.hour, d.minute) == (6, 0) and MAINT_CTX.search(ctx):
                cand = d + timedelta(hours=5)
                if ver not in explicit or cand < explicit[ver]:
                    explicit[ver] = cand
        st = (items.get(aid) or {}).get("_st")
        if st:
            cand = next_wednesday_11(st)
            if ver not in fallback or cand > fallback[ver]:
                fallback[ver] = cand
    anchors = dict(fallback)
    anchors.update(explicit)
    return anchors


def version_start(anchors, ver):
    if ver in anchors:
        return anchors[ver]
    major, minor = ver.split(".")
    same = [(int(v.split(".")[1]), d) for v, d in anchors.items() if v.split(".")[0] == major]
    if same:
        m, d = min(same, key=lambda x: abs(x[0] - int(minor)))
        return d + timedelta(days=VERSION_DAYS * (int(minor) - m))
    return None


def version_end(anchors, ver):
    major, minor = ver.split(".")
    nxt = anchors.get(f"{major}.{int(minor) + 1}")
    if nxt:
        # Versi berakhir saat maintenance versi berikutnya dimulai (06:00)
        return nxt - timedelta(hours=5, seconds=1)
    st = version_start(anchors, ver)
    return st + timedelta(days=VERSION_DAYS) - timedelta(hours=5, seconds=1) if st else None


def hoyo_short_title(raw_title, subtitle):
    t = clean_text(subtitle) or clean_text(raw_title)
    if len(t) < 4:
        t = clean_text(raw_title)
    m = re.match(r'^"([^"]+)"\s*(?:[:\-–]|Event|Outfit|$)', t)
    if m and not t.lower().startswith('"event wish'):
        t = m.group(1)
    t = re.sub(r"\s*(Event Details|Details|Event)$", "", t).strip()
    t = re.sub(r"^Genius Invokation TCG\s*-\s*", "GI TCG: ", t)
    t = re.sub(r'^Event Wish\s*(?:-\s*)?"?([^"]+?)"?$', r"Event Wish: \1", t)
    if t.startswith('"') and t.endswith('"'):
        t = t[1:-1]
    return t.strip()


def hoyo_featured(game_id, text):
    pats = {
        "gi": [r'event-exclusive 5-star character "[^"]+" ([^()]+?) \(',
               r'event-exclusive 5-star weapons? ([^.]+?) will'],
        "hsr": [r'limited 5-star character ([^()]+?) \(', r'limited 5-star Light Cone "([^"]+)"'],
        "zzz": [r'limited S-Rank Agent ([^()]+?) \(', r'limited S-Rank W-Engine ([^()]+?) \('],
    }[game_id]
    names = []
    for p in pats:
        for m in re.finditer(p, text):
            n = m.group(1).strip()
            if n not in names:
                names.append(n)
    return names[:4]


def hoyo_dates(text, item, anchors):
    """Tentukan (start, end) dari teks pengumuman resmi."""
    km = DURATION_KEY.search(text)
    seg = text[km.start(): km.start() + 420] if km else text[:400]
    dates = find_dates(seg)
    after = re.search(r"after (?:the )?Version (\d+\.\d+) [Uu]pdate", seg, re.I)
    during = re.search(r"(?:throughout(?: the entirety of)?|during|until the end of)(?: the)? Version (\d+\.\d+)",
                       seg, re.I)
    start = end = None
    if after and (not dates or after.start() < dates[0][0]):
        start = version_start(anchors, after.group(1))
        later = [d for p, d in dates if p > after.start()]
        if later:
            # Event multi-fase (mis. "Preparation Phase ... Play Phase ...") -> pakai akhir fase terakhir
            end = later[-1] if re.search(r"\bPhase\b", seg) else later[0]
        elif during:
            end = version_end(anchors, during.group(1))
    elif len(dates) >= 2:
        start, end = dates[0][1], dates[1][1]
    elif during:
        start, end = version_start(anchors, during.group(1)), version_end(anchors, during.group(1))
    elif len(dates) == 1:
        end = dates[0][1]

    if start is None:
        start = item.get("_st")
    if end is None:
        end = item.get("_en")
    return start, end, seg


def scrape_hoyo(game_id):
    cfg = HOYO_GAMES[game_id]
    print(f"Fetching {cfg['name']} (official announcements)...")
    items, contents = hoyo_fetch(cfg)
    anchors = hoyo_version_starts(items, contents)
    print(f"  version anchors: { {k: iso(v) for k, v in anchors.items()} }")

    events = []
    for aid, item in items.items():
        c = contents.get(aid, {})
        raw_title = clean_text(c.get("title") or item.get("title"))
        subtitle = item.get("subtitle") or c.get("subtitle") or ""
        title = hoyo_short_title(raw_title, subtitle)
        if not title or HOYO_SKIP.search(title) or HOYO_SKIP.search(raw_title):
            continue
        text = hoyo_plain(c.get("content"))
        if re.search(r"Event Duration\s*〓?\s*Permanent|available long-term|Permanently available", text, re.I):
            continue

        start, end, seg = hoyo_dates(text, item, anchors)
        if not start or not end or end <= start:
            continue
        if (end - start).days > MAX_EVENT_DAYS:
            continue

        lower = (raw_title + " " + title).lower()
        is_banner = bool(re.search(r"event wish|epitome invocation|chronicled wish|event warp|collaboration warp|"
                                   r"limited-time channels|signal search", lower))
        type_ = "BANNER" if is_banner else classify(title)

        description = raw_title if raw_title != title else ""
        if is_banner:
            feat = hoyo_featured(game_id, text)
            if feat:
                description = "Featured: " + ", ".join(feat)

        long_desc = re.sub(r"^[〓■◇●\s]+", "", text)[:600] or None
        image = item.get("banner") or item.get("img") or c.get("banner") or None
        if not image:
            m = re.search(r'<img[^>]+src="([^"]+)"', c.get("content") or "")
            image = m.group(1) if m else None

        events.append(make_event(game_id, title, start, end, type_, description, image, None, long_desc))
    return events


# ---------------------------------------------------------------------------
# Arknights: Endfield (endfield.wiki.gg) - timer server Asia
# ---------------------------------------------------------------------------

def scrape_endfield_events():
    print("Fetching Arknights: Endfield (endfield.wiki.gg)...")
    api = "https://endfield.wiki.gg/api.php"
    events = []
    seen = set()

    def parse_page(page):
        data = http_get(api, params={"action": "parse", "page": page, "format": "json", "prop": "text",
                                     "redirects": 1}).json()
        return BeautifulSoup(data["parse"]["text"]["*"], "html.parser")

    def timer_of(block):
        # Ambil timer server Asia (biasanya yang pertama); fallback ke timer pertama apapun
        timers = block.select("[data-start][data-end]")
        if not timers:
            return None, None
        pick = next((t for t in timers if "asia" in t.get_text(" ").lower()), timers[0])
        try:
            st = datetime.fromisoformat(pick["data-start"])
            en = datetime.fromisoformat(pick["data-end"])
            return st, en
        except ValueError:
            return None, None

    def image_of(block):
        img = block.find("img")
        if not img:
            return None
        src = img.get("src") or ""
        if src.startswith("/"):
            src = "https://endfield.wiki.gg" + src
        return src.split("?")[0] or None

    def link_of(block):
        a = block.find("a", href=True)
        if a and a["href"].startswith("/wiki/"):
            return "https://endfield.wiki.gg" + a["href"]
        return None

    pages = []
    for p in ("Main Page", "Event"):
        try:
            pages.append(parse_page(p))
        except Exception as e:  # noqa: BLE001
            print(f"  Failed to load Endfield page {p}: {e}")

    for soup in pages:
        for b in soup.select(".mp-banner"):
            h = b.select_one(".mp-banner-header")
            title = h.get_text(" ", strip=True) if h else None
            st, en = timer_of(b)
            if not title or not st or (title, st) in seen:
                continue
            seen.add((title, st))
            is_weapon = title.lower().endswith("issue")
            events.append(make_event(
                "endfield", title, st, en, "BANNER",
                "Weapon Issue" if is_weapon else "Headhunting",
                image_of(b), link_of(b),
                f"{title} - {'Arsenal Issue (weapon banner)' if is_weapon else 'Headhunting (operator banner)'}."))
        for b in soup.select(".mp-event"):
            n = b.select_one(".mp-event-name")
            title = n.get_text(" ", strip=True) if n else None
            t = b.select_one(".mp-event-type")
            etype = t.get_text(" ", strip=True) if t else ""
            st, en = timer_of(b)
            if not title or not st or (title, st) in seen:
                continue
            seen.add((title, st))
            type_ = "ENDGAME" if "challenge" in etype.lower() and "contingency" in title.lower() else classify(title)
            events.append(make_event("endfield", title, st, en, type_, etype, image_of(b), link_of(b),
                                     f"{title} ({etype})." if etype else None))
    return events


# ---------------------------------------------------------------------------
# Game8 helpers (NTE, P5X, WuWa)
# ---------------------------------------------------------------------------

_G8_CACHE = {}


def game8_article_dates(url):
    """
    Baca halaman artikel Game8 dan ambil Start/End date.
    Mengutamakan tanggal server Asia/SEA/GMT+8 jika tersedia.
    """
    if not url:
        return None, None
    if url.startswith("/"):
        url = "https://game8.co" + url
    if url in _G8_CACHE:
        return _G8_CACHE[url]
    try:
        text = clean_text(BeautifulSoup(http_get(url).text, "html.parser").get_text(" "))
        time.sleep(0.4)
    except Exception as e:  # noqa: BLE001
        print(f"  Game8 article failed {url}: {e}")
        _G8_CACHE[url] = (None, None)
        return None, None

    def pick(label):
        m = re.search(label + r"\s*:?\s*(.{0,160})", text)
        if not m:
            return None
        chunk = m.group(1)
        # Potong sebelum label berikutnya
        chunk = re.split(r"End Date|Start Date|Countdown", chunk)[0] if label.startswith("Start") else chunk
        # Cari tanggal yang ditandai Asia/SEA/GMT+8
        for dm in re.finditer(r"([A-Za-z]{3,9}\.? \d{1,2},? \d{4})\s*\(([^)]*)\)", chunk):
            if re.search(r"Asia|SEA|GMT\+8|UTC\+8", dm.group(2)):
                return parse_month_date(dm.group(1))
        return parse_month_date(chunk)

    st = pick(r"Start(?: Date)?")
    en = pick(r"End(?: Date)?")
    if not st or not en:
        # Pola alternatif: "October 21, 2026 – November 11, 2026" atau "10/21/2026 - 11/11/2026"
        m = re.search(r"([A-Z][a-z]{2,8}\.? \d{1,2},? \d{4})\s*[-–~to]+\s*([A-Z][a-z]{2,8}\.? \d{1,2},? \d{4})", text)
        if m:
            st, en = st or parse_month_date(m.group(1)), en or parse_month_date(m.group(2))
    if st and en and en < st:
        st, en = None, None
    _G8_CACHE[url] = (st, en)
    return st, en


def game8_sections(page_html, headings):
    """Kembalikan {heading: [(title, href, img, date_text)]} dari tabel di bawah heading h3/h4."""
    soup = BeautifulSoup(page_html, "html.parser")
    result = {}
    for h in soup.find_all(["h3", "h4"]):
        name = h.get_text(" ", strip=True)
        if name not in headings or name in result:
            continue
        table = h.find_next("table")
        rows = []
        if table:
            for td in table.find_all("td"):
                a = td.find("a", href=True)
                if not a:
                    continue
                img = td.find("img")
                img_url = img and (img.get("data-src") or img.get("src"))
                if img_url and img_url.startswith("data:"):
                    img_url = None
                title = a.get_text(" ", strip=True) or (img.get("alt") if img else "")
                date_text = td.get_text(" ", strip=True).replace(title, "", 1).strip(" |")
                # Tanggal kadang di sel sebelah (td berikutnya)
                sib = td.find_next_sibling("td")
                if sib and not sib.find("a") and re.search(r"\d{4}", sib.get_text()):
                    date_text = (date_text + " " + sib.get_text(" ", strip=True)).strip()
                rows.append((title, a["href"], img_url, date_text))
        result[name] = rows
    return result


# ---------------------------------------------------------------------------
# Neverness to Everness (Game8)
# ---------------------------------------------------------------------------

def scrape_nte_events():
    print("Fetching Neverness to Everness (Game8)...")
    url = "https://game8.co/games/Neverness-to-Everness"
    events = []
    page = http_get(url).text
    secs = game8_sections(page, {"Current Banners", "Upcoming Banners", "Previous Banners",
                                 "Current Events", "Upcoming Events", "Previous Events"})
    for sect, rows in secs.items():
        is_banner = "Banner" in sect
        for title, href, img, date_text in rows:
            if not title:
                continue
            st, en = game8_article_dates(href)
            listed = parse_month_date(date_text)
            # Fallback dari tabel utama bila artikel tidak memuat tanggal
            if not st and listed and not re.search(r"until", date_text, re.I):
                st = listed
            if not en and listed and re.search(r"until", date_text, re.I):
                en = listed
            if not st or not en:
                print(f"  NTE skip (no reliable dates): {title}")
                continue
            events.append(make_event(
                "nte", title, day_start(st), day_end(en), "BANNER" if is_banner else classify(title),
                "Limited Banner" if is_banner else "Limited-Time Event",
                img, "https://game8.co" + href if href.startswith("/") else href))
    return events


# ---------------------------------------------------------------------------
# Persona 5: The Phantom X (Game8, server SEA/GMT+8)
# ---------------------------------------------------------------------------

def scrape_p5x_events():
    print("Fetching Persona 5: The Phantom X (Game8)...")
    url = "https://game8.co/games/Persona-5-Phantom-X"
    page = http_get(url).text
    events = []

    # Event: tanggal tersedia langsung di tabel (MM/DD/YYYY - MM/DD/YYYY)
    secs = game8_sections(page, {"Available Events", "Finished Events", "Upcoming Events",
                                 "Active Character Banners", "Finished Character Banners",
                                 "Active Weapon Banners", "Finished Weapon Banners", "Upcoming Banners"})
    for sect in ("Available Events", "Upcoming Events", "Finished Events"):
        for title, href, img, date_text in secs.get(sect, []):
            m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})\s*-\s*(\d{1,2})/(\d{1,2})/(\d{4})", date_text)
            if not m:
                continue
            mo1, d1, y1, mo2, d2, y2 = map(int, m.groups())
            st, en = datetime(y1, mo1, d1).date(), datetime(y2, mo2, d2).date()
            events.append(make_event("p5x", title, day_start(st), day_end(en), classify(title), "Event",
                                     img, "https://game8.co" + href))

    # Banner: tanggal (GMT+8) diambil dari halaman artikel banner
    for kind in ("Character", "Weapon"):
        for state in ("Active", "Upcoming", "Finished"):
            sect = f"{state} {kind} Banners" if state != "Upcoming" else "Upcoming Banners"
            rows = secs.get(sect, [])
            if state == "Finished":
                rows = rows[:8]  # riwayat secukupnya
            for idx, (title, href, img, _) in enumerate(rows):
                st, en = game8_article_dates(href)
                if (not st or not en) and kind == "Weapon":
                    # Banner senjata berpasangan dengan banner karakter pada urutan yang sama
                    chars = secs.get(f"{state} Character Banners", [])
                    if idx < len(chars):
                        st, en = game8_article_dates(chars[idx][1])
                if not st or not en:
                    print(f"  P5X skip (no reliable dates): {title}")
                    continue
                events.append(make_event("p5x", title, day_start(st), day_end(en), "BANNER",
                                         f"{kind} Banner", img, "https://game8.co" + href))
    return events


# ---------------------------------------------------------------------------
# Wuthering Waves: event dari Game8, banner dari Fandom
# ---------------------------------------------------------------------------

def strip_date_suffix(title):
    return re.sub(r"\s+\d{4}-\d{2}-\d{2}$", "", title or "").strip()


def wiki_image(img):
    if not img:
        return None
    url = img.get("data-src") or img.get("src")
    if not url or url.startswith("data:"):
        return None
    if "/revision/latest" in url:
        url = url.split("/revision/latest")[0] + "/revision/latest"
    return url


def scrape_wuwa_events():
    print("Fetching Wuthering Waves...")
    events = []

    # 1. Banner (Fandom - daftar lengkap fase convene, tanggal per fase)
    try:
        data = http_get("https://wutheringwaves.fandom.com/api.php", params={
            "action": "parse", "page": "Featured_Resonator_Convene", "format": "json", "prop": "text"}).json()
        soup = BeautifulSoup(data["parse"]["text"]["*"], "html.parser")
        for h in soup.find_all(["h2", "h3"]):
            span = h.find("span", class_="mw-headline")
            if not span or span.text.strip() != "List of Featured Resonator Convenes":
                continue
            table = h.find_next_sibling("table")
            if not table:
                continue
            for row in table.find_all("tr")[1:]:
                cols = row.find_all(["th", "td"])
                if len(cols) < 4:
                    continue
                a_tags = cols[1].find_all("a")
                title = strip_date_suffix(a_tags[-1].text.strip() if a_tags else cols[1].text.strip())
                st, en = parse_month_date(cols[2].text), parse_month_date(cols[3].text)
                if not title or not st or not en:
                    continue
                # Convene WuWa: mulai setelah maintenance / jam 10:00, berakhir 09:59 (UTC+8)
                start = datetime(st.year, st.month, st.day, 10, 0, tzinfo=TZ8)
                end = datetime(en.year, en.month, en.day, 9, 59, 59, tzinfo=TZ8)
                if end <= start:
                    end = day_end(en)
                events.append(make_event("wuwa", title, start, end, "BANNER", "Featured Resonator Convene",
                                         wiki_image(cols[0].find("img")), None,
                                         f"{title} is a Wuthering Waves Featured Resonator Convene."))
    except Exception as e:  # noqa: BLE001
        print(f"  Failed WuWa convenes: {e}")

    # 2. Event (Game8 - Current/Upcoming + daftar per versi, tanggal dari artikel)
    try:
        page = http_get("https://game8.co/games/Wuthering-Waves").text
        soup = BeautifulSoup(page, "html.parser")
        wanted = {"Current Events", "Upcoming Events"}
        for h in soup.find_all("h4"):
            if re.match(r"Version [\d.]+ Events and Game Modes", h.get_text(" ", strip=True)):
                wanted.add(h.get_text(" ", strip=True))
        secs = game8_sections(page, wanted)
        seen = set()
        for sect, rows in secs.items():
            for title, href, img, _ in rows:
                if not href or "/archives/" not in href:
                    continue
                href_abs = href if href.startswith("http") else "https://game8.co" + href
                if href_abs in seen:
                    continue
                seen.add(href_abs)
                st, en = game8_article_dates(href_abs)
                if not st or not en or (en - st).days > MAX_EVENT_DAYS:
                    continue
                if day_end(en) < NOW - timedelta(days=HISTORY_DAYS):
                    continue
                events.append(make_event("wuwa", title, day_start(st), day_end(en), classify(title),
                                         "Limited-Time Event", img, href_abs))
    except Exception as e:  # noqa: BLE001
        print(f"  Failed WuWa events: {e}")
    return events


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_previous():
    try:
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return []


def parse_iso(s):
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=TZ8)


def main():
    print(f"Mulai mengambil jadwal event... (now = {iso(NOW.astimezone(TZ8))})")
    scrapers = [
        ("gi", lambda: scrape_hoyo("gi")),
        ("hsr", lambda: scrape_hoyo("hsr")),
        ("zzz", lambda: scrape_hoyo("zzz")),
        ("wuwa", scrape_wuwa_events),
        ("endfield", scrape_endfield_events),
        ("nte", scrape_nte_events),
        ("p5x", scrape_p5x_events),
    ]

    previous = load_previous()
    # Hanya data format baru (id stabil "game-hash", waktu ber-offset) yang dipertahankan sebagai riwayat
    prev_valid = [e for e in previous if re.match(r"^[a-z0-9]+-[0-9a-f]{12}$", e.get("id", ""))]

    all_events = {}
    for game_id, fn in scrapers:
        try:
            evs = fn()
        except Exception as e:  # noqa: BLE001
            print(f"!! Scraper {game_id} gagal: {e}")
            evs = []
        if not evs:
            # Jangan hapus data game ini kalau sumbernya sedang error
            evs = [e for e in prev_valid if e["gameId"] == game_id]
            print(f"   {game_id}: 0 event baru, memakai {len(evs)} event dari data sebelumnya")
        for e in evs:
            all_events[e["id"]] = e
        active = sum(1 for e in evs if parse_iso(e["startTime"]) <= NOW < parse_iso(e["endTime"]))
        upcoming = sum(1 for e in evs if parse_iso(e["startTime"]) > NOW)
        print(f"   {game_id}: {len(evs)} event (aktif {active}, akan datang {upcoming})")

    # Gabungkan riwayat dari run sebelumnya (event yang sudah selesai)
    cutoff = NOW - timedelta(days=HISTORY_DAYS)
    keys = {(e["gameId"], norm_title(e["title"]), e["startTime"][:10]) for e in all_events.values()}
    for e in prev_valid:
        if e["id"] in all_events:
            continue
        k = (e["gameId"], norm_title(e["title"]), e["startTime"][:10])
        if k in keys:
            continue
        if cutoff < parse_iso(e["endTime"]) <= NOW:
            all_events[e["id"]] = e

    result = [e for e in all_events.values() if parse_iso(e["endTime"]) > cutoff]
    result.sort(key=lambda e: (e["gameId"], e["startTime"], e["title"]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Berhasil menyimpan {len(result)} event ke {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
