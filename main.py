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

# --- Config ---
V_WIDTH, V_HEIGHT = 800, 500
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
            if os.path.exists(file):
                try:
                    self.sounds[key] = pygame.mixer.Sound(file)
                except:
                    pass

    def start_music(self):
        if self.music_playing:
            return
        if os.path.exists("background.mp3"):
            try:
                pygame.mixer.music.load("background.mp3")
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
            self.x = V_WIDTH
            self.y = random.randint(0, V_HEIGHT)
    def draw(self, surf):
        pygame.draw.circle(surf, (200, 200, 255), (int(self.x), int(self.y)), self.size)

class Ball:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x, self.y = V_WIDTH // 2, V_HEIGHT // 2
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
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
        pygame.display.set_caption("PIXEL PONG")
        self.icon = None
        if os.path.exists("icon.png"):
            try:
                self.icon = pygame.image.load("icon.png")
                pygame.display.set_icon(self.icon)
            except:
                pass
        self.game_surf = pygame.Surface((V_WIDTH, V_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("orbitron,segoeui,arial", 32, bold=True)
        self.font_big = pygame.font.SysFont("orbitron,segoeui,arial", 110, bold=True)
        self.font_mid = pygame.font.SysFont("orbitron,segoeui,arial", 64, bold=True)
        
        self.highscore = load_highscore()
        self.state = "MENU"
        self.game_mode = 0
        self.difficulty = 1
        self.theme = "NEON"
        self.modes = ["SINGLE PLAYER", "LOCAL VERSUS", "CHAOS MODE"]
        self.diffs = ["NOVICE", "ELITE", "INSANE"]
        self.theme_list = list(THEMES.keys())
        self.draw_rect = pygame.Rect(0, 0, V_WIDTH, V_HEIGHT)
        self.stars = [Star() for _ in range(120)]
        self.particles = []
        self.btns = {
            "START": pygame.Rect(V_WIDTH//2-160, 260, 320, 70),
            "SETTINGS": pygame.Rect(V_WIDTH//2-160, 350, 320, 70),
            "RESTART": pygame.Rect(V_WIDTH//2-160, 380, 320, 70),
            "GITHUB": pygame.Rect(V_WIDTH - 150, V_HEIGHT - 50, 130, 40)
        }
        self.tick = 0
        self.reset_game()

    def update_scaling(self):
        tr = V_WIDTH / V_HEIGHT
        sr = self.screen_w / self.screen_h
        if sr > tr:
            nh = self.screen_h
            nw = int(nh * tr)
        else:
            nw = self.screen_w
            nh = int(nw / tr)
        self.draw_rect = pygame.Rect((self.screen_w - nw)//2, (self.screen_h - nh)//2, nw, nh)

    def reset_game(self):
        self.p1_y, self.p2_y = V_HEIGHT//2-50, V_HEIGHT//2-50
        self.score, self.lives, self.level = 0, 3, 1
        self.balls = [Ball()]
        if self.game_mode == 2:
            self.balls.append(Ball())
        self.bricks, self.shake, self.super_meter = [], 0, 0
        self.load_level()

    def load_level(self):
        self.bricks = []
        cols, rows = 3 + (self.level // 2), 7
        for c in range(cols):
            for r in range(rows):
                exp = random.random() < 0.1
                self.bricks.append({"rect": pygame.Rect(V_WIDTH//2-(cols*35)//2+c*35, 90+r*45, 28, 35), "active": True, "exp": exp})

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
        rw, rh = self.draw_rect.width, self.draw_rect.height
        rel_m = ((mx - self.draw_rect.x) * (V_WIDTH / rw), (my - self.draw_rect.y) * (V_HEIGHT / rh))
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self.screen_w, self.screen_h = event.size
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.update_scaling()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) if self.screen.get_flags() & pygame.FULLSCREEN == 0 else pygame.display.set_mode((V_WIDTH, V_HEIGHT), pygame.RESIZABLE)
                    self.screen_w, self.screen_h = self.screen.get_size()
                    self.update_scaling()
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
            elif self.state == "SETTINGS":
                if rel_m[1] > 410:
                    self.state = "MENU"
                    self.audio.play("button")
                elif 100 < rel_m[1] < 170:
                    self.game_mode = (self.game_mode + 1) % len(self.modes)
                    self.audio.play("button")
                elif 175 < rel_m[1] < 245:
                    self.difficulty = (self.difficulty + 1) % len(self.diffs)
                    self.audio.play("button")
                elif 250 < rel_m[1] < 320:
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
        dm, ai = [0.8, 1.1, 1.5][self.difficulty], [0.06, 0.1, 0.15][self.difficulty]
        keys = pygame.key.get_pressed()
        u = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_i]
        d = keys[pygame.K_s] or keys[pygame.K_DOWN] or keys[pygame.K_k]
        if u:
            self.p1_y -= 8
        if d:
            self.p1_y += 8
        self.p1_y = max(0, min(V_HEIGHT-100, self.p1_y))
        if self.game_mode == 0:
            t = self.balls[0].y-50 if self.balls else V_HEIGHT//2
            self.p2_y += (t - self.p2_y) * ai
        else:
            if keys[pygame.K_UP]:
                self.p2_y -= 8
            if keys[pygame.K_DOWN]:
                self.p2_y += 8
        self.p2_y = max(0, min(V_HEIGHT-100, self.p2_y))
        if self.shake > 0:
            self.shake -= 1
        self.super_meter = min(100, self.super_meter + 0.1)

        for b in self.balls[:]:
            b.update(dm)
            if b.y < b.radius or b.y > V_HEIGHT-b.radius:
                b.vy *= -1
                self.shake = 3
                self.audio.play("wall")
            p1_r, p2_r, b_r = pygame.Rect(30, self.p1_y, 14, 100), pygame.Rect(V_WIDTH-44, self.p2_y, 14, 100), pygame.Rect(b.x-12, b.y-12, 24, 24)
            if b_r.colliderect(p1_r) and b.vx < 0:
                b.vx *= -1.1
                b.x = 44
                self.shake = 6
                b.charged = False
                self.audio.play("paddle")
            elif b_r.colliderect(p2_r) and b.vx > 0:
                b.vx *= -1.1
                b.x = V_WIDTH-44-24
                self.shake = 6
                self.audio.play("paddle")
            for br in self.bricks:
                if br["active"] and b_r.colliderect(br["rect"]):
                    br["active"] = False
                    self.score += 10
                    self.audio.play("brick")
                    if not b.charged:
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
            elif b.x > V_WIDTH:
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
        for y in range(V_HEIGHT):
            f = y / V_HEIGHT
            c = [int(t["bg_top"][i] * (1-f) + t["bg_bot"][i] * f) for i in range(3)]
            pygame.draw.line(self.game_surf, c, (0, y), (V_WIDTH, y))
        for s in self.stars:
            s.draw(self.game_surf)
        for p in self.particles:
            p.draw(self.game_surf)
        
        mx, my = pygame.mouse.get_pos()
        rw, rh = self.draw_rect.width, self.draw_rect.height
        rel_m = ((mx - self.draw_rect.x) * (V_WIDTH / rw), (my - self.draw_rect.y) * (V_HEIGHT / rh))
        
        if self.state == "PLAY":
            for br in self.bricks:
                if br["active"]:
                    pygame.draw.rect(self.game_surf, t["accent"] if br["exp"] else t["p2"], br["rect"], border_radius=6)
                    pygame.draw.rect(self.game_surf, WHITE, br["rect"], 2, border_radius=6)
            so = (random.randint(-self.shake, self.shake), random.randint(-self.shake, self.shake)) if self.shake > 0 else (0, 0)
            pygame.draw.rect(self.game_surf, t["p1"], (30+so[0], self.p1_y+so[1], 16, 100), border_radius=10)
            pygame.draw.rect(self.game_surf, t["p2"], (V_WIDTH-46+so[0], self.p2_y+so[1], 16, 100), border_radius=10)
            for b in self.balls:
                b.draw(self.game_surf, self.theme)
            self.draw_txt(self.game_surf, f"SCORE: {self.score}", self.font, WHITE, (100, 40))
            self.draw_txt(self.game_surf, f"LIVES: {self.lives}", self.font, RED, (V_WIDTH-100, 40))
        elif self.state == "MENU":
            y_off = math.sin(self.tick * 0.04) * 15
            for i in range(12):
                alpha = 70 - i * 5
                self.draw_txt(self.game_surf, "PIXEL PONG", self.font_big, (*t["glow"], alpha), (V_WIDTH//2, 130 + y_off))
            self.draw_txt(self.game_surf, "PIXEL PONG", self.font_big, WHITE, (V_WIDTH//2, 130 + y_off))
            if self.icon:
                ic = pygame.transform.smoothscale(self.icon, (100, 100))
                self.game_surf.blit(ic, (V_WIDTH//2-50, 185 + y_off))
            self.draw_glass_btn(self.game_surf, self.btns["START"], "ENTER GAME", t["p1"], self.btns["START"].collidepoint(rel_m))
            self.draw_glass_btn(self.game_surf, self.btns["SETTINGS"], "GAME SETUP", t["p1"], self.btns["SETTINGS"].collidepoint(rel_m))
            gh_hover = self.btns["GITHUB"].collidepoint(rel_m)
            gh_c = t["p1"] if gh_hover else (150, 150, 170)
            pygame.draw.rect(self.game_surf, (30, 30, 40), self.btns["GITHUB"], border_radius=8)
            pygame.draw.rect(self.game_surf, gh_c, self.btns["GITHUB"], 2, border_radius=8)
            self.draw_txt(self.game_surf, "GitHub", self.font, gh_c, self.btns["GITHUB"].center)
        elif self.state == "SETTINGS":
            self.draw_txt(self.game_surf, "GAME SETUP", self.font_mid, WHITE, (V_WIDTH//2, 60))
            opts = [("MODE", self.modes[self.game_mode]), ("DIFF", self.diffs[self.difficulty]), ("THEME", self.theme), ("CONTROLS", "ALL KEYS")]
            for i, (l, v) in enumerate(opts):
                y = 135 + i * 75
                hover = y-32 < rel_m[1] < y+32
                self.draw_glass_btn(self.game_surf, pygame.Rect(60, y-32, 680, 64), f"{l} | {v}", t["p1"], hover)
            back_r = pygame.Rect(V_WIDTH//2-110, 430, 220, 55)
            self.draw_glass_btn(self.game_surf, back_r, "BACK", t["p1"], back_r.collidepoint(rel_m))
        elif self.state == "OVER":
            self.draw_txt(self.game_surf, "GAME OVER", self.font_big, RED, (V_WIDTH//2, 180))
            self.draw_txt(self.game_surf, f"SCORE: {self.score}", self.font_mid, WHITE, (V_WIDTH//2, 300))
            self.draw_glass_btn(self.game_surf, self.btns["RESTART"], "RETRY", RED, self.btns["RESTART"].collidepoint(rel_m))


        
        self.screen.fill(BLACK)
        scaled = pygame.transform.smoothscale(self.game_surf, (self.draw_rect.width, self.draw_rect.height))
        self.screen.blit(scaled, (self.draw_rect.x, self.draw_rect.y))
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
