'''
PIXEL PONG - THE ARCADE MASTERPIECE EDITION V2
Vibrant Gradients, Electric UI, and Immersive Atmosphere.
'''

import pygame
import random
import math
import json
import os
import array
import time
import webbrowser
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Config ---
V_WIDTH, V_HEIGHT = 1280, 800
FPS = 120
SAVE_FILE = "highscore.json"

# Themes
THEMES = {
    "NEON": {"bg_top": (5, 5, 20), "bg_bot": (10, 10, 40), "p1": (0, 255, 255), "p2": (255, 0, 255), "accent": (255, 255, 0), "glow": (0, 150, 255)},
    "EMERALD": {"bg_top": (2, 10, 2), "bg_bot": (5, 30, 5), "p1": (0, 255, 120), "p2": (180, 255, 50), "accent": (255, 255, 255), "glow": (0, 200, 100)},
    "SUNSET": {"bg_top": (15, 5, 5), "bg_bot": (40, 10, 10), "p1": (255, 80, 0), "p2": (255, 200, 0), "accent": (255, 50, 100), "glow": (255, 100, 0)}
}

WHITE, BLACK, DARK_GRAY, RED = (250, 250, 255), (2, 2, 8), (30, 30, 45), (255, 40, 40)

# --- Audio Engine ---
class AudioEngine:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2)
        self.sounds = {}
        self._generate_fallbacks()
        self._load_custom_assets()
        self.music_playing = False

    def _tone(self, freq, dur):
        sr = 22050
        n = int(sr * dur)
        buf = array.array('h', [int(16384 * math.sin(2.0 * math.pi * freq * (float(i)/sr))) for i in range(n)])
        return pygame.mixer.Sound(buffer=buf)

    def _generate_fallbacks(self):
        self.sounds = {
            "paddle": self._tone(440, 0.1),
            "wall": self._tone(220, 0.05),
            "brick": self._tone(660, 0.08),
            "score": self._tone(880, 0.15),
            "powerup": self._tone(1100, 0.2),
            "game_over": self._tone(330, 0.5),
            "explosion": self._tone(100, 0.3),
            "button": self._tone(500, 0.05),
            "start": self._tone(800, 0.2),
            "close": self._tone(200, 0.2)
        }

    def _load_custom_assets(self):
        mapping = {"game over.mp3": "game_over", "ball hit.mp3": "paddle", "menu button.mp3": "button", "start game.mp3": "start", "game close.mp3": "close"}
        for file, key in mapping.items():
            path = resource_path(file)
            if os.path.exists(path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(path)
                except:
                    pass

    def start_music(self):
        if self.music_playing:
            return
        bg_path = resource_path("background.mp3")
        if os.path.exists(bg_path):
            try:
                pygame.mixer.music.load(bg_path)
                pygame.mixer.music.play(-1)
                self.music_playing = True
                return
            except:
                pass
        sr = 22050
        dur = 4.0
        n = int(sr * dur)
        buf = array.array('h', [0] * n)
        for i in range(n):
            t = float(i) / sr
            k = math.sin(2.0 * math.pi * 60 * math.exp(-15 * (t % 0.5))) * 8000 if (t % 0.5) < 0.15 else 0
            buf[i] = int(k + math.sin(2.0 * math.pi * 80 * t) * 3000)
        pygame.mixer.Sound(buffer=buf).play(-1)
        self.music_playing = True

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

# --- Utility ---
def load_highscore():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f).get("highscore", 0)
        except:
            return 0
    return 0

def save_highscore(s):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump({"highscore": s}, f)
    except:
        pass

# --- Game Objects ---
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-1, 1), random.uniform(-1, 1)
        self.life = 1.0
        self.color = color
        self.size = random.randint(2, 4)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.02
    def draw(self, surf):
        if self.life > 0:
            a = int(self.life * 255)
            pygame.draw.circle(surf, (*self.color, a), (int(self.x), int(self.y)), self.size)

class Star:
    def __init__(self):
        self.x, self.y = random.randint(0, V_WIDTH), random.randint(0, V_HEIGHT)
        self.speed = random.uniform(0.2, 0.8)
        self.size = random.randint(1, 4)
    def update(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = pygame.display.get_surface().get_width()
            self.y = random.randint(0, pygame.display.get_surface().get_height())
    def draw(self, surf):
        pygame.draw.circle(surf, (200, 200, 255), (int(self.x), int(self.y)), self.size)

class Ball:
    def __init__(self):
        self.reset()
    def reset(self):
        surf = pygame.display.get_surface()
        w, h = surf.get_size() if surf else (1280, 800)
        self.x, self.y = w // 2, h // 2
        self.vx, self.vy = 5 * random.choice([-1, 1]), random.uniform(-3, 3)
        self.radius = 12
        self.trail = []
        self.charged = False
    def update(self, m=1.0):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 25:
            self.trail.pop(0)
        self.x += self.vx * m
        self.y += self.vy * m
    def draw(self, surf, theme):
        t = THEMES[theme]
        c = t["accent"] if self.charged else t["p1"]
        for i, pos in enumerate(self.trail):
            f = i / len(self.trail)
            r = int(self.radius * 0.8 * f)
            if r > 0:
                pygame.draw.circle(surf, c, (int(pos[0]), int(pos[1])), r)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.radius, 4)

class Game:
    def __init__(self):
        pygame.init()
        self.audio = AudioEngine()
        self.screen_w, self.screen_h = V_WIDTH, V_HEIGHT
        self.screen = pygame.display.set_mode((V_WIDTH, V_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("PIXEL PONG")
        self.icon = None
        icon_path = resource_path("icon.png")
        if os.path.exists(icon_path):
            try:
                self.icon = pygame.image.load(icon_path)
                pygame.display.set_icon(self.icon)
            except:
                pass
        self.game_surf = pygame.Surface((V_WIDTH, V_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("orbitron,segoeui,arial", 44, bold=True)
        self.font_small = pygame.font.SysFont("orbitron,segoeui,arial", 28, bold=True)
        self.font_big = pygame.font.SysFont("orbitron,segoeui,arial", 160, bold=True)
        self.font_mid = pygame.font.SysFont("orbitron,segoeui,arial", 90, bold=True)
        
        self.highscore = load_highscore()
        self.state = "MENU"
        self.game_mode = 0
        self.difficulty = 1
        self.w, self.h = V_WIDTH, V_HEIGHT
        self.theme = "NEON"
        self.modes = ["SINGLE PLAYER", "LOCAL VERSUS", "CHAOS MODE"]
        self.diffs = ["EASY", "MEDIUM", "HARD"]
        self.theme_list = list(THEMES.keys())
        self.update_scaling()
        self.stars = [Star() for _ in range(120)]
        self.particles = []
        self.update_btns()
        self.tick = 0
        self.reset_game()

    def update_btns(self):
        self.btns = {
            "START": pygame.Rect(self.w//2-220, 420, 440, 90),
            "SETTINGS": pygame.Rect(self.w//2-220, 540, 440, 90),
            "RESTART": pygame.Rect(self.w//2-220, 580, 440, 90),
            "GITHUB": pygame.Rect(self.w - 160, self.h - 60, 130, 42),
            "EXIT": pygame.Rect(30, self.h - 60, 130, 42),
            "RESUME": pygame.Rect(self.w//2-220, self.h//2-100, 440, 90),
            "QUIT": pygame.Rect(self.w//2-220, self.h//2+20, 440, 90)
        }

    def update_scaling(self):
        self.w, self.h = self.screen.get_size()
        self.game_surf = pygame.Surface((self.w, self.h))
        self.update_btns()

    def reset_game(self):
        self.p1_y, self.p2_y = self.h//2-75, self.h//2-75
        self.score, self.lives, self.level = 0, 3, 1
        self.balls = [Ball()]
        if self.game_mode == 2:
            self.balls.append(Ball())
        self.bricks, self.shake, self.super_meter = [], 0, 0
        self.load_level()

    def load_level(self):
        self.bricks = []
        cols, rows = 3 + (self.level // 2), 9
        bw, bh, gap = 36, 46, 6
        total_w = cols * (bw + gap)
        for c in range(cols):
            for r in range(rows):
                exp = random.random() < 0.1
                bx = self.w//2 - total_w//2 + c * (bw + gap)
                by = 130 + r * (bh + gap)
                self.bricks.append({"rect": pygame.Rect(bx, by, bw, bh), "active": True, "exp": exp})

    def run(self):
        self.audio.start_music()
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.audio.play("close")
        time.sleep(0.5)
        pygame.quit()

    def handle_input(self):
        mx, my = pygame.mouse.get_pos()
        # With pygame.SCALED, mouse coords are already in virtual space
        rel_m = (mx, my)
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                # Let pygame.SCALED handle the scaling, just update internal size trackers
                self.screen_w, self.screen_h = event.size
                self.update_scaling()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    flags = self.screen.get_flags()
                    if flags & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode((V_WIDTH, V_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
                    else:
                        self.screen = pygame.display.set_mode((V_WIDTH, V_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if self.state == "PLAY":
                        self.state = "PAUSE"
                        self.audio.play("button")
                    elif self.state == "PAUSE":
                        self.state = "PLAY"
                        self.audio.play("button")
                if self.state == "MENU":
                    self.state = "PLAY"
                    self.reset_game()
                    self.audio.play("start")
                elif self.state == "OVER":
                    self.state = "MENU"
                    self.audio.play("button")
                elif self.state == "PLAY" and event.key == pygame.K_LSHIFT and self.super_meter >= 100:
                    self.activate_super()

        if click:
            if self.state == "MENU":
                if self.btns["START"].collidepoint(rel_m):
                    self.state = "PLAY"
                    self.reset_game()
                    self.audio.play("start")
                elif self.btns["SETTINGS"].collidepoint(rel_m):
                    self.state = "SETTINGS"
                    self.audio.play("button")
                elif self.btns["GITHUB"].collidepoint(rel_m):
                    webbrowser.open("https://github.com/Subhan-Haider")
                    self.audio.play("button")
                elif self.btns["EXIT"].collidepoint(rel_m):
                    return False
            elif self.state == "PAUSE":
                if self.btns["RESUME"].collidepoint(rel_m):
                    self.state = "PLAY"
                    self.audio.play("button")
                elif self.btns["QUIT"].collidepoint(rel_m):
                    self.state = "MENU"
                    self.audio.play("button")
            elif self.state == "SETTINGS":
                if rel_m[1] > 660:
                    self.state = "MENU"
                    self.audio.play("button")
                elif 155 < rel_m[1] < 245:
                    self.game_mode = (self.game_mode + 1) % len(self.modes)
                    self.audio.play("button")
                elif 275 < rel_m[1] < 365:
                    self.difficulty = (self.difficulty + 1) % len(self.diffs)
                    self.audio.play("button")
                elif 395 < rel_m[1] < 485:
                    self.theme = self.theme_list[(self.theme_list.index(self.theme) + 1) % len(self.theme_list)]
                    self.audio.play("powerup")
            elif self.state == "OVER":
                if self.btns["RESTART"].collidepoint(rel_m):
                    self.state = "MENU"
                    self.audio.play("button")
        return True

    def activate_super(self):
        self.super_meter = 0
        self.shake = 30
        self.audio.play("powerup")
        for b in self.balls:
            b.charged = True
            b.vx *= 2

    def update(self):
        self.tick += 1
        for s in self.stars:
            s.update()
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
        if self.state != "PLAY":
            return
        dm, ai = [0.65, 0.95, 1.3][self.difficulty], [3, 6, 10][self.difficulty]
        keys = pygame.key.get_pressed()
        u = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_i]
        d = keys[pygame.K_s] or keys[pygame.K_DOWN] or keys[pygame.K_k]
        if u:
            self.p1_y -= 10
        if d:
            self.p1_y += 10
        self.p1_y = max(0, min(self.h-150, self.p1_y))

        if self.game_mode == 0:
            # AI tracking with reaction delay and increased error
            # Only update target every few frames to simulate reaction time
            delay = [15, 8, 3][self.difficulty]
            if self.tick % delay == 0:
                # Random error based on difficulty (Novice has more error)
                error_range = [80, 50, 25][self.difficulty]
                self.ai_error = random.randint(-error_range, error_range)
                self.ai_target = self.balls[0].y - 75 + self.ai_error if self.balls else self.h//2 - 75
            
            if not hasattr(self, 'ai_target'): self.ai_target = self.h//2 - 75
            
            dist = self.ai_target - self.p2_y
            if abs(dist) > ai:
                self.p2_y += ai if dist > 0 else -ai
            else:
                self.p2_y = self.ai_target
        else:
            if keys[pygame.K_UP]:
                self.p2_y -= 10
            if keys[pygame.K_DOWN]:
                self.p2_y += 10
        self.p2_y = max(0, min(self.h-150, self.p2_y))
        if self.shake > 0:
            self.shake -= 1
        self.super_meter = min(100, self.super_meter + 0.1)

        for b in self.balls[:]:
            b.update(dm)
            if b.y < b.radius:
                b.y = b.radius
                b.vy *= -1
                self.shake = 3
                self.audio.play("wall")
            elif b.y > self.h-b.radius:
                b.y = self.h-b.radius
                b.vy *= -1
                self.shake = 3
                self.audio.play("wall")
            
            p1_r = pygame.Rect(40, self.p1_y, 20, 150)
            p2_r = pygame.Rect(self.w-60, self.p2_y, 20, 150)
            b_r = pygame.Rect(b.x-14, b.y-14, 28, 28)
            
            if b_r.colliderect(p1_r) and b.vx < 0:
                b.vx *= -1.06
                b.x = p1_r.right + b.radius + 2
                self.shake = 6
                b.charged = False
                self.audio.play("paddle")
            elif b_r.colliderect(p2_r) and b.vx > 0:
                b.vx *= -1.06
                b.x = p2_r.left - b.radius - 2
                self.shake = 6
                self.audio.play("paddle")
            for br in self.bricks:
                if br["active"] and b_r.colliderect(br["rect"]):
                    br["active"] = False
                    self.score += 10
                    self.audio.play("brick")
                    if not b.charged:
                        # Move ball out of brick based on velocity
                        if b.vx > 0: b.x = br["rect"].left - b.radius
                        else: b.x = br["rect"].right + b.radius
                        b.vx *= -1
                    if br["exp"]:
                        self.detonate(br["rect"].center)
                        self.audio.play("explosion")
                        break
            if b.x < 0:
                self.balls.remove(b)
                self.audio.play("explosion")
                if not self.balls:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = "OVER"
                        self.audio.play("game_over")
                        if self.score > self.highscore:
                            self.highscore = self.score
                            save_highscore(self.score)
                    else:
                        self.balls = [Ball()]
            elif b.x > self.w:
                if self.game_mode == 0:
                    self.score += 100
                    b.reset()
                    self.audio.play("score")
                else:
                    self.balls.remove(b)
                    self.audio.play("score")
                    if not self.balls:
                        self.balls = [Ball()]
                        if self.game_mode == 2:
                            self.balls.append(Ball())
        if not any(br["active"] for br in self.bricks):
            self.level += 1
            self.load_level()
            self.audio.play("score")

    def detonate(self, pos):
        self.shake = 20
        for br in self.bricks:
            if br["active"] and math.hypot(br["rect"].centerx-pos[0], br["rect"].centery-pos[1]) < 100:
                br["active"] = False
                self.score += 5

    def draw_glass_btn(self, surf, rect, text, theme_p1, hover):
        off = 5 if hover else 0
        if hover:
            for _ in range(2):
                self.particles.append(Particle(rect.centerx + random.uniform(-100, 100), rect.centery + random.uniform(-20, 20), theme_p1))
        pygame.draw.rect(surf, (0, 0, 0, 150), rect.move(6, 6), border_radius=20)
        c = (*theme_p1, 100) if hover else (40, 40, 55, 200)
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, c, s.get_rect(), border_radius=20)
        pygame.draw.rect(s, theme_p1 if hover else (140, 140, 160), s.get_rect(), 4, border_radius=20)
        if hover:
            for i in range(1, 5):
                pygame.draw.rect(surf, (*theme_p1, 50-i*10), rect.inflate(i*6, i*6), 2, border_radius=20+i)
        surf.blit(s, rect.move(0, -off).topleft)
        self.draw_txt(surf, text, self.font, WHITE if hover else (220, 220, 240), rect.move(0, -off).center)

    def draw(self):
        t = THEMES[self.theme]
        for y in range(self.h):
            f = y / self.h
            c = [int(t["bg_top"][i] * (1-f) + t["bg_bot"][i] * f) for i in range(3)]
            pygame.draw.line(self.game_surf, c, (0, y), (self.w, y))
        for s in self.stars:
            s.draw(self.game_surf)
        for p in self.particles:
            p.draw(self.game_surf)
        
        mx, my = pygame.mouse.get_pos()
        rel_m = (mx, my) 
        
        if self.state == "PLAY":
            for br in self.bricks:
                if br["active"]:
                    pygame.draw.rect(self.game_surf, t["accent"] if br["exp"] else t["p2"], br["rect"], border_radius=6)
                    pygame.draw.rect(self.game_surf, WHITE, br["rect"], 2, border_radius=6)
            so = (random.randint(-self.shake, self.shake), random.randint(-self.shake, self.shake)) if self.shake > 0 else (0, 0)
            pygame.draw.rect(self.game_surf, t["p1"], (40+so[0], self.p1_y+so[1], 20, 150), border_radius=10)
            pygame.draw.rect(self.game_surf, t["p2"], (self.w-60+so[0], self.p2_y+so[1], 20, 150), border_radius=10)
            for b in self.balls:
                b.draw(self.game_surf, self.theme)
            self.draw_txt(self.game_surf, f"SCORE: {self.score}", self.font, WHITE, (150, 50))
            self.draw_txt(self.game_surf, f"LIVES: {self.lives}", self.font, RED, (self.w-150, 50))
        elif self.state == "MENU":
            y_off = math.sin(self.tick * 0.04) * 18
            for i in range(12):
                alpha = 70 - i * 5
                self.draw_txt(self.game_surf, "PIXEL PONG", self.font_big, (*t["glow"], alpha), (self.w//2, 200 + y_off))
            self.draw_txt(self.game_surf, "PIXEL PONG", self.font_big, WHITE, (self.w//2, 200 + y_off))
            if self.icon:
                ic = pygame.transform.smoothscale(self.icon, (130, 130))
                self.game_surf.blit(ic, (self.w//2-65, 300 + y_off))
            self.draw_glass_btn(self.game_surf, self.btns["START"], "ENTER GAME", t["p1"], self.btns["START"].collidepoint(rel_m))
            self.draw_glass_btn(self.game_surf, self.btns["SETTINGS"], "GAME SETUP", t["p1"], self.btns["SETTINGS"].collidepoint(rel_m))
            gh_hover = self.btns["GITHUB"].collidepoint(rel_m)
            gh_c = t["p1"] if gh_hover else (150, 150, 170)
            pygame.draw.rect(self.game_surf, (30, 30, 40), self.btns["GITHUB"], border_radius=6)
            pygame.draw.rect(self.game_surf, gh_c, self.btns["GITHUB"], 2, border_radius=6)
            self.draw_txt(self.game_surf, "GitHub", self.font_small, gh_c, self.btns["GITHUB"].center)
            
            ex_hover = self.btns["EXIT"].collidepoint(rel_m)
            ex_c = RED if ex_hover else (150, 150, 170)
            pygame.draw.rect(self.game_surf, (30, 30, 40), self.btns["EXIT"], border_radius=6)
            pygame.draw.rect(self.game_surf, ex_c, self.btns["EXIT"], 2, border_radius=6)
            self.draw_txt(self.game_surf, "EXIT", self.font_small, ex_c, self.btns["EXIT"].center)
        elif self.state == "SETTINGS":
            self.draw_txt(self.game_surf, "GAME SETUP", self.font_mid, WHITE, (self.w//2, 80))
            opts = [("MODE", self.modes[self.game_mode]), ("LEVEL", self.diffs[self.difficulty]), ("THEME", self.theme), ("CONTROLS", "ALL KEYS")]
            for i, (l, v) in enumerate(opts):
                y = 200 + i * 120
                hover = y-45 < rel_m[1] < y+45
                self.draw_glass_btn(self.game_surf, pygame.Rect(80, y-45, self.w-160, 90), f"{l} | {v}", t["p1"], hover)
            back_r = pygame.Rect(self.w//2-160, 690, 320, 80)
            self.draw_glass_btn(self.game_surf, back_r, "BACK", t["p1"], back_r.collidepoint(rel_m))
        elif self.state == "OVER":
            self.draw_txt(self.game_surf, "GAME OVER", self.font_big, RED, (self.w//2, 280))
            self.draw_txt(self.game_surf, f"SCORE: {self.score}", self.font_mid, WHITE, (self.w//2, 450))
            self.draw_glass_btn(self.game_surf, self.btns["RESTART"], "RETRY", RED, self.btns["RESTART"].collidepoint(rel_m))
        elif self.state == "PAUSE":
            # Draw game background but dim it
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.game_surf.blit(overlay, (0, 0))
            self.draw_txt(self.game_surf, "PAUSED", self.font_big, WHITE, (self.w//2, 180))
            self.draw_glass_btn(self.game_surf, self.btns["RESUME"], "RESUME", t["p1"], self.btns["RESUME"].collidepoint(rel_m))
            self.draw_glass_btn(self.game_surf, self.btns["QUIT"], "QUIT MENU", RED, self.btns["QUIT"].collidepoint(rel_m))
            
        self.screen.fill(BLACK)
        self.screen.blit(self.game_surf, (0, 0))
        pygame.display.flip()

    def draw_txt(self, s, t, f, c, p):
        if len(c) == 3:
            ts_shadow = f.render(t, 1, (0, 0, 0))
            tr_shadow = ts_shadow.get_rect(center=(p[0]+2, p[1]+2))
            s.blit(ts_shadow, tr_shadow)
            ts = f.render(t, 1, c)
        else:
            ts = f.render(t, 1, c[:3])
            ts.set_alpha(c[3])
        tr = ts.get_rect(center=p)
        s.blit(ts, tr)

if __name__ == "__main__":
    Game().run()
