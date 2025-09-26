import time
import threading
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
from ovos_bus_client import MessageBusClient, Message

responses = []
response_received = threading.Event()

def on_message(message):
    global responses, response_received
    try:
        if hasattr(message, 'msg_type'):
            msg_type = message.msg_type
            msg_data = getattr(message, 'data', {})
        else:
            import json
            try:
                msg_dict = json.loads(message)
                msg_type = msg_dict.get('type', 'unknown')
                msg_data = msg_dict.get('data', {})
            except:
                msg_type = 'unknown'
                msg_data = str(message)
        if msg_type == 'speak':
            utter = msg_data.get('utterance', '')
            if utter:
                print(utter)
                response_received.set()
    except Exception:
        pass

bus = MessageBusClient()
bus.run_in_thread()

if not bus.connected_event.wait(5):
    print('❌ Hata: MessageBus\\'a bağlanılamadı!')
    exit(1)

bus.on('message', on_message)

# 81 il listesi (küçük harf)
cities = [
    'adana','adiyaman','afyonkarahisar','ağrı','amasya','ankara','antalya','artvin','aydın','balıkesir','bilecik','bingöl','bitlis','bolu','burdur','bursa','çanakkale','çankırı','çorum','denizli','diyarbakır','edirne','elazığ','erzincan','erzurum','eskişehir','gaziantep','giresun','gümüşhane','hakkari','hatay','ısparta','mersin','istanbul','izmir','kars','kastamonu','kayseri','kırklareli','kırşehir','kocaeli','konya','kütahya','malatya','manisa','kahramanmaraş','mardin','muğla','muş','nevşehir','niğde','ordu','rize','sakarya','samsun','siirt','sinop','sivas','tekirdağ','tokat','trabzon','tunceli','şanlıurfa','uşak','van','yozgat','zonguldak','aksaray','bayburt','karaman','kırıkkale','batman','şırnak','bartın','ardahan','ığdır','yalova','karabük','kilis','osmaniye','düzce'
]

utterance = '$UTTERANCE'.lower()

if 'hava' in utterance:
    city_found = None
    for city in cities:
        if city in utterance:
            # İlk bulunan il ile devam et
            city_found = city.capitalize()
            break
    if not city_found:
        city_found = 'İstanbul'  # varsayılan şehir
    weather_message = Message('my_weather_skill:get_weather', {'city': city_found})
    bus.emit(weather_message)

# SAAT ile ilgili istekleri yerelde, doğru timezone ile hesapla ve anında cevap ver
elif 'saat' in utterance or 'kaç' in utterance:
    try:
        # Tercihen zoneinfo kullan (Python 3.9+)
        if ZoneInfo is not None:
            tz = ZoneInfo('Europe/Istanbul')
            now = datetime.now(tz)
        else:
            # Fallback: Turkey UTC+3 (Türkiye 2016'dan beri +3 sabit)
            now = datetime.utcfromtimestamp(time.time() + 3*3600)
        time_str = now.strftime('%H:%M')
        print(f'Şu an saat {time_str}')
        # skill'den gelen speak mesajını bekleyen ana loop'u uyandırmak için event'i tetikle
        response_received.set()
    except Exception:
        # En son çare olarak sistem zamanını kullan
        try:
            time_str = time.strftime('%H:%M', time.localtime())
            print(f'Şu an saat {time_str}')
            response_received.set()
        except Exception:
            pass

if not response_received.wait($WAIT_TIME):
    print('Yanıt alınamadı')
