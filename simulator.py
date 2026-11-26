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

# -------------------------------------------------------------
# 1. HARDWARE & DISPLAY CONSTANTS
# -------------------------------------------------------------
NATIVE_WIDTH = 240
NATIVE_HEIGHT = 280
CORNER_RADIUS = 43     # 4-R5 mm = ~43px on 0.1165mm pitch

SCALE = 2.5            # Scale factor for comfortable desktop viewing
WINDOW_WIDTH = int(NATIVE_WIDTH * SCALE) + 80   # Extra margin for wooden chassis frame
WINDOW_HEIGHT = int(NATIVE_HEIGHT * SCALE) + 80

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

SAMPLE_TRACKS = [
    {"title": "Midnight City", "artist": "M83", "duration": 243},
    {"title": "Get Lucky", "artist": "Daft Punk", "duration": 248},
    {"title": "Resonance", "artist": "HOME", "duration": 212},
    {"title": "Starboy", "artist": "The Weeknd", "duration": 230},
    {"title": "After Dark", "artist": "Mr.Kitty", "duration": 257},
    {"title": "Blinding Lights", "artist": "The Weeknd", "duration": 200},
    {"title": "Nightcall", "artist": "Kavinsky", "duration": 259},
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
        self.font_small = pygame.font.SysFont("segoeui,helvetica,arial", 10)
        self.font_tiny  = pygame.font.SysFont("segoeui,helvetica,arial", 8, bold=True)

        # State Machine
        self.current_screen = "HOME_ORBIT"   # "HOME_ORBIT", "SONG_LIST", "NOW_PLAYING"
        self.selected_hub_index = 0
        self.highlight_angle = -math.pi / 2  # Current angle of the highlighter (starts at top, -90 deg)
        self.target_highlight_angle = -math.pi / 2
        self.departure_angle = -math.pi / 2  # The circle angle we are traveling FROM
        
        # Song list state
        self.selected_song_index = 0
        self.list_scroll_offset = 0
        
        # Playback state
        self.current_track = SAMPLE_TRACKS[0]
        self.is_playing = True
        self.playback_time = 45.0
        self.volume = 75

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
        self.mask_surface.fill((0, 0, 0, 255))
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
        if key in (pygame.K_DOWN, pygame.K_RIGHT):
            self.on_rotate_clockwise()
        elif key in (pygame.K_UP, pygame.K_LEFT):
            self.on_rotate_counter_clockwise()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.on_center_click()
        elif key in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
            self.on_back_click()

    def on_rotate_clockwise(self):
        if self.current_screen == "HOME_ORBIT":
            self.departure_angle = self.highlight_angle
            self.selected_hub_index = (self.selected_hub_index + 1) % len(HUB_ITEMS)
            self.target_highlight_angle = self.selected_hub_index * (2 * math.pi / len(HUB_ITEMS)) - (math.pi / 2)
        elif self.current_screen == "SONG_LIST":
            if self.selected_song_index < len(SAMPLE_TRACKS) - 1:
                self.selected_song_index += 1
        elif self.current_screen == "NOW_PLAYING":
            self.volume = min(100, self.volume + 5)

    def on_rotate_counter_clockwise(self):
        if self.current_screen == "HOME_ORBIT":
            self.departure_angle = self.highlight_angle
            self.selected_hub_index = (self.selected_hub_index - 1) % len(HUB_ITEMS)
            self.target_highlight_angle = self.selected_hub_index * (2 * math.pi / len(HUB_ITEMS)) - (math.pi / 2)
        elif self.current_screen == "SONG_LIST":
            if self.selected_song_index > 0:
                self.selected_song_index -= 1
        elif self.current_screen == "NOW_PLAYING":
            self.volume = max(0, self.volume - 5)

    def on_center_click(self):
        if self.current_screen == "HOME_ORBIT":
            selected_id = HUB_ITEMS[self.selected_hub_index]["id"]
            if selected_id == "music":
                self.current_screen = "SONG_LIST"
            elif selected_id == "now_playing":
                self.current_screen = "NOW_PLAYING"
            elif selected_id == "shuffle":
                self.selected_song_index = 0
                self.current_screen = "NOW_PLAYING"
        elif self.current_screen == "SONG_LIST":
            self.current_track = SAMPLE_TRACKS[self.selected_song_index]
            self.playback_time = 0.0
            self.is_playing = True
            self.current_screen = "NOW_PLAYING"
        elif self.current_screen == "NOW_PLAYING":
            self.is_playing = not self.is_playing

    def on_back_click(self):
        if self.current_screen == "SONG_LIST":
            self.current_screen = "HOME_ORBIT"
        elif self.current_screen == "NOW_PLAYING":
            self.current_screen = "HOME_ORBIT"

    def update(self):
        # Smooth interpolation for highlighter angle (shortest angular distance)
        diff = (self.target_highlight_angle - self.highlight_angle + math.pi) % (2 * math.pi) - math.pi
        self.highlight_angle += diff * 0.28

        # Increment playback timer
        if self.is_playing and self.current_screen == "NOW_PLAYING":
            self.playback_time = min(float(self.current_track["duration"]), self.playback_time + 1/60)

    # ---------------------------------------------------------
    # RENDERING ENGINE
    # ---------------------------------------------------------
    def render(self):
        # 1. Clear native buffer
        self.screen_buffer.fill(COLOR_BG)

        # 2. Render active screen content
        if self.current_screen == "HOME_ORBIT":
            self.render_home_orbit()
        elif self.current_screen == "SONG_LIST":
            self.render_song_list()
        elif self.current_screen == "NOW_PLAYING":
            self.render_now_playing()

        # 3. Render Status Bar on top
        self.render_status_bar()

        # 4. Apply 43px rounded corners mask
        # We fill outside the mask with bezel color
        bezel_masked = self.screen_buffer.copy()
        
        # 5. Blit to main desktop window with scale and chassis
        self.window.fill(COLOR_CHASSIS)
        
        # Scaled LCD display (crisp pixel-sharp scaling without bilinear blur)
        scaled_lcd = pygame.transform.scale(
            self.screen_buffer, 
            (int(NATIVE_WIDTH * SCALE), int(NATIVE_HEIGHT * SCALE))
        )
        
        # Position centered inside wooden chassis
        screen_x = (WINDOW_WIDTH - scaled_lcd.get_width()) // 2
        screen_y = (WINDOW_HEIGHT - scaled_lcd.get_height()) // 2
        
        # Glass bezel border
        bezel_rect = pygame.Rect(
            screen_x - 6, screen_y - 6, 
            scaled_lcd.get_width() + 12, scaled_lcd.get_height() + 12
        )
        pygame.draw.rect(self.window, COLOR_BEZEL, bezel_rect, border_radius=int(CORNER_RADIUS * SCALE) + 4)
        
        self.window.blit(scaled_lcd, (screen_x, screen_y))

        # Instructions banner at bottom
        hint = self.font_small.render("Turn Wheel / Arrow Keys • Click Enter / Space • Back: Backspace", True, (160, 140, 120))
        self.window.blit(hint, ((WINDOW_WIDTH - hint.get_width()) // 2, WINDOW_HEIGHT - 28))

        pygame.display.flip()

    def render_status_bar(self):
        """Top 22px Status Bar: Clock, Animated Waveform, Battery."""
        pygame.draw.line(self.screen_buffer, COLOR_DIVIDER, (0, 22), (NATIVE_WIDTH, 22), 1)

        # Time
        time_surf = self.font_small.render("12:45", True, COLOR_TEXT_MUTED)
        self.screen_buffer.blit(time_surf, (14, 5))

        # Waveform mini-player if playing
        if self.is_playing:
            wf = self.font_tiny.render("ılı", True, COLOR_AMBER)
            self.screen_buffer.blit(wf, (NATIVE_WIDTH // 2 - wf.get_width() // 2, 6))

        # Battery & BT
        bat_surf = self.font_small.render("92% [BT]", True, COLOR_TEXT_MUTED)
        self.screen_buffer.blit(bat_surf, (NATIVE_WIDTH - bat_surf.get_width() - 14, 5))

    def render_home_orbit(self):
        """Screen 1: Stationary Circular Hub with Morphing Track Highlighter."""
        center_x = NATIVE_WIDTH // 2
        center_y = 150
        orbit_radius = 65
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
        # At node: R = 19px (big ring). In transit: shrinks to R = 6px (bead along the borderline)
        hl_radius = 19.0 - (13.0 * (transit_factor ** 0.8))
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
                node_r = int(13 + 3 * arrival_glow)
                # Subtle amber glow ring around target node
                pygame.draw.circle(self.screen_buffer, (int(60 * arrival_glow), int(35 * arrival_glow), 0), (int(nx), int(ny)), node_r + 3)
                node_color = (
                    int(24 + (COLOR_AMBER[0] - 24) * arrival_glow),
                    int(29 + (COLOR_AMBER[1] - 29) * arrival_glow),
                    int(36 + (COLOR_AMBER[2] - 36) * arrival_glow),
                )
                text_color = (0, 0, 0) if arrival_glow > 0.7 else COLOR_TEXT_WHITE
            else:
                node_r = 13
                node_color = COLOR_CARD
                text_color = COLOR_TEXT_MUTED

            # Node bubble
            pygame.draw.circle(self.screen_buffer, node_color, (int(nx), int(ny)), node_r)
            pygame.draw.circle(self.screen_buffer, COLOR_DIVIDER, (int(nx), int(ny)), node_r, 1)

            # Draw icon: Use image if linked, otherwise fallback to letter
            icon_img = self.icons.get(item["id"])
            if icon_img:
                icon_size = 20 if is_target else 16
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
        pygame.draw.circle(self.screen_buffer, (20, 24, 30), (center_x, center_y), 32)
        pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (center_x, center_y), 32, 2)

        hub_text = self.font_tiny.render(selected_item["title"], True, COLOR_AMBER)
        self.screen_buffer.blit(
            hub_text, 
            (center_x - hub_text.get_width() // 2, center_y - hub_text.get_height() // 2)
        )

        # 6. Footer Hint
        hint = self.font_tiny.render("ROTATE TO SELECT", True, (80, 90, 105))
        self.screen_buffer.blit(hint, (center_x - hint.get_width() // 2, NATIVE_HEIGHT - 22))

    def render_song_list(self):
        """Screen 2: Clean Vertical Song Browser."""
        # Header
        header_surf = self.font_mid.render("Tracks (A-Z)", True, COLOR_AMBER)
        self.screen_buffer.blit(header_surf, (14, 28))

        row_y = 52
        row_height = 30
        visible_rows = 7

        for i, track in enumerate(SAMPLE_TRACKS):
            is_selected = (i == self.selected_song_index)
            pill_rect = pygame.Rect(10, row_y, NATIVE_WIDTH - 20, row_height - 4)

            if is_selected:
                pygame.draw.rect(self.screen_buffer, COLOR_AMBER, pill_rect, border_radius=6)
                title_color = (0, 0, 0)
                artist_color = (40, 40, 40)
            else:
                title_color = COLOR_TEXT_WHITE
                artist_color = COLOR_TEXT_MUTED

            # Track Title
            title_surf = self.font_small.render(track["title"], True, title_color)
            self.screen_buffer.blit(title_surf, (18, row_y + 2))

            # Artist
            artist_surf = self.font_tiny.render(track["artist"], True, artist_color)
            self.screen_buffer.blit(artist_surf, (18, row_y + 14))

            row_y += row_height

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
        pygame.draw.circle(self.screen_buffer, (18, 22, 28), (center_x, 101), 24)
        pygame.draw.circle(self.screen_buffer, COLOR_AMBER, (center_x, 101), 6)

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
