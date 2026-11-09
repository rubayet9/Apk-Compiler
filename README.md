# APK Compiler ⚡

A modern, high-performance desktop application for Windows that converts **HTML5 Web Applications** and **Google AI Studio exports** into production-ready, signed Android APK packages.

Built with Python, CustomTkinter, and automated Android build toolchains.

---

## ✨ Features

- **Obsidian Glass Design System:** Premium frosted glass aesthetic with senior UI/UX layout standards, responsive scaling, and zero color gradients.
- **Bilingual Interface:** Instant real-time toggle between **English** and **Bengali (বাংলা)**.
- **Crash-Proof Drag & Drop:** Native 64-bit Windows shell drag-and-drop integration for directories and `.zip` archives.
- **Google AI Studio & Web App Support:**
  - Converts HTML5/CSS/JavaScript web applications using a native Android WebView wrapper.
  - Directly builds native Kotlin Jetpack Compose export packages from Google AI Studio.
- **High-Performance Compilation:**
  - Automated Gradle toolchain with multi-threaded parallel execution (`--parallel`).
  - Persistent Gradle build cache (`--build-cache`).
  - Optimized JVM heap and garbage collection tuning.
- **Automated Toolchain Management:** Built-in discovery and support for bundled OpenJDK 17 and Android SDK build tools.
- **Signing & Zipalign:** Automatic debug/release keystore generation, v1/v2 APK signature verification, and zipalign optimization.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ (64-bit recommended)
- Java Development Kit (JDK 17+)
- Android SDK (build-tools & platform 34/36)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rubayet9/Apk-Compiler.git
   cd Apk-Compiler
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python main.py
   ```

---

## 🛠️ Building Standalone Executable (.exe)

To build a standalone Windows distribution with PyInstaller:

```bash
python build.py
```

The output executable will be created at:
```
dist/APK Compiler/APK Compiler.exe
```

---

## 📄 License

This project is open-source and available under the MIT License.
