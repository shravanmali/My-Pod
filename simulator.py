"""
My-Pod UI Simulator (240x280 ST7789 IPS Display)
Theme: Studio Dark (Obsidian + Electric Amber)

Controls:
- UP / DOWN Arrow OR Mouse Scroll Wheel: Turn Rotary Encoder
- ENTER / SPACE: Center Click (Select / Play-Pause)
- BACKSPACE / ESC: Long-Press Back (Return to Previous Screen)
"""

import sys
import math
import pygame
import random

# -------------------------------------------------------------
# 1. HARDWARE & DISPLAY CONSTANTS
# -------------------------------------------------------------
NATIVE_WIDTH = 240
NATIVE_HEIGHT = 280
CORNER_RADIUS = 43     # 4-R5 mm = ~43px on 0.1165mm pitch

SCALE = 0.65           # 0.65 = ~1:1 real 1.69" size on 1080p laptop (2.5 = zoomed view)
WINDOW_WIDTH = max(420, int(NATIVE_WIDTH * SCALE) + 80)   # Extra margin for wooden chassis frame
WINDOW_HEIGHT = max(340, int(NATIVE_HEIGHT * SCALE) + 80)

# -------------------------------------------------------------
# 2. COLOR PALETTE (Theme A: Studio Dark)
# -------------------------------------------------------------
COLOR_CHASSIS     = (28, 22, 18)     # Layered 2.1mm MDF wood enclosure
COLOR_BEZEL       = (10, 10, 12)     # Screen glass bezel
COLOR_BG          = (14, 17, 22)     # Deep Obsidian screen background
COLOR_AMBER       = (255, 159, 10)   # Electric Amber highlight
COLOR_AMBER_DARK  = (120, 70, 0)     # Dimmed Amber
COLOR_CARD        = (24, 29, 36)     # Unfocused node background
COLOR_TEXT_WHITE  = (240, 246, 252)  # Primary text
COLOR_TEXT_MUTED  = (139, 148, 158)  # Subtitle / secondary text
COLOR_DIVIDER     = (35, 42, 52)     # Status bar line

# -------------------------------------------------------------
# 3. MENU DATA & STATE
# -------------------------------------------------------------
HUB_ITEMS = [
    {"id": "music",       "title": "MUSIC",       "icon": "M"},
    {"id": "now_playing", "title": "NOW PLAYING", "icon": ">"},
    {"id": "shuffle",     "title": "SHUFFLE",     "icon": "S"},
    {"id": "files",       "title": "FILES",       "icon": "F"},
    {"id": "bluetooth",   "title": "BLUETOOTH",   "icon": "B"},
    {"id": "settings",    "title": "SETTINGS",    "icon": "*"},
]

SHUFFLE_ITEMS = [
    {"id":"shuf_all", "title":"All Tracks", "icon":"A"},
    {"id":"shuf_genres", "title":"By Genre", "icon":"G"},
    {"id":"shuf_artists", "title":"By Artist", "icon":"A"},
    {"id":"shuf_playlists", "title":"Playlists", "icon":"P"},
    {"id":"shuf_fav", "title":"Favorites", "icon":"F"},
    {"id":"back", "title":"< Back", "icon":"<"},
]
MUSIC_MENU_ITEMS = [
    {"id":"back", "title":"< Back", "subtitle":"Return to home"},
    {"id":"tracks", "title":"All Tracks", "subtitle":"16 songs (A-Z)"},
    {"id":"alpha","title":"Quick Jump (A-Z)","subtitle":"7-screen latter orbit"},
    {"id":"artists", "title":"Artists", "subtitle":"Browse by artist"},
    {"id":"albums", "title":"Albums", "subtitle":"Browse by album"},
    {"id":"playlists", "title":"Playlists", "subtitle":"Save M3U lists"},
    {"id":"genres", "title":"Genres", "subtitle":"Synthwave . Pop , Idnie , Rock"},
]
    
FILE_ITEMS = [
    {"id":"back", "title":"< Back", "subtitle":"Return to home"},
    {"id":"dir_1", "title":"[DIR] Synthwave/", "subtitle":"14 songs"},
    {"id":"dir_2", "title":"[DIR] Lo-Fi/", "subtitle":"28 tracks"},
    {"id":"dir_3", "title":"[DIR] Podcasts/", "subtitle":"4 episodes"},
    {"id":"file_1", "title":"demo_master.flac", "subtitle":"24-bit • 48kHz"},
]
    
BT_DEVICES = [
    {"id":"back", "title":"< Back", "subtitle":"Return to home"},
    {"id":"bt_pwr", "title":"Bluetooth Power", "subtitle":"Toggle radio"},
    {"id":"bt_1", "title":"HEADPHONES-1234", "subtitle":"tap to connect"},
    {"id":"bt_2", "title":"CAR-AUX-5678", "subtitle":"tap to connect"},
    {"id":"bt_3", "title":"SPEAKER-ABCD", "subtitle":"tap to connect"},
]

EQ_PRESETS = ["Flat", "Bass Boost", "Treble Boost", "Vocal", "Rock"]   
SLEEP_OPTIONS = ["Off", "5 min", "10 min", "15 min", "30 min", "60 min"]

SAMPLE_TRACKS = [
    {"title": "After Dark",      "artist": "Mr.Kitty",   "genre": "Synthwave", "duration": 257},
    {"title": "Blinding Lights", "artist": "The Weeknd", "genre": "Pop",       "duration": 200},
    {"title": "Cruel Summer",    "artist": "Taylor S.",  "genre": "Pop",       "duration": 178},
    {"title": "Digital Love",    "artist": "Daft Punk",  "genre": "Electronic","duration": 298},
    {"title": "Electric Feel",   "artist": "MGMT",       "genre": "Indie",     "duration": 229},
    {"title": "Feels Like",      "artist": "Gracie A.",  "genre": "Pop",       "duration": 195},
    {"title": "Get Lucky",       "artist": "Daft Punk",  "genre": "Funk",      "duration": 248},
    {"title": "Heartless",       "artist": "The Weeknd", "genre": "R&B",       "duration": 198},
    {"title": "Instant Crush",   "artist": "Daft Punk",  "genre": "Synthwave", "duration": 337},
    {"title": "Just Dance",      "artist": "Lady Gaga",  "genre": "Pop",       "duration": 242},
    {"title": "Kavinsky Drive",  "artist": "Kavinsky",   "genre": "Synthwave", "duration": 220},
    {"title": "Levitating",      "artist": "Dua Lipa",   "genre": "Pop",       "duration": 203},
    {"title": "Midnight City",   "artist": "M83",        "genre": "Synthwave", "duration": 243},
    {"title": "Nightcall",       "artist": "Kavinsky",   "genre": "Synthwave", "duration": 259},
    {"title": "Resonance",       "artist": "HOME",       "genre": "Synthwave", "duration": 212},
    {"title": "Starboy",         "artist": "The Weeknd", "genre": "R&B",       "duration": 230},
]

ALPHA_PAGES = [
    ["A", "B", "C", "D", ">", "BACK"],
    ["E", "F", "G", "H", ">", "<"],
    ["I", "J", "K", "L", ">", "<"],
    ["M", "N", "O", "P", ">", "<"],
    ["Q", "R", "S", "T", ">", "<"],
    ["U", "V", "W", "X", ">", "<"],
    ["Y", "Z", "#", "ALL", "BACK", "<"],
]



class MyPodSimulator:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("My-Pod Desktop Simulator (240x280)")
        
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Native 240x280 display buffer
        self.screen_buffer = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT))
        
        # Corner masking surface for 43px rounded screen simulation
        self.mask_surface = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT), pygame.SRCALPHA)
        self.init_corner_mask()
        
        # Typography
        self.font_large = pygame.font.SysFont("segoeui,helvetica,arial", 18, bold=True)
        self.font_mid   = pygame.font.SysFont("segoeui,helvetica,arial", 13, bold=True)
        self.font_small = pygame.font.SysFont("segoeui,helvetica,arial", 12, bold=True)
        self.font_tiny  = pygame.font.SysFont("segoeui,helvetica,arial", 10, bold=True)

        # State Machine
        self.current_screen = "HOME_ORBIT"   # "HOME_ORBIT", "SONG_LIST", "NOW_PLAYING"
        self.selected_hub_index = 0
        self.highlight_angle = -math.pi / 2  # Current angle of the highlighter (starts at top, -90 deg)
        self.target_highlight_angle = -math.pi / 2
        self.departure_angle = -math.pi / 2  # The circle angle we are traveling FROM
        
        self.shuffle_index = 0 
        self.file_index = 0
        self.bt_index = 0
        self.settings_index = 0

        self.bt_enabled = True
        self.bt_connected = "AirPods Pro"
        self.auto_brightness = True
        self.haptic_click = True
        self.eq_index = 0
        self.sleep_index = 0

        self.music_menu_index = 0

        # Song list state
        self.selected_song_index = 0
        self.alpha_page = 0
        self.alpha_node_index = 0
        self.vinyl_angle = 0.0
        self.list_scroll_offset = 0
        
        # Playback state
        self.current_track = SAMPLE_TRACKS[0]
        self.is_playing = True
        self.playback_time = 45.0
        self.volume = 75
        self.scale = 2.5
        self.overlay_mode = None
        self.overlay_timer = 0

        # Icon Images (Loaded from assets/)
        self.icons = {}
        self.icons["bluetooth"] = pygame.image.load("assets/bluetooth.png")
        self.icons["music"] = pygame.image.load("assets/music.png")
        self.icons["now_playing"] = pygame.image.load("assets/now_playing.png")
        self.icons["shuffle"] = pygame.image.load("assets/shuffle.png")
        self.icons["files"] = pygame.image.load("assets/files.png")
        self.icons["settings"] = pygame.image.load("assets/settings.png")
        
    def init_corner_mask(self):
        """Creates transparent cutouts for the 43px rounded screen edges."""
        self.mask_surface.fill((*COLOR_BEZEL, 255))
        rect = pygame.Rect(0, 0, NATIVE_WIDTH, NATIVE_HEIGHT)
        pygame.draw.rect(self.mask_surface, (0, 0, 0, 0), rect, border_radius=CORNER_RADIUS)

    def run(self):
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)
                elif event.type == pygame.MOUSEWHEEL:
                    self.handle_wheel(event.y)

            # Update physics / animation
            self.update()

            # Render
            self.render()

            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_wheel(self, direction):
        """Simulates rotary encoder turning (direction: +1 CW, -1 CCW)."""
        if direction > 0:
            self.on_rotate_clockwise()
        elif direction < 0:
            self.on_rotate_counter_clockwise()

    def handle_keydown(self, key):
        if key == pygame.K_RIGHT:
            if self.current_screen == "NOW_PLAYING" :
                self.next_track()
            else:
                self.on_rotate_clockwise()
        elif key == pygame.K_LEFT :
            if self.current_screen == "NOW_PLAYING" :
                self.prev_track()
            else :
                self.on_rotate_counter_clockwise()
        elif key == pygame.K_DOWN :
            self.on_rotate_clockwise()
        elif key == pygame.K_UP :
            self.on_rotate_counter_clockwise()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.on_center_click()
        elif key == pygame.K_h:
            self.highlight_angle = self.selected_hub_index * (2 * math.pi / len(HUB_ITEMS)) - (math.pi / 2)
            self.target_highlight_angle = self.highlight_angle
            self.departure_angle = self.highlight_angle
            self.departure_angle = self.highlight_angle
            self.current_screen = "HOME_ORBIT"
        elif key == pygame.K_r:
            self.scale = 0.65 if self.scale > 1.0 else 2.5
            w = max(420 , int(NATIVE_WIDTH * self.scale) + 80)
            h = max(340, int(NATIVE_HEIGHT * self.scale) + 80 )
            self.window = pygame.display.set_mode((w,h))
        elif key in (pygame.K_BACKSPACE , pygame.K_ESCAPE):
            self.on_back_click()

    def next_track(self):
        self.selected_song_index = (self.selected_song_index + 1) % len(SAMPLE_TRACKS) 
        self.current_track = SAMPLE_TRACKS[self.selected_song_index]
        self.playback_time = 0.0
        self.is_playing = True 

    def prev_track(self):
        self.selected_song_index = (self.selected_song_index -1 ) % len(SAMPLE_TRACKS)
        self.current_track = SAMPLE_TRACKS[self.selected_song_index]
        self.playback_time = 0.0
        self.is_playing = True 
        
            


    def on_rotate_clockwise(self):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_v]:
            self.volume = min(100, self.volume + 5)
            self.overlay_mode = "VOL"
            self.overlay_timer = 90
            return
        if keys[pygame.K_s]:
            self.playback_time = min(float(self.current_track["duration"] ), self.playback_time + 5.0)
            self.overlay_mode = "SEEK"
            self.overlay_timer = 90
            return  

        if self.current_screen == "HOME_ORBIT":
            self.departure_angle = self.highlight_angle
            self.selected_hub_index = (self.selected_hub_index + 1) % len(HUB_ITEMS)
            self.target_highlight_angle = self.selected_hub_index * (2 * math.pi / len(HUB_ITEMS)) - (math.pi / 2)
        
        elif self.current_screen == "SHUFFLE_ORBIT":
            self.departure_angle = self.highlight_angle
            self.shuffle_index = (self.shuffle_index + 1) % len(SHUFFLE_ITEMS)
            self.target_highlight_angle = self.shuffle_index * (2 * math.pi / len(SHUFFLE_ITEMS)) - (math.pi / 2)

        elif self.current_screen == "ALPHA_ORBIT":
            self.departure_angle = self.highlight_angle
            self.alpha_node_index = (self.alpha_node_index + 1) % 6
            self.target_highlight_angle = self.alpha_node_index * (2 * math.pi / 6) - (math.pi / 2)


        elif self.current_screen == "MUSIC_MENU":
            if self.music_menu_index < len(MUSIC_MENU_ITEMS) - 1:
                self.music_menu_index += 1
      
        elif self.current_screen == "SONG_LIST":
            if self.selected_song_index < len(SAMPLE_TRACKS) - 1:
                self.selected_song_index += 1
                if self.selected_song_index >= self.list_scroll_offset + 6:
                    self.list_scroll_offset += 1


        elif self.current_screen == "FILE_SCREEN":
            if self.file_index < len(FILE_ITEMS) - 1:
                self.file_index += 1
        elif self.current_screen == "BT_SCREEN":
            if self.bt_index < len(BT_DEVICES) - 1:
                self.bt_index += 1
        elif self.current_screen == "SETTINGS_SCREEN":
            if self.settings_index < 4:
                self.settings_index += 1

        elif self.current_screen == "NOW_PLAYING":
            self.volume = min(100, self.volume + 5)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_v]:
                self.volume = max(0 , self.volume - 5)
                self.overlay_mode = "VOL"
                self.overlay_timer = 90
                return
            if keys[pygame.K_s]:
                self.playback_time = max(0.0 , self.playback_time - 5.0)
                self.overlay_mode = "SEEK"
                self.overlay_timer = 90
                return  

    def on_rotate_counter_clockwise(self):
        if self.current_screen == "HOME_ORBIT":
            self.departure_angle = self.highlight_angle
            self.selected_hub_index = (self.selected_hub_index - 1) % len(HUB_ITEMS)
            self.target_highlight_angle = self.selected_hub_index * (2 * math.pi / len(HUB_ITEMS)) - (math.pi / 2)
        
        elif self.current_screen == "SHUFFLE_ORBIT":
            self.departure_angle = self.highlight_angle
            self.shuffle_index = (self.shuffle_index - 1) % len(SHUFFLE_ITEMS)
            self.target_highlight_angle = self.shuffle_index * (2 * math.pi / len(SHUFFLE_ITEMS)) - (math.pi / 2)

        elif self.current_screen == "ALPHA_ORBIT":
            self.departure_angle = self.highlight_angle
            self.alpha_node_index = (self.alpha_node_index - 1) % 6
            self.target_highlight_angle = self.alpha_node_index * (2 * math.pi / 6) - (math.pi / 2)

        elif self.current_screen == "MUSIC_MENU":
            if self.music_menu_index > 0:
                self.music_menu_index -= 1
       
        elif self.current_screen == "SONG_LIST":
            if self.selected_song_index > 0:
                self.selected_song_index -= 1
                if self.selected_song_index < self.list_scroll_offset:
                    self.list_scroll_offset -= 1

        elif self.current_screen == "ALPHA_ORBIT":
            self.departure_angle = self.highlight_angle
            self.alpha_node_index = (self.alpha_node_index - 1) % 6
            self.target_highlight_angle = self.alpha_node_index * (2 * math.pi / 6) - (math.pi / 2)

        elif self.current_screen == "FILE_SCREEN":
            if self.file_index > 0:
                self.file_index -= 1
        elif self.current_screen == "BT_SCREEN":
            if self.bt_index > 0:
                self.bt_index -= 1
        elif self.current_screen == "SETTINGS_SCREEN":
            if self.settings_index > 0:
                self.settings_index -= 1   

        elif self.current_screen == "NOW_PLAYING":
            self.volume = max(0, self.volume - 5)

    def on_center_click(self):
        if self.current_screen == "HOME_ORBIT":
            selected_id = HUB_ITEMS[self.selected_hub_index]["id"]
            if selected_id == "music":
                self.music_menu_index = 1
                self.current_screen = "MUSIC_MENU"
            elif selected_id == "now_playing":
                self.current_screen = "NOW_PLAYING"
            elif selected_id == "shuffle":
                self.shuffle_index = 0
                self.highlight_angle = -math.pi / 2
                self.target_highlight_angle = -math.pi / 2
                self.departure_angle = -math.pi / 2
                self.current_screen = "SHUFFLE_ORBIT"
            elif selected_id == "files":
                self.file_index = 1
                self.current_screen = "FILE_SCREEN"
            elif selected_id == "bluetooth":
                self.bt_index = 1
                self.current_screen = "BT_SCREEN"
            elif selected_id == "settings":
                self.settings_index = 0
                self.current_screen = "SETTINGS_SCREEN"

        elif self.current_screen == "ALPHA_ORBIT":
            val = ALPHA_PAGES[self.alpha_page][self.alpha_node_index]
            if val == "BACK":
                self.on_back_click()
            elif val == ">":
                self.alpha_page = (self.alpha_page + 1) % len(ALPHA_PAGES)
            elif val == "<":
                self.alpha_page = (self.alpha_page - 1) % len(ALPHA_PAGES)
            elif val == "ALL":
                self.selected_song_index = 0
                self.list_scroll_offset = 0
                self.current_screen = "SONG_LIST"
            else:
                target_idx = 0
                for idx, tr in enumerate(SAMPLE_TRACKS):
                    if tr["title"].upper().startswith(val) or tr["title"][0].upper() >= val:
                        target_idx = idx
                        break
                self.selected_song_index = target_idx
                self.list_scroll_offset = max(0, min(target_idx, len(SAMPLE_TRACKS) - 6))
                self.current_screen = "SONG_LIST"

         

        elif self.current_screen == "SHUFFLE_ORBIT":
            choice = SHUFFLE_ITEMS[self.shuffle_index]["id"]
            if choice == "back":
                self.on_back_click()
            else:
                self.current_track = random.choice(SAMPLE_TRACKS)
                self.playback_time = 0.0
                self.is_playing = True
                self.current_screen = "NOW_PLAYING"

        elif self.current_screen == "MUSIC_MENU":
            choice = MUSIC_MENU_ITEMS[self.music_menu_index]["id"]
            if choice == "back":
                self.on_back_click()
            elif choice == "tracks":
                self.selected_song_index = 0
                self.list_scroll_offset = 0
                self.current_screen = "SONG_LIST"
            elif choice == "alpha":
                self.alpha_page = 0
                self.alpha_node_index = 0
                self.highlight_angle = -math.pi / 2
                self.target_highlight_angle = -math.pi / 2
                self.departure_angle = -math.pi / 2
                self.current_screen = "ALPHA_ORBIT"
         
        elif self.current_screen == "SONG_LIST":
            self.current_track = SAMPLE_TRACKS[self.selected_song_index]
            self.playback_time = 0.0
            self.is_playing = True
            self.current_screen = "NOW_PLAYING"
        elif self.current_screen == "NOW_PLAYING": self.is_playing = not self.is_playing

        elif self.current_screen == "FILE_SCREEN":
            if FILE_ITEMS[self.file_index]["id"] == "back":
                self.on_back_click()
            elif FILE_ITEMS[self.file_index]["id"].startswith("dir_"):
                self.selected_song_index = 0
                self.current_screen = "SONG_LIST"

        elif self.current_screen == "BT_SCREEN":
            item_id = BT_DEVICES[self.bt_index]["id"]
            if item_id == "back":
                self.on_back_click()
            elif item_id == "bt_pwr":
                self.bt_enabled = not self.bt_enabled
                if not self.bt_enabled:
                    self.bt_connected = None
            elif self.bt_enabled:
                name = BT_DEVICES[self.bt_index]["title"]
                self.bt_connected = None if self.bt_connected == name else name

        elif self.current_screen == "SETTINGS_SCREEN":
            if self.settings_index == 0:
                self.on_back_click()
            elif self.settings_index == 1:
                self.auto_brightness = not self.auto_brightness
            elif self.settings_index == 2:
                self.haptic_click = not self.haptic_click
            elif self.settings_index == 3:
                self.eq_index = (self.eq_index + 1) % len(EQ_PRESETS)
            elif self.settings_index == 4:
                self.sleep_index = (self.sleep_index + 1) % len(SLEEP_OPTIONS)
    

    def on_back_click(self):
        if self.current_screen == "SONG_LIST":
            self.current_screen = "MUSIC_MENU"
        elif self.current_screen in ["SHUFFLE_ORBIT", "MUSIC_MENU", "NOW_PLAYING", "FILE_SCREEN", "BT_SCREEN", "SETTINGS_SCREEN"]:
     
            self.highlight_angle = self.selected_hub_index * (2 * math.pi / len(HUB_ITEMS)) - (math.pi / 2)
            self.target_highlight_angle = self.highlight_angle
            self.departure_angle = self.highlight_angle
            self.current_screen = "HOME_ORBIT"

        if self.current_screen == "ALPHA_ORBIT":
            self.current_screen = "MUSIC_MENU"

    def update(self):
        # Smooth interpolation for highlighter angle (shortest angular distance)
        diff = (self.target_highlight_angle - self.highlight_angle + math.pi) % (2 * math.pi) - math.pi
        self.highlight_angle += diff * 0.28

        # Increment playback timer
        if self.is_playing and self.current_screen == "NOW_PLAYING":
            self.playback_time = min(float(self.current_track["duration"]), self.playback_time + 1/60)

        if self.is_playing :
            self.vinyl_angle += 0.04
        if self.overlay_timer > 0:
            self.overlay_timer -= 1

    # ---------------------------------------------------------
    # RENDERING ENGINE
    # ---------------------------------------------------------

    def render(self):
        # 1. Clear native buffer
        self.screen_buffer.fill(COLOR_BG)

        # 2. Render active screen content
        if self.current_screen == "HOME_ORBIT":
            self.render_home_orbit()
        elif self.current_screen == "SHUFFLE_ORBIT":
            self.render_shuffle_orbit()
        elif self.current_screen == "MUSIC_MENU":
            self.render_music_menu()
        elif self.current_screen == "SONG_LIST":
            self.render_song_list()
        elif self.current_screen == "NOW_PLAYING":
            self.render_now_playing()
        elif self.current_screen == "FILE_SCREEN":
            self.render_file_screen()
        elif self.current_screen == "BT_SCREEN":
            self.render_bt_screen()
        elif self.current_screen == "SETTINGS_SCREEN":
            self.render_settings_screen()
        elif self.current_screen == "ALPHA_ORBIT":
            self.render_alpha_orbit()
        # 3. Render Status Bar on top
        self.render_status_bar()
        if self.overlay_timer > 0:
            self.render_overlay()

        # 4. Apply 43px rounded corners mask
        # We fill outside the mask with bezel color
        self.screen_buffer.blit(self.mask_surface, (0, 0))
        
        # 5. Blit to main desktop window with scale and chassis
        self.window.fill(COLOR_CHASSIS)
        
        # Scaled LCD display (use smoothscale when shrinking below 1.0x so text doesn't drop pixels)
        scale_fn = pygame.transform.smoothscale if SCALE < 1.0 else pygame.transform.scale
        scaled_lcd = scale_fn(
            self.screen_buffer, 
            (int(NATIVE_WIDTH * SCALE), int(NATIVE_HEIGHT * SCALE))
        )
        
        # Position centered inside wooden chassis
        win_w ,win_h = self.window.get_size()
        screen_x = (win_w - scaled_lcd.get_width()) // 2
        screen_y = (win_h - scaled_lcd.get_height()) // 2
        
        # Glass bezel border
        bezel_rect = pygame.Rect(
            screen_x - 6, screen_y - 6, 
            scaled_lcd.get_width() + 12, scaled_lcd.get_height() + 12
        )
        pygame.draw.rect(self.window, COLOR_BEZEL, bezel_rect, border_radius=int(CORNER_RADIUS * SCALE) + 4)
        
        self.window.blit(scaled_lcd, (screen_x, screen_y))

        # Instructions banner at bottom
        hint = self.font_tiny.render("Wheel : Scroll | V+Wheel : Vol | S+Wheel : Seek | H:Home | R: 1:1 size",  True, (160, 140, 120))
        self.window.blit(hint, ((win_w - hint.get_width()) // 2, win_h - 24))

        pygame.display.flip()

    def render_overlay(self):
        box_w, box_h = 164, 42
        box_x = (NATIVE_WIDTH - box_w) // 2
        box_y = NATIVE_HEIGHT - 64

        pygame.draw.rect(self.screen_buffer, (20, 24, 30), (box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(self.screen_buffer, COLOR_AMBER, (box_x, box_y, box_w, box_h), 2, border_radius=10)

        if self.overlay_mode == "VOL":
            label = f"VOLUME  {self.volume}%"
            ratio = self.volume / 100.0
        else:
            cur_m, cur_s = divmod(int(self.playback_time), 60)
            tot_m, tot_s = divmod(int(self.current_track["duration"]), 60)
            label = f"SEEK  {cur_m:02d}:{cur_s:02d} / {tot_m:02d}:{tot_s:02d}"
            ratio = self.playback_time / float(self.current_track["duration"])

        txt = self.font_tiny.render(label, True, COLOR_TEXT_WHITE)
        self.screen_buffer.blit(txt, (box_x + 12, box_y + 8))

        bar_x, bar_y, bar_w = box_x + 12, box_y + 26, box_w - 24
        pygame.draw.rect(self.screen_buffer, (40, 48, 60), (bar_x, bar_y, bar_w, 6), border_radius=3)
        fill_w = int(bar_w * max(0.0, min(1.0, ratio)))
        if fill_w > 0:
            pygame.draw.rect(self.screen_buffer, COLOR_AMBER, (bar_x, bar_y, fill_w, 6), border_radius=3)        

    def render_status_bar(self):
        """Top 22px Status Bar: Clock, Animated Waveform, Battery."""
        pygame.draw.line(self.screen_buffer, COLOR_DIVIDER, (0, 22), (NATIVE_WIDTH, 22), 1)

        # Time
        time_surf = self.font_small.render("12:45", True, COLOR_TEXT_MUTED)
        self.screen_buffer.blit(time_surf, (16, 5))

        # Waveform mini-player if playing
        if self.is_playing:
            t = pygame.time.get_ticks() / 150.0
            for b in range(3):
                bar_h = int(4 + 5 * abs(math.sin(t + b * 1.1)))
                bx = (NATIVE_WIDTH // 2) - 6 + (b * 5)
                by = 16 - bar_h
                pygame.draw.rect(self.screen_buffer, COLOR_AMBER, (bx, by, 3, bar_h), border_radius=1)

        bat_x, bat_y = NATIVE_WIDTH - 36, 7
        pygame.draw.rect(self.screen_buffer, COLOR_TEXT_MUTED, (bat_x, bat_y, 18, 9), 1, border_radius=2)
        pygame.draw.rect(self.screen_buffer, COLOR_TEXT_MUTED, (bat_x + 18, bat_y + 2, 2, 5))
        pygame.draw.rect(self.screen_buffer, COLOR_AMBER, (bat_x + 2, bat_y + 2, 13, 5), border_radius=1)

    def render_home_orbit(self):
        """Screen 1: Stationary Circular Hub with Morphing Track Highlighter."""
        center_x = NATIVE_WIDTH // 2
        center_y = 148
        orbit_radius = 80
        total_nodes = len(HUB_ITEMS)
        step_angle = 2 * math.pi / total_nodes

        # 1. Base Circular Borderline Track connecting all nodes
        pygame.draw.circle(self.screen_buffer, (35, 42, 54), (center_x, center_y), orbit_radius, 2)

        # 2. Calculate animation state: distance to target node
        diff_to_target = abs((self.target_highlight_angle - self.highlight_angle + math.pi) % (2 * math.pi) - math.pi)
        transit_norm = min(1.0, diff_to_target / step_angle)
        
        # transit_factor: 0.0 at nodes, 1.0 mid-track
        transit_factor = math.sin(math.pi * transit_norm)

        # Calculate highlighter size based on transit
        # At node: R = 23px (big ring). In transit: shrinks to R = 7px (bead along the borderline)
        hl_radius = 23.0 - (16.0 * (transit_factor ** 0.8))
        aura_radius = hl_radius + 4.0 if transit_factor < 0.4 else hl_radius + 2.0

        # Highlighter position on the orbit track
        hl_x = center_x + orbit_radius * math.cos(self.highlight_angle)
        hl_y = center_y + orbit_radius * math.sin(self.highlight_angle)

        # Draw glowing connection trail along the border wire ONLY between Circle 1 and Circle 2
        diff_from_dep = (self.highlight_angle - self.departure_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(diff_from_dep) > 0.03 and transit_factor > 0.05:
            num_pts = 16
            trail_pts = []
            for k in range(num_pts + 1):
                frac = k / float(num_pts)
                th = self.departure_angle + diff_from_dep * frac
                tx = center_x + orbit_radius * math.cos(th)
                ty = center_y + orbit_radius * math.sin(th)
                trail_pts.append((tx, ty))
            
            if len(trail_pts) >= 2:
                pygame.draw.lines(self.screen_buffer, COLOR_AMBER, False, trail_pts, 3)

        # 3. Draw 6 Stationary Orbit Nodes in fixed clock positions
        for i, item in enumerate(HUB_ITEMS):
            fixed_angle = i * step_angle - (math.pi / 2)
            nx = center_x + orbit_radius * math.cos(fixed_angle)
            ny = center_y + orbit_radius * math.sin(fixed_angle)

            is_target = (i == self.selected_hub_index)
            # Nodes stay parked; target node glows brighter as highlighter arrives
            if is_target:
                arrival_glow = 1.0 - transit_factor
                node_r = int(16 + 4 * arrival_glow)
                # Subtle amber glow ring around target node
                pygame.draw.circle(self.screen_buffer, (int(60 * arrival_glow), int(35 * arrival_glow), 0), (int(nx), int(ny)), node_r + 3)
                node_color = (
                    int(24 + (COLOR_AMBER[0] - 24) * arrival_glow),
                    int(29 + (COLOR_AMBER[1] - 29) * arrival_glow),
                    int(36 + (COLOR_AMBER[2] - 36) * arrival_glow),
                )
                text_color = (0, 0, 0) if arrival_glow > 0.7 else COLOR_TEXT_WHITE
            else:
                node_r = 16
                node_color = COLOR_CARD
                text_color = COLOR_TEXT_MUTED

            # Node bubble
            pygame.draw.circle(self.screen_buffer, node_color, (int(nx), int(ny)), node_r)
            pygame.draw.circle(self.screen_buffer, COLOR_DIVIDER, (int(nx), int(ny)), node_r, 1)

            # Draw icon: Use image if linked, otherwise fallback to letter
            icon_img = self.icons.get(item["id"])
            if icon_img:
                icon_size = 24 if is_target else 19
                scaled_icon = pygame.transform.smoothscale(icon_img, (icon_size, icon_size))
                self.screen_buffer.blit(scaled_icon, (int(nx) - icon_size // 2, int(ny) - icon_size // 2))
            else:
                icon_surf = self.font_mid.render(item["icon"], True, text_color)
                self.screen_buffer.blit(
                    icon_surf, 
                    (int(nx) - icon_surf.get_width() // 2, int(ny) - icon_surf.get_height() // 2)
                )

        # 4. Draw the Morphing Highlighter (Bead on the line -> Big Pop-up Ring at Node)
        if transit_factor > 0.3:
            # Traveling along the wire: sleek solid glowing bead with inner bright core
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER_DARK, (int(hl_x), int(hl_y)), int(aura_radius))
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (int(hl_x), int(hl_y)), int(hl_radius))
            pygame.draw.circle(self.screen_buffer, (255, 255, 230), (int(hl_x), int(hl_y)), max(2, int(hl_radius - 3)))
        else:
            # Arrived at node: Pop-up glowing amber halo ring enclosing the node
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER_DARK, (int(hl_x), int(hl_y)), int(aura_radius), 2)
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (int(hl_x), int(hl_y)), int(hl_radius), 2)

        # 5. Center Hub Circle (Selected menu info)
        selected_item = HUB_ITEMS[self.selected_hub_index]
        pygame.draw.circle(self.screen_buffer, (20, 24, 30), (center_x, center_y), 40)
        pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (center_x, center_y), 40, 2)

        hub_text = self.font_tiny.render(selected_item["title"], True, COLOR_AMBER)
        self.screen_buffer.blit(
            hub_text, 
            (center_x - hub_text.get_width() // 2, center_y - hub_text.get_height() // 2)
        )

        # 6. Footer Hint
        hint = self.font_tiny.render("ROTATE TO SELECT", True, (80, 90, 105))
        self.screen_buffer.blit(hint, (center_x - hint.get_width() // 2, NATIVE_HEIGHT - 18))

    def render_shuffle_orbit(self):
        """Smart Shuffle Radial Orbit Screen."""
        center_x, center_y, orbit_radius = NATIVE_WIDTH // 2, 148, 80
        total_nodes = len(SHUFFLE_ITEMS)
        step_angle = 2 * math.pi / total_nodes

        # Header label
        hdr = self.font_tiny.render("SMART SHUFFLE", True, COLOR_TEXT_MUTED)
        self.screen_buffer.blit(hdr, (center_x - hdr.get_width() // 2, 26))

        pygame.draw.circle(self.screen_buffer, (35, 42, 54), (center_x, center_y), orbit_radius, 2)

        diff_to_target = abs((self.target_highlight_angle - self.highlight_angle + math.pi) % (2 * math.pi) - math.pi)
        transit_factor = math.sin(math.pi * min(1.0, diff_to_target / step_angle))
        hl_radius = 23.0 - (16.0 * (transit_factor ** 0.8))
        hl_x = center_x + orbit_radius * math.cos(self.highlight_angle)
        hl_y = center_y + orbit_radius * math.sin(self.highlight_angle)

        diff_from_dep = (self.highlight_angle - self.departure_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(diff_from_dep) > 0.03 and transit_factor > 0.05:
            trail_pts = [
                (
                    center_x + orbit_radius * math.cos(self.departure_angle + diff_from_dep * (k / 15.0)),
                    center_y + orbit_radius * math.sin(self.departure_angle + diff_from_dep * (k / 15.0)),
                )
                for k in range(16)
            ]
            pygame.draw.lines(self.screen_buffer, COLOR_AMBER, False, trail_pts, 3)

        for i, item in enumerate(SHUFFLE_ITEMS):
            ang = i * step_angle - (math.pi / 2)
            nx, ny = center_x + orbit_radius * math.cos(ang), center_y + orbit_radius * math.sin(ang)
            is_target = (i == self.shuffle_index)
            node_r = int(16 + 4 * (1.0 - transit_factor)) if is_target else 16
            node_color = COLOR_AMBER if (is_target and transit_factor < 0.25) else COLOR_CARD
            text_color = (0, 0, 0) if (is_target and transit_factor < 0.25) else COLOR_TEXT_MUTED

            pygame.draw.circle(self.screen_buffer, node_color, (int(nx), int(ny)), node_r)
            pygame.draw.circle(self.screen_buffer, COLOR_DIVIDER, (int(nx), int(ny)), node_r, 1)
            icon_surf = self.font_mid.render(item["icon"], True, text_color)
            self.screen_buffer.blit(icon_surf, (int(nx) - icon_surf.get_width() // 2, int(ny) - icon_surf.get_height() // 2))

        if transit_factor > 0.3:
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (int(hl_x), int(hl_y)), int(hl_radius))
        else:
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (int(hl_x), int(hl_y)), int(hl_radius), 2)

        selected = SHUFFLE_ITEMS[self.shuffle_index]
        pygame.draw.circle(self.screen_buffer, (20, 24, 30), (center_x, center_y), 40)
        pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (center_x, center_y), 40, 2)
        hub_text = self.font_tiny.render(selected["title"], True, COLOR_AMBER)
        self.screen_buffer.blit(hub_text, (center_x - hub_text.get_width() // 2, center_y - hub_text.get_height() // 2))

    def render_music_menu(self):
        """Music Library Sub-Menu (Vertical List)."""
        header_surf = self.font_mid.render("Music Library", True, COLOR_AMBER)
        self.screen_buffer.blit(header_surf, (26, 28))

        row_y = 54
        row_height = 32
        for i, item in enumerate(MUSIC_MENU_ITEMS):
            is_selected = (i == self.music_menu_index)
            pill_rect = pygame.Rect(10, row_y, NATIVE_WIDTH - 20, row_height - 4)
            if is_selected:
                pygame.draw.rect(self.screen_buffer, COLOR_AMBER, pill_rect, border_radius=6)
                t_col, s_col = (0, 0, 0), (40, 40, 40)
            else:
                t_col, s_col = COLOR_TEXT_WHITE, COLOR_TEXT_MUTED

            self.screen_buffer.blit(self.font_small.render(item["title"], True, t_col), (18, row_y + 2))
            self.screen_buffer.blit(self.font_tiny.render(item["subtitle"], True, s_col), (18, row_y + 15))
            row_y += row_height

    def render_file_screen(self):
        """File Browser Sub-Menu (Vertical List)."""
        header_surf = self.font_mid.render("File (SD)", True, COLOR_AMBER)
        self.screen_buffer.blit(header_surf, (26, 28))

        row_y = 54
        row_height = 32
        for i, item in enumerate(FILE_ITEMS):
            is_selected = (i == self.file_index)
            pill_rect = pygame.Rect(10, row_y, NATIVE_WIDTH - 20, row_height - 4)
            if is_selected:
                pygame.draw.rect(self.screen_buffer, COLOR_AMBER, pill_rect, border_radius=6)
                t_col, s_col = (0, 0, 0), (40, 40, 40)
            else:
                t_col, s_col = COLOR_TEXT_WHITE, COLOR_TEXT_MUTED

            self.screen_buffer.blit(self.font_small.render(item["title"], True, t_col), (18, row_y + 2))
            self.screen_buffer.blit(self.font_tiny.render(item["subtitle"], True, s_col), (18, row_y + 15))
            row_y += row_height

    def render_bt_screen(self):
        """Bluetooth Sub-Menu (Vertical List)."""
        header_surf = self.font_mid.render("Bluetooth", True, COLOR_AMBER)
        self.screen_buffer.blit(header_surf, (26, 28))

        row_y = 54
        row_height = 32
        for i, item in enumerate(BT_DEVICES):
            is_selected = (i == self.bt_index)
            pill_rect = pygame.Rect(10, row_y, NATIVE_WIDTH - 20, row_height - 4)
            if is_selected:
                pygame.draw.rect(self.screen_buffer, COLOR_AMBER, pill_rect, border_radius=6)
                t_col, s_col = (0, 0, 0), (40, 40, 40)
            else:
                t_col, s_col = COLOR_TEXT_WHITE, COLOR_TEXT_MUTED

            subtitle = item["subtitle"]
            if item["id"] == "bt_pwr":
                subtitle = "ON" if self.bt_enabled else "OFF"
            elif item["title"] == self.bt_connected and self.bt_enabled:
                subtitle = "CONNECTED"

            self.screen_buffer.blit(self.font_small.render(item["title"], True, t_col), (18, row_y + 2))
            self.screen_buffer.blit(self.font_tiny.render(subtitle, True, s_col), (18, row_y + 15))
            row_y += row_height

    def render_settings_screen(self):
        """Settings Sub-Menu (Vertical List)."""
        header_surf = self.font_mid.render("Settings", True, COLOR_AMBER)
        self.screen_buffer.blit(header_surf, (26, 28))

        rows = [
            ("< Back", "Return to Home"),
            ("Auto Brightness", "ON (LDR)" if self.auto_brightness else "OFF (Manual)"),
            ("Haptic Click", "ON (Haptic)" if self.haptic_click else "OFF"),
            ("EQ Preset", EQ_PRESETS[self.eq_index]),
            ("Sleep Timer", SLEEP_OPTIONS[self.sleep_index]),
        ]

        row_y = 54
        row_height = 32
        for i, (title, val) in enumerate(rows):
            is_selected = (i == self.settings_index)
            pill_rect = pygame.Rect(10, row_y, NATIVE_WIDTH - 20, row_height - 4)
            if is_selected:
                pygame.draw.rect(self.screen_buffer, COLOR_AMBER, pill_rect, border_radius=6)
                t_col, s_col = (0, 0, 0), (40, 40, 40)
            else:
                t_col, s_col = COLOR_TEXT_WHITE, COLOR_TEXT_MUTED

            self.screen_buffer.blit(self.font_small.render(title, True, t_col), (18, row_y + 2))
            self.screen_buffer.blit(self.font_tiny.render(val, True, s_col), (18, row_y + 15))
            row_y += row_height 

    def render_alpha_orbit(self):
        center_x, center_y, orbit_radius = NATIVE_WIDTH // 2, 148, 80
        nodes = ALPHA_PAGES[self.alpha_page]
        step_angel = 2 * math.pi / 6

        hdr = self.font_tiny.render(f"JUMP A-Z ({self.alpha_page + 1}/7)", True, COLOR_TEXT_MUTED)
        self.screen_buffer.blit(hdr, (center_x - hdr.get_width() // 2, 26))

        pygame.draw.circle(self.screen_buffer, (35, 42, 54), (center_x, center_y), orbit_radius, 2)

        diff_to_target = abs((self.target_highlight_angle - self.highlight_angle + math.pi) % (2 * math.pi) - math.pi)
        transit_factor = math.sin(math.pi * min(1.0, diff_to_target / step_angel))
        hl_radius = 23.0 - (16.0 * (transit_factor ** 0.8))
        hl_x = center_x + orbit_radius * math.cos(self.highlight_angle)
        hl_y = center_y + orbit_radius * math.sin(self.highlight_angle)

        diff_from_dep = (self.highlight_angle - self.departure_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(diff_from_dep) > 0.03 and transit_factor > 0.05:
            trail_pts = [
                (
                    center_x + orbit_radius * math.cos(self.departure_angle + diff_from_dep * (k / 15.0)),
                    center_y + orbit_radius * math.sin(self.departure_angle + diff_from_dep * (k / 15.0)),
                )
                for k in range(16)
            ]
            pygame.draw.lines(self.screen_buffer, COLOR_AMBER, False, trail_pts, 3)

        for i, label in enumerate(nodes):
            ang = i * step_angel - (math.pi / 2)
            nx, ny = center_x + orbit_radius * math.cos(ang), center_y + orbit_radius * math.sin(ang)
            is_target = (i == self.alpha_node_index)
            node_r = int(16 + 4 * (1.0 - transit_factor)) if is_target else 16
            node_color = COLOR_AMBER if (is_target and transit_factor < 0.25) else COLOR_CARD
            text_color = (0, 0, 0) if (is_target and transit_factor < 0.25) else COLOR_TEXT_MUTED

            pygame.draw.circle(self.screen_buffer, node_color, (int(nx), int(ny)), node_r)
            pygame.draw.circle(self.screen_buffer, COLOR_DIVIDER, (int(nx), int(ny)), node_r, 1)
            short_lbl = "<" if label == "BACK" else label
            txt = self.font_tiny.render(short_lbl, True, text_color)
            self.screen_buffer.blit(txt, (int(nx) - txt.get_width() // 2, int(ny) - txt.get_height() // 2))

        if transit_factor > 0.3:
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (int(hl_x), int(hl_y)), int(hl_radius))
        else:
            pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (int(hl_x), int(hl_y)), int(hl_radius), 2)

        selected = nodes[self.alpha_node_index]
        pygame.draw.circle(self.screen_buffer, (20, 24, 30), (center_x, center_y), 40)
        pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (center_x, center_y), 40, 2)
        hub_text = self.font_mid.render(selected, True, COLOR_AMBER)
        self.screen_buffer.blit(hub_text, (center_x - hub_text.get_width() // 2, center_y - hub_text.get_height() // 2))

    def render_song_list(self):
        """Screen 2: Clean Vertical Song Browser."""
        # Header
        header_surf = self.font_mid.render("Tracks (A-Z)", True, COLOR_AMBER)
        self.screen_buffer.blit(header_surf, (26, 28))

        row_y = 52
        row_height = 32
        visible_rows = 6
        visible_tracks = SAMPLE_TRACKS[self.list_scroll_offset:self.list_scroll_offset + visible_rows]

        for idx, track in enumerate(visible_tracks):
            actual_i = self.list_scroll_offset + idx
            is_selected = (actual_i == self.selected_song_index)
            pill_rect = pygame.Rect(10, row_y, NATIVE_WIDTH - 28, row_height - 4)

            if is_selected:
                pygame.draw.rect(self.screen_buffer, COLOR_AMBER, pill_rect, border_radius=6)
                title_color ,  artist_color = (0, 0, 0) ,(40, 40, 40)
               
            else:
                title_color ,artist_color = COLOR_TEXT_WHITE , COLOR_TEXT_MUTED
            
            self.screen_buffer.blit(self.font_small.render(track["title"], True, title_color), (18, row_y + 2))
            self.screen_buffer.blit(self.font_tiny.render(track["artist"], True, artist_color), (18, row_y + 15))
            row_y += row_height

        if len(SAMPLE_TRACKS) > visible_rows:
            sb_x, sb_y, sb_h = NATIVE_WIDTH - 12, 56, visible_rows * row_height - 8
            pygame.draw.rect(self.screen_buffer, (30, 36, 46), (sb_x, sb_y, 3, sb_h), border_radius=2)
            thumb_h = max(14, int(sb_h * (visible_rows / len(SAMPLE_TRACKS))))
            max_scroll = len(SAMPLE_TRACKS) - visible_rows
            thumb_y = sb_y + int((sb_h - thumb_h) * (self.list_scroll_offset / max_scroll))
            pygame.draw.rect(self.screen_buffer, COLOR_AMBER, (sb_x, thumb_y, 3, thumb_h), border_radius=2)
                
    def render_now_playing(self):
        """Screen 3: The Now Playing Crown Jewel."""
        center_x = NATIVE_WIDTH // 2

        # Header Title
        hdr = self.font_tiny.render("NOW PLAYING", True, COLOR_AMBER)
        self.screen_buffer.blit(hdr, (center_x - hdr.get_width() // 2, 26))

        # Album Art Card (Square 110x110)
        art_rect = pygame.Rect(center_x - 55, 46, 110, 110)
        pygame.draw.rect(self.screen_buffer, (30, 36, 46), art_rect, border_radius=12)
        pygame.draw.rect(self.screen_buffer, (60, 70, 85), art_rect, 1, border_radius=12)

        # Vinyl center disc decoration
        

        pygame.draw.circle(self.screen_buffer, (18, 22, 28), (center_x, 101), 36)
        pygame.draw.circle(self.screen_buffer,(45,52,65), (center_x,101),26,1)
        for s in range(2):
            ang = self.vinyl_angle + s * math.pi
            sx = center_x + int(30 * math.cos(ang))
            sy = 101 + int(30 * math.sin(ang))
            pygame.draw.line(self.screen_buffer,COLOR_AMBER_DARK ,(center_x,101) , (sx,sy),2)
            pygame.draw.circle(self.screen_buffer,COLOR_AMBER,(center_x ,101), 7)

        # Track Title & Artist
        title_surf = self.font_mid.render(self.current_track["title"], True, COLOR_TEXT_WHITE)
        self.screen_buffer.blit(title_surf, (center_x - title_surf.get_width() // 2, 164))

        artist_surf = self.font_small.render(self.current_track["artist"], True, COLOR_TEXT_MUTED)
        self.screen_buffer.blit(artist_surf, (center_x - artist_surf.get_width() // 2, 182))

        # Scrubber Timeline Bar
        bar_x = 24
        bar_y = 205
        bar_w = NATIVE_WIDTH - 48
        pygame.draw.rect(self.screen_buffer, (35, 42, 52), (bar_x, bar_y, bar_w, 4), border_radius=2)

        progress = self.playback_time / float(self.current_track["duration"])
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            pygame.draw.rect(self.screen_buffer, COLOR_AMBER, (bar_x, bar_y, fill_w, 4), border_radius=2)
            pygame.draw.circle(self.screen_buffer, COLOR_TEXT_WHITE, (bar_x + fill_w, bar_y + 2), 4)

        # Time labels
        cur_m, cur_s = divmod(int(self.playback_time), 60)
        tot_m, tot_s = divmod(int(self.current_track["duration"]), 60)
        t_left = self.font_tiny.render(f"{cur_m:02d}:{cur_s:02d}", True, COLOR_TEXT_MUTED)
        t_right = self.font_tiny.render(f"{tot_m:02d}:{tot_s:02d}", True, COLOR_TEXT_MUTED)
        self.screen_buffer.blit(t_left, (bar_x, bar_y + 8))
        self.screen_buffer.blit(t_right, (bar_x + bar_w - t_right.get_width(), bar_y + 8))

        # Play / Pause & Volume footer
        state_icon = "PAUSED" if not self.is_playing else "PLAYING"
        ctrl_text = self.font_tiny.render(f"[{state_icon}]  •  VOL {self.volume}%", True, COLOR_AMBER)
        self.screen_buffer.blit(ctrl_text, (center_x - ctrl_text.get_width() // 2, 234))

if __name__ == "__main__":
    app = MyPodSimulator()
    app.run()
