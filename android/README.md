# 📱 Pro Mutual Fund Analytics — Native Android App (Option 1)

This folder contains the complete, production-ready **Native Android Studio project** for the **Pro Mutual Fund Analytics** dashboard.

---

## 🚀 Key Features

- **⚡ Hardware Accelerated WebView**: Chart.js graphs, Monte Carlo simulations, portfolio rebalancing, and comparisons render at a smooth 60 FPS.
- **🔄 Native Pull-To-Refresh**: Uses Android's `SwipeRefreshLayout` with theme-matching cyan and purple accents.
- **📡 Dynamic Server URL Switcher**: Seamlessly switch between local Wi-Fi development (`http://192.168.1.18:5000/dashboard`) and your deployed cloud URL (e.g., Render, Railway, AWS, DigitalOcean) directly inside the app without rebuilding the APK!
- **🌐 Offline & Reconnection Handling**: Shows a sleek dark-themed error screen with **"Retry Connection"** and **"Change Server URL"** if the server is temporarily unreachable.
- **🔙 Smart Hardware Back Button**: Navigates through tab history inside the app; prompts "Press back again to exit" when at the home screen to prevent accidental closures.
- **🎨 Custom App Icon & Dark Status Bar**: Seamless dark slate `#0A0F1E` matching the web theme.

---

## 🛠️ How to Build the APK

### Method 1: Android Studio (Recommended — 2 Minutes)
1. Open **Android Studio**.
2. Click **File > Open...** (or "Open" on the welcome screen).
3. Select the `android` folder:
   ```
   c:\Users\v2spl_p5nx879\Downloads\mftool-master\android
   ```
4. Wait a moment for Gradle to sync dependencies automatically.
5. In the top menu, go to:
   **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
6. Once compiled, a notification will pop up in the bottom right corner with a **"locate"** link.
7. Click **"locate"** to find your compiled `app-debug.apk`!

---

### Method 2: One-Click Build Script (`build_apk.bat`)
If you have Java JDK (17+) or Android Studio installed on your computer:
1. Double-click [`build_apk.bat`](file:///c:/Users/v2spl_p5nx879/Downloads/mftool-master/android/build_apk.bat).
2. The script will automatically detect your JDK/SDK, download the Gradle wrapper if needed, and compile the APK.
3. The ready-to-install file `ProMutualFund-Analytics.apk` will appear right in the `android/` folder.

---

## 📲 Installing on Your Android Phone

1. Transfer `app-debug.apk` (or `ProMutualFund-Analytics.apk`) to your Android phone via:
   - **USB Cable** (copy to Phone Storage / Downloads)
   - **Google Drive** / **Dropbox**
   - **WhatsApp** / **Telegram** (send file to yourself)
2. On your phone, tap the `.apk` file to install.
3. If prompted with *"For your security, your phone is not allowed to install unknown apps from this source"*:
   - Tap **Settings**.
   - Toggle **Allow from this source** to **ON**.
   - Tap **Install**.

---

## 🌐 Connecting Phone to Your Computer's Server

### When Testing Locally over Wi-Fi:
1. Make sure your PC and Android phone are connected to the **same Wi-Fi router / hotspot**.
2. Keep your Flask server running on your PC:
   ```bash
   python app.py
   ```
3. Open the app on your phone. It defaults to:
   ```
   http://192.168.1.18:5000/dashboard
   ```
4. If your PC's IP address ever changes (e.g. after restarting router):
   - In the app's error screen, tap **"Change Server URL"**.
   - Enter your updated IP, e.g.: `http://192.168.1.XX:5000/dashboard` and tap **Save & Connect**.

### When Testing over the Internet (Cloud Deployment):
- If you deploy your Flask backend to **Render**, **Railway**, or **PythonAnywhere**, simply tap **"Change Server URL"** in the app and enter your live URL (e.g. `https://my-mf-analytics.up.railway.app/dashboard`).
- Your app will now work anywhere in the world on 4G/5G mobile data!
