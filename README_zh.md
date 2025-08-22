# 黑荊棘角鬥場：重鑄版 存檔修改器（JSON）

<!-- Replace OWNER with your GitHub username if you want repo-linked badges -->
<p align="left">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg">
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue">
  <img alt="OS" src="https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-informational">
  <img alt="UI" src="https://img.shields.io/badge/UI-tkinter-blueviolet">
  <img alt="Release" src="https://img.shields.io/badge/release-v1.0.0-brightgreen">
</p>

**特色**
- 繁中介面，亮/暗主題、斑馬紋表格、搜尋高亮、欄位可排序、字體/行高放大、介面縮放（100/125/150%）  
- 篩選：只顯示玩家隊伍（預設 team==0）、只顯示名字含 `_`、最小等級、關鍵字搜尋  
- 批次編輯：等級、`potentialPoint`、`skillPoint`、`livingSkillPoint`（加值 ± 或 設值 =）  
- 全局屬性：金錢（`wealth`）、聲望（`reputation`）  
- 自動備份：儲存時在原始 `sav.dat` 旁建立 `.bak.YYYYMMDD-HHMMSS`

---

## 快速開始
```bash
python src/blackthorn_arena_reforged_save_editor_zh.py
```
> 若在 Linux 缺少 tkinter：`sudo apt-get install python3-tk`。

### 存檔路徑（Windows / Steam 範例）
```
C:\Users\<你>\AppData\LocalLow\PersonaeGames\BlackthornArena Reforged\Save\ArenaMode\<玩家名稱>\SaveData\
```

## 打包為 .exe（選用）
```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/blackthorn_arena_reforged_save_editor_zh.py
```

## 建議使用方式（避免太 OP）
- 先以「加值(±)」小幅調整（每人 +5～+10），等級一次 +1～+2。  
- 儲存會自動備份，不喜歡就還原。

## 授權
MIT
