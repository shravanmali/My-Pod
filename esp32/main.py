import random
from machine import Pin, PWM
import math
import time
from st7789_fb import ST7789 , rgb565

lcd = ST7789(240 , 280)

BG = rgb565(0 , 0, 0)
AMBER = rgb565(255 , 159 , 10)
CARD = rgb565(22 , 26  , 32)
WHITE = rgb565(240 , 246 , 252)
MUTED = rgb565(139 , 148 , 158)
TRACK = rgb565(35 , 42 , 54)

clk = Pin(4, Pin.IN, Pin.PULL_UP)
dt = Pin(5, Pin.IN, Pin.PULL_UP)
sw = Pin(6, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(7), freq=2000, duty=0)

HUB_ITEMS = [
    ("MUSIC", "M"),
    ("NOW PLAYING", ">"),
    ("SHUFFLE", "S"),
    ("FILES", "F"),
    ("BLUETOOTH", "B"),
    ("SETTINGS", "*"),
]

TRACKS = [
    ("After Dark", "Mr.Kitty"),
    ("Blinding Lights", "The Weeknd"),
    ("Cruel Summer", "Taylor S."),
    ("Digital Love", "Daft Punk"),
    ("Electric Feel", "MGMT"),
    ("Midnight City", "M83"),
]

def tick(freq=2200 , ms=8):
    buzzer.freq(freq)
    buzzer.duty(128)
    time.sleep_ms(ms)
    buzzer.duty(0)

def draw_circle(fb, cx, cy, r, col, fill=False):
    if fill:
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            fb.hline(cx - dx, cy + dy, 2 * dx + 1, col)
    else:
        for deg in range(0, 360, 3):
            a = math.radians(deg)
            fb.pixel(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), col)

BT_LIST =["< Back" , "Power" ,"AirPods" ,"JBL Flip" , "Sony XM5"]
EQ_LIST = ["Flat","Base","Rock","Vocal"]

FILE_LIST = [
    ("< Back" ,"Return Home"),
    ("Synthwave/", "14 tracks"),
    ("Lo-Fi/" , "28 tracks"),
    ("Podcasts/","4 episodes"),
]

file_idx =0
vol = 75
bt_idx = 0
bt_on = True
bt_dev = "AirPods"
set_idx = 0
auto_bright = True
haptics = True
eq_idx = 0
screen = "HOME"
hub_idx = 0
song_idx = 0
cur_track = 0

def draw_message(title ,line1 ,line2):
    lcd.fill(BG)
    lcd.hline(0 ,22,240,TRACK)
    lcd.text(title,26,30,AMBER)
    lcd.text(line1,20,90,WHITE)
    lcd.text(line2 ,20,115,MUTED)
    lcd.text("[CLICK: HOME]",68 , 242 ,MUTED)
    lcd.show()
    
def draw_list(title , rows , sel_idx):
    lcd.fill(BG)
    lcd.hline(0, 22 , 240 , TRACK)
    lcd.text(title,26 ,30, AMBER)
    y = 54
    for i , (name , val) in enumerate(rows):
        sel = (i == sel_idx)
        if sel:
            lcd.fill_rect(12 , y ,216,28 ,AMBER)
            lcd.text(name, 20, y + 4, BG)
            lcd.text(val, 20, y + 16, BG)
        else:
            lcd.text(name , 20 ,y + 4,WHITE)
            lcd.text(val , 20 ,y + 16,MUTED)
        y += 32
    lcd.show()
def draw_bt():
    rows =[]
    for name in BT_LIST:
        if name == "< Back":
            val = "Return Home"
        elif name == "Power":
            val = "ON" if bt_on else "OFF"
        elif bt_on and name == bt_dev:
            val = "Connected"
        else:
            val = "Tap to pair"
        rows.append((name , val))
    draw_list("BLUETOOTH",rows , bt_idx)

def draw_settings():
    rows = [
        ("< Back","Return Home"),
        ("Auto Bright","ON (LDR)" if auto_bright else "OFF"),
        ("Haptics","ON" if haptics else "OFF"),
        ("EQ preset",EQ_LIST[eq_idx]),
        ]
    draw_list("SETTINGS",rows,set_idx)

def draw_files():
    draw_list("FILES (SD)" , FILE_LIST , file_idx)

def draw_home():
    lcd.fill(BG)
    lcd.hline(0, 22, 240, TRACK)
    lcd.text("12:45", 16, 8, MUTED)
    lcd.text("MY-POD", 96, 8, AMBER)

    cx, cy, orbit_r = 120, 148, 80
    draw_circle(lcd, cx, cy, orbit_r, TRACK, False)
    for i, (title, ch) in enumerate(HUB_ITEMS):
        ang = i * (2 * math.pi / 6) - (math.pi / 2)
        nx = cx + int(orbit_r * math.cos(ang))
        ny = cy + int(orbit_r * math.sin(ang))
        sel = (i == hub_idx)
        if sel:
            draw_circle(lcd, nx, ny, 23, AMBER, False)
            draw_circle(lcd, nx, ny, 20, AMBER, True)
            lcd.text(ch, nx - 4, ny - 4, BG)
        else:
            draw_circle(lcd, nx, ny, 16, CARD, True)
            lcd.text(ch, nx - 4, ny - 4, MUTED)
    
    draw_circle(lcd, cx , cy, 40 ,CARD , True)
    draw_circle(lcd, cx , cy, 40 ,AMBER , False)
    lbl =HUB_ITEMS[hub_idx][0]
    lcd.text(lbl , cx - (len(lbl)* 4),cy - 4,AMBER)
    lcd.show()

def draw_songs():
    lcd.fill(BG)
    lcd.hline(0 , 22, 240 , TRACK)
    lcd.text("TRACKS" ,26 , 30 , AMBER)
    y = 54
    for i , (title , artist) in enumerate(TRACKS):
        sel = (i == song_idx)
        if sel :
            lcd.fill_rect(12 , y , 216,28 , AMBER)
            lcd.text(title,20 , y+ 4 ,BG)
            lcd.text(artist,20 , y+ 16 , BG )
        else:
            lcd.text(title,20,y+ 4 ,WHITE)
            lcd.text(artist,20,y+ 16 ,MUTED)
        y += 32
    lcd.show() 

def draw_now_playing():
    lcd.fill(BG)
    lcd.hline(0,22,240,TRACK)
    lcd.text("NOW PLAYING",76 , 30 ,AMBER)
    draw_circle(lcd , 120 , 108 , 42 ,CARD , True)
    draw_circle(lcd , 120 , 108 , 42 ,TRACK , False)
    draw_circle(lcd , 120 , 108 , 10 ,AMBER , True)
    title, artist = TRACKS[cur_track]
    lcd.text(title, 120 - len(title) * 4, 170, WHITE)
    lcd.text(artist, 120 - len(artist) * 4, 188, MUTED)
    lcd.fill_rect(28, 215, 184, 5, TRACK)
    lcd.fill_rect(28, 215, 80, 5, AMBER)
    lcd.text("VOL" + str(vol) + "%" ,92 ,226 ,AMBER)
    lcd.text("[CLICK: HOME]", 68, 242, MUTED)
    lcd.show()

draw_home()

last_clk = clk.value()
last_sw = sw.value()
last_sw_ms = 0

while True:
    c = clk.value()
    if c != last_clk and c == 0:
        step = 1 if dt.value() != c else -1
        tick(2200, 6)
        if screen == "HOME":
            hub_idx = (hub_idx + step) % len(HUB_ITEMS)
            draw_home()
        elif screen == "SONGS":
            song_idx = max(0, min(len(TRACKS) - 1, song_idx + step))
            draw_songs()
        elif screen == "BT":
            bt_idx = max(0 ,min(len(BT_LIST) - 1,bt_idx + step))
            draw_bt()
        elif screen == "SETTINGS":
            set_idx = max(0, min (3, set_idx + step))
            draw_settings()
        elif screen == "FILES":
            file_idx = max(0 , min(len(FILE_LIST) - 1 , file_idx + step))
            draw_files()
        elif screen == "NOW":
            vol = max(0 , min (100 , vol + step * 5))
            draw_now_playing()
    last_clk = c


    s = sw.value()
    now = time.ticks_ms()
    if s == 0 and last_sw == 1 and time.ticks_diff(now, last_sw_ms) > 250:
        last_sw_ms = now
        tick(2800, 12)
        if screen == "HOME":
            if hub_idx == 0:
                screen = "SONGS"
                draw_songs()
            elif hub_idx == 1:
                screen = "NOW"
                draw_now_playing()
            elif hub_idx == 2:
                cur_track = random.randrange(len(TRACKS))
                screen ="NOW"
                draw_now_playing()
            elif hub_idx == 3:
                file_idx = 1
                screen = "FILES"
                draw_files()
            elif hub_idx == 4:
                bt_idx = 1
                screen = "BT"
                draw_bt()
            elif hub_idx == 5 :
                set_idx = 1
                screen = "SETTINGS"
                draw_settings()  
        elif screen == "SONGS":
            cur_track = song_idx
            screen = "NOW"
            draw_now_playing()
        elif screen == "NOW":
            screen = "HOME"
            draw_home()
        elif screen == "INFO":
            screen = "HOME"
            draw_home()
        elif screen == "BT":
            if bt_idx == 0:
                screen = "HOME"
                draw_home()
            elif bt_idx == 1:
                bt_on = not bt_on
                if not bt_on:
                    bt_dev = ""
                draw_bt()
            elif bt_on:
                name = BT_LIST[bt_idx]
                bt_dev = "" if bt_dev == name else name
                draw_bt()
        elif screen == "SETTINGS":
            if set_idx == 0:
                screen = "HOME"
                draw_home()
            elif set_idx == 1:
                auto_bright = not auto_bright
                draw_settings()
            elif set_idx == 2:
                haptics = not haptics
                draw_settings()
            elif set_idx == 3:
                eq_idx = (eq_idx + 1) % len(EQ_LIST)
                draw_settings()
        elif screen == "FILES":
            if file_idx == 0:
                screen = "HOME"
                draw_home()
            else:
                song_idx =0
                screen = "SONGS"
                draw_songs()

    last_sw = s
    time.sleep_ms(2)



            

            








