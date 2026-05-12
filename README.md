# PIXEL PONG: The Arcade Masterpiece 🕹️

**Pixel Pong** is a premium, high-octane reimagining of the classic Pong experience. Built with **Python** and **Pygame-CE**, it combines nostalgic arcade vibes with modern visual effects, responsive design, and deep gameplay mechanics.

Developed with passion by **Subhan Haider**.

---

## ✨ Key Features

### 🌈 Next-Gen Visuals
- **Premium Aesthetics:** Vibrant gradients, neon glow effects, and sleek glassmorphism UI.
- **Particle Engine:** Interactive particle systems for button hovers, hits, and explosions.
- **Smooth Animations:** Floating menu titles and screen-shake effects for high-impact collisions.

### 🎮 Enhanced Gameplay
- **Super Meter:** Charge up your energy and press `Left Shift` to unleash a **Charged Attack** that smashes through bricks!
- **Dynamic Bricks:** Destructible bricks in the center of the field with occasional explosive variants.
- **Three Game Modes:**
  - **Single Player:** Face off against a balanced, human-like AI.
  - **Local Versus:** Competitive 1v1 action on a single keyboard.
  - **Chaos Mode:** Double the balls, double the madness!

### ⚙️ Intelligent Systems
- **Responsive Resolution:** Full support for any window size or aspect ratio. The game dynamically repositions all elements to fill your screen—no black bars!
- **Balanced AI:** Our AI features built-in reaction delays and tracking errors, making it challenging but beatable and "human-like."
- **Pause & Resume:** Full control with a dedicated pause menu (`ESC` or `P`).

---

## 🛠️ Installation

1. **Prerequisites:** Ensure you have Python 3.10 or higher installed.
2. **Dependencies:** We recommend using `pygame-ce` for the best performance and feature support.
   ```bash
   pip install pygame-ce
   ```

---

## 🚀 How to Play

1. Run the game:
   ```bash
   python main.py
   ```
2. Navigate the menu with your mouse.
3. Choose your **Level** (Easy, Medium, Hard) and **Theme** in Game Setup.

---

## ⌨️ Controls

| Action | Control |
| :--- | :--- |
| **Move Player 1** | `W` / `S` |
| **Move Player 2** | `Up` / `Down` or `I` / `K` |
| **Super Attack** | `Left Shift` (at 100% meter) |
| **Pause Game** | `ESC` or `P` |
| **Toggle Fullscreen** | `F` |
| **Navigate Menus** | Mouse (Left Click) |

---

## 📂 Project Structure
```text
ping-pong/
├── main.py              # Main game engine and logic
├── highscore.json       # Persistent high score data (auto-generated)
├── README.md            # Comprehensive project documentation
├── icon.png             # Game window icon (optional)
├── background.mp3       # Game soundtrack (optional)
└── *.mp3                # SFX assets (optional fallbacks included)
```

---

## 🛠️ Troubleshooting

- **Sound Issues:** If the game fails to play custom MP3s, it will automatically fall back to its internal synthesized audio engine.
- **Performance:** Ensure you are using `pygame-ce` instead of the standard `pygame` for the smoothest 120 FPS experience.
- **Window Size:** If the window looks small, press `F` to toggle Fullscreen or simply drag the window corners to resize.

---

## 🗺️ Roadmap
- [ ] **Online Multiplayer:** Global matchmaking using WebSockets.
- [ ] **Character Skins:** Unlockable paddle designs and trail effects.
- [ ] **Boss Battles:** Massive AI opponents with unique abilities.
- [ ] **Mobile Port:** Porting the engine to Android/iOS using Kivy or PyTM.

---

## ⚖️ License
This project is open-source and available under the **MIT License**. Feel free to fork, modify, and share!

---
*Created with ❤️ by Subhan Haider using Python and Pygame-CE*
