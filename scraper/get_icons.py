import urllib.request, re

def get_play_icon(pkg):
    url = f'https://play.google.com/store/apps/details?id={pkg}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        match = re.search(r'<img[^>]+src="(https://play-lh.googleusercontent.com/[^"]+)"[^>]+alt="Icon image"', html)
        if match:
            return match.group(1).replace('=s48-rw', '=s256-rw')
    except Exception as e:
        print(f'Error for {pkg}: {e}')
    return None

print('GI:', get_play_icon('com.miHoYo.GenshinImpact'))
print('HSR:', get_play_icon('com.HoYoverse.hkrpgoversea'))
print('ZZZ:', get_play_icon('com.HoYoverse.Nap'))
print('WuWa:', get_play_icon('com.kurogame.wutheringwaves.global'))
print('Arknights:', get_play_icon('com.YoStarEN.Arknights'))
