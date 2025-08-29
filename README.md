# Executable Combiner (Educational Tool)

⚠️ **Disclaimer:**  
This project is provided **for educational and research purposes only**.  
It demonstrates how to bundle two executable files into a single distributable package using Python and PyInstaller.  
Do **not** use this tool for malicious purposes. The authors take **no responsibility** for misuse.  

By keeping this project **open, transparent, and responsibly documented**, it avoids confusion with malware-like tools.

---

## 📌 Overview
The Executable Combiner is a Python-based desktop tool with a modern Tkinter interface.  
It allows you to select two `.exe` files:

- **Primary Executable (Visible):** Runs normally and visibly to the user.  
- **Secondary Executable (Background):** Runs silently in the background (intended for helper utilities, updaters, or supporting tools).  

The tool then packages them into a single distributable `.exe` using **PyInstaller**.

---

## ✨ Features
- Modern Tkinter UI with dark theme  
- File selection dialogs for executables  
- Progress log panel with status updates  
- Auto-installs PyInstaller if missing  
- Cross-platform support (Windows/Linux)  

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/executable-combiner.git
cd executable-combiner
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the Tool
```bash
python executable-combiner.py
```

---

## 🛠️ Requirements

> Python 3.8+

> Tkinter (included with most Python installs)

> PyInstaller

---

## 📜 License

Distributed under the MIT License. See LICENSE for more information.

---

## ⚠️ Legal Notice

This repository is not intended for malicious use.
Possible legitimate use cases include:

> Bundling an installer + updater

> Packaging a main app + helper tool

> Educational demonstrations of PyInstaller
