# Blackthorn Arena: Reforged Save Editor (JSON)

<!-- Replace OWNER with your GitHub username if you want repo-linked badges -->
<p align="left">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg">
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue">
  <img alt="OS" src="https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-informational">
  <img alt="UI" src="https://img.shields.io/badge/UI-tkinter-blueviolet">
  <img alt="Release" src="https://img.shields.io/badge/release-v1.1.0-brightgreen">
</p>

**Highlights**
- Chinese UI (Traditional). Light/Dark theme, zebra table, search highlight, sortable headers, larger fonts/row height, UI scaling (100/125/150%).  
- Filters: player team only (default team==0), name contains `_`, minimum level, keyword search.  
- Bulk edit: level, `potentialPoint`, `skillPoint`, `livingSkillPoint`, base attributes (`BSstrength`, `BSendurance`, `BSagility`, `BSprecision`, `BSintelligence`, `BSwillpower`) (add ± or set =).
- Global fields: `wealth`, `reputation`.  
- Auto backup: `.bak.YYYYMMDD-HHMMSS` next to `sav.dat` when saving.

---

## Quick Start
```bash
python src/blackthorn_arena_reforged_save_editor.py
```

Linux may need tkinter via: `sudo apt-get install python3-tk`.

## Build Windows .exe (optional)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/blackthorn_arena_reforged_save_editor.py
```

## Tips (avoid overpowered edits)
- Start small with **Add (±)** (+5 to +10 per character), and +1~+2 levels at a time.  
- Backups are auto-created; revert anytime.

## License
MIT
