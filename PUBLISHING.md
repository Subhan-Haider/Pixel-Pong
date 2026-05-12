# Publishing to the Microsoft Store 🚀

To get **Pixel Pong** onto the Microsoft Store, you will need to follow these steps. This guide will help you prepare your game for a professional release.

---

## 1. 🔑 Create a Developer Account
Before you can upload anything, you need a Microsoft Developer Account.
- **Where:** [Microsoft Partner Center](https://partner.microsoft.com/dashboard)
- **Cost:** A one-time registration fee (approx. $19 USD for individuals).
- **Setup:** Once registered, create a new app submission and reserve the name **"Pixel Pong"**.

---

## 2. 📦 Create an MSIX Package
The Microsoft Store requires apps to be in the **MSIX** format. Since we have a `PixelPong.exe`, the easiest way is to use the **MSIX Packaging Tool**.

1. **Download:** Get the [MSIX Packaging Tool](https://apps.microsoft.com/store/detail/msix-packaging-tool/9N5LW3JBCXKF) from the Microsoft Store.
2. **Launch:** Open the tool and select **"Application package"**.
3. **Installer:** Point it to your `dist/PixelPong.exe`.
4. **Metadata:** Use the information from the **Store Metadata** section below.
5. **Sign:** You will need a code-signing certificate (or use a test certificate for the initial package).

---

## 📝 Store Metadata (Ready to Copy)

### App Name
`Pixel Pong: Arcade Masterpiece`

### Short Description
`A premium, high-octane reimagining of the classic Pong experience with stunning neon visuals and explosive arcade action.`

### Full Description
`Step into the neon-drenched world of Pixel Pong! This isn't your grandfather's ping pong.

Pixel Pong is a high-fidelity arcade engine built for speed, style, and satisfaction. Whether you're fighting for a high score against our advanced adaptive AI or challenging a friend in Local Versus mode, every hit feels electric.

Key Features:
- Stunning Glassmorphism UI & Particle Effects.
- Three Game Modes: Single Player, Local Versus, and Chaos Mode.
- Super Meter: Build up energy to unleash a high-speed Charged Attack!
- Dynamic Resolution: Perfect full-screen support for any monitor.
- Adaptive AI: A challenging but fair opponent that learns your moves.
- Multiple Themes: Switch between Neon, Emerald, and Sunset aesthetics.`

### Keywords
`Pong, Arcade, Retro, Neon, Local Multiplayer, Casual, Indie Game, Pixel Art, Action.`

---

## 📸 Screenshots & Assets
Microsoft Store requires specific image sizes:
- **Store Logo:** 50x50 png
- **Square 44x44 Logo:** 44x44 png
- **Square 150x150 Logo:** 150x150 png
- **Wide 310x150 Logo:** 310x150 png
- **Square 71x71 Logo:** 71x71 png
- **Screenshots:** At least 4 screenshots (1920x1080 recommended).

---

## 🧪 App Certification (WACK)
Before uploading, run the **Windows App Certification Kit (WACK)** on your MSIX package. It will check for:
- Performance issues.
- Security vulnerabilities.
- API compliance.

Once your package passes WACK, upload it to the Partner Center and hit **Submit**! 🏁
