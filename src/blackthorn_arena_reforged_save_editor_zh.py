
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黑荊棘角鬥場：重鑄版 存檔修改器（繁中介面, 強化視覺）
作者：ChatGPT
用途：編輯 JSON 格式的存檔（通常為 sav.dat）

主要功能
- 讀取 / 顯示角鬥士名單（預設只顯示玩家隊伍 team==0，可切換「全部 NPC」）
- 搜尋、等級下限篩選、只看名字含底線 _ 的角色
- 批次編輯：等級 / 潛力點 potentialPoint / 技能點 skillPoint / 生活技能點 livingSkillPoint
- 全局屬性：金錢（wealth）、聲望（reputation）
- 視覺強化：字體放大、列間距加大、斑馬紋、關鍵字高亮、列頭可排序、亮/暗色主題
- 自動備份：儲存時會在原始檔旁建立 .bak.時間戳

免責：請先備份存檔，風險自負。
"""
import json
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ui_style import init_style, apply_palette as style_apply_palette

APP_TITLE = "黑荊棘角鬥場：重鑄版 存檔修改器（JSON）"
DEFAULT_FILENAME = "sav.dat"

# ---------- 工具 ----------
def safe_int(v, default=None):
    try:
        return int(v)
    except Exception:
        return default

# ---------- 資料模型 ----------
class SaveModel:
    def __init__(self):
        self.path = None
        self.data = None
        self.npcs = []
        self.gold_key = 'wealth'
        self.reputation_key = 'reputation'
        self.player_team = 0

    def load(self, path):
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.npcs = self.data.get('npcs', [])
        if not isinstance(self.npcs, list):
            self.npcs = []
        return True

    def save(self, out_path=None, make_backup=True):
        if self.data is None or self.path is None:
            raise RuntimeError("尚未載入存檔")
        src = self.path
        dst = out_path or self.path
        if make_backup and os.path.exists(src):
            ts = time.strftime("%Y%m%d-%H%M%S")
            backup = f"{src}.bak.{ts}"
            try:
                with open(src, "rb") as rf, open(backup, "wb") as wf:
                    wf.write(rf.read())
            except Exception as e:
                print("WARN: 備份失敗:", e)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, separators=(",", ":"), indent=None)
        return dst

    def get_gold(self):
        return self.data.get(self.gold_key)

    def set_gold(self, value):
        v = safe_int(value, 0)
        self.data[self.gold_key] = max(0, v if v is not None else 0)

    def get_rep(self):
        return self.data.get(self.reputation_key)

    def set_rep(self, value):
        v = safe_int(value, 0)
        self.data[self.reputation_key] = max(0, v if v is not None else 0)

    def iter_roster(self, only_team=None):
        for idx, npc in enumerate(self.npcs):
            if not isinstance(npc, dict):
                continue
            if only_team is None or npc.get('team') == only_team:
                yield idx, npc

    @staticmethod
    def npc_summary(npc):
        return {
            'id': npc.get('id'),
            'unitId': npc.get('unitId'),
            'team': npc.get('team'),
            'unitname': npc.get('unitname'),
            'level': npc.get('level'),
            'potentialPoint': npc.get('potentialPoint'),
            'skillPoint': npc.get('skillPoint'),
            'livingSkillPoint': npc.get('livingSkillPoint'),
        }

# ---------- 介面 ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1200x700")
        self.minsize(1000, 620)

        # DPI/縮放
        try:
            self.tk.call('tk', 'scaling', 1.25)  # 預設放大 125%
        except Exception:
            pass

        # 風格與主題
        self.style = init_style(self)
        self.theme_var = tk.StringVar(value="亮色")
        self.tag_colors = {}
        self.apply_palette(self.theme_var.get())

        # 內部狀態
        self.model = SaveModel()
        self.show_only_player_var = tk.BooleanVar(value=True)
        self.only_underscore_var = tk.BooleanVar(value=False)
        self.search_var = tk.StringVar(value="")
        self.filter_min_level_var = tk.StringVar(value="")

        # 全域屬性
        self.gold_var = tk.StringVar(value="")
        self.rep_var = tk.StringVar(value="")

        # 編輯欄位
        self.level_var = tk.StringVar(value="")
        self.potential_var = tk.StringVar(value="")
        self.skill_var = tk.StringVar(value="")
        self.living_skill_var = tk.StringVar(value="")

        self.bulk_mode_var = tk.StringVar(value="add")  # add / set

        # 排序狀態
        self.sort_column = None
        self.sort_reverse = False

        # UI
        self.create_menu()
        self.create_widgets()

        # 快捷鍵
        self.bind_all("<Control-o>", lambda e: self.on_open())
        self.bind_all("<Control-s>", lambda e: self.on_save())

        # 嘗試自動載入
        if os.path.exists(DEFAULT_FILENAME):
            try:
                self.load_path(DEFAULT_FILENAME)
            except Exception as e:
                print("自動載入失敗:", e)

    # --------- 主題配色 ---------
    def apply_palette(self, kind):
        self.tag_colors = style_apply_palette(self, self.style, kind)

    # ---------- UI ----------
    def create_menu(self):
        mbar = tk.Menu(self)
        filem = tk.Menu(mbar, tearoff=False)
        filem.add_command(label="開啟存檔... (Ctrl+O)", command=self.on_open)
        filem.add_command(label="儲存 (Ctrl+S)", command=self.on_save)
        filem.add_command(label="另存新檔...", command=self.on_save_as)
        filem.add_separator()
        filem.add_command(label="離開", command=self.on_quit)
        mbar.add_cascade(label="檔案", menu=filem)

        viewm = tk.Menu(mbar, tearoff=False)
        viewm.add_command(label="介面縮放 100%", command=lambda: self.tk.call('tk', 'scaling', 1.0))
        viewm.add_command(label="介面縮放 125%", command=lambda: self.tk.call('tk', 'scaling', 1.25))
        viewm.add_command(label="介面縮放 150%", command=lambda: self.tk.call('tk', 'scaling', 1.5))
        mbar.add_cascade(label="視圖", menu=viewm)

        helpm = tk.Menu(mbar, tearoff=False)
        helpm.add_command(label="關於", command=self.on_about)
        mbar.add_cascade(label="說明", menu=helpm)
        self.config(menu=mbar)

    def card(self, parent, title=None):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(10,10,10,10))
        frame.pack(fill="x", pady=(0,8))
        if title:
            ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0,6))
        return frame

    def create_widgets(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        # 外觀/主題列
        topbar = self.card(root)
        ttk.Label(topbar, text="外觀：", width=6).pack(side="left")
        ttk.OptionMenu(topbar, self.theme_var, self.theme_var.get(), "亮色", "暗色", command=self.on_theme_change).pack(side="left", padx=(0,10))
        ttk.Label(topbar, text="（可在「視圖」選單調整介面縮放）", style="Hint.TLabel").pack(side="left")

        # 全局屬性 + 篩選
        meta = self.card(root, "全局屬性 / 篩選")
        # 行1：篩選控制
        row1 = ttk.Frame(meta)
        row1.pack(fill="x", pady=4)
        ttk.Checkbutton(row1, text="只顯示玩家隊伍 (team=0)", variable=self.show_only_player_var, command=self.refresh_table).pack(side="left")
        ttk.Checkbutton(row1, text="只顯示名字含底線 _", variable=self.only_underscore_var, command=self.refresh_table).pack(side="left", padx=(10,0))
        ttk.Label(row1, text="搜尋名字：").pack(side="left", padx=(14,2))
        ttk.Entry(row1, textvariable=self.search_var, width=20).pack(side="left", padx=(0,10))
        ttk.Label(row1, text="等級下限：").pack(side="left")
        ttk.Entry(row1, textvariable=self.filter_min_level_var, width=6).pack(side="left", padx=(4,6))
        ttk.Button(row1, text="套用篩選", command=self.refresh_table).pack(side="left", padx=(8,0))

        # 行2：全局屬性
        row2 = ttk.Frame(meta)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="金錢 (wealth)：").pack(side="left")
        ttk.Entry(row2, textvariable=self.gold_var, width=10).pack(side="left", padx=(4,12))
        ttk.Label(row2, text="聲望 (reputation)：").pack(side="left")
        ttk.Entry(row2, textvariable=self.rep_var, width=10).pack(side="left", padx=(4,12))
        ttk.Button(row2, text="更新全局屬性", command=self.on_update_meta).pack(side="left")
        ttk.Label(meta, text="提示：修改後記得到【檔案→儲存】寫回存檔（會自動備份）", style="Hint.TLabel").pack(anchor="w", pady=(6,0))

        # 表格
        table_card = self.card(root, "角鬥士清單")
        table_frame = ttk.Frame(table_card)
        table_frame.pack(fill="both", expand=True)

        columns = ("idx","id","unitId","team","unitname","level","potentialPoint","skillPoint","livingSkillPoint")
        headers = {
            "idx": "索引", "id": "ID", "unitId": "單位ID", "team": "隊伍",
            "unitname": "名稱", "level": "等級", "potentialPoint": "潛力點",
            "skillPoint": "技能點", "livingSkillPoint": "生活技能點"
        }
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        col_widths = (70,80,80,60,280,70,90,90,120)
        for col, w in zip(columns, col_widths):
            self.tree.heading(col, text=headers[col], command=lambda c=col: self.on_sort_column(c))
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)
        yscroll.pack(side="right", fill="y")

        # 編輯面板
        editor = self.card(root, "批次編輯（套用至選取的角色）")
        grid = ttk.Frame(editor)
        grid.pack(fill="x", padx=2, pady=2)

        r=0
        ttk.Label(grid, text="等級").grid(row=r, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.level_var, width=8).grid(row=r, column=1, sticky="w", padx=6)
        ttk.Label(grid, text="潛力點").grid(row=r, column=2, sticky="w")
        ttk.Entry(grid, textvariable=self.potential_var, width=8).grid(row=r, column=3, sticky="w", padx=6)
        ttk.Label(grid, text="技能點").grid(row=r, column=4, sticky="w")
        ttk.Entry(grid, textvariable=self.skill_var, width=8).grid(row=r, column=5, sticky="w", padx=6)
        ttk.Label(grid, text="生活技能點").grid(row=r, column=6, sticky="w")
        ttk.Entry(grid, textvariable=self.living_skill_var, width=10).grid(row=r, column=7, sticky="w", padx=6)

        r+=1
        ttk.Label(grid, text="模式").grid(row=r, column=0, sticky="w", pady=(8,0))
        ttk.Radiobutton(grid, text="加值 (±)", variable=self.bulk_mode_var, value="add").grid(row=r, column=1, sticky="w", pady=(8,0))
        ttk.Radiobutton(grid, text="設值 (=)", variable=self.bulk_mode_var, value="set").grid(row=r, column=2, sticky="w", pady=(8,0))
        ttk.Button(grid, text="套用到選取", command=self.on_apply_selected).grid(row=r, column=3, sticky="w", padx=10, pady=(8,0))

        ttk.Label(editor, text="建議：先用「加值」小幅調整（+5～+10），避免過度破壞平衡。", style="Hint.TLabel").pack(anchor="w", pady=(6,0))

    # ---------- 事件 ----------
    def on_theme_change(self, *_):
        self.apply_palette(self.theme_var.get())
        self.refresh_table()

    def on_open(self):
        path = filedialog.askopenfilename(
            title="選取 Blackthorn 存檔（JSON）",
            filetypes=[("存檔 / JSON", "*.dat *.json"), ("所有檔案", "*.*")],
            initialfile=DEFAULT_FILENAME
        )
        if path:
            self.load_path(path)

    def on_save(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "請先載入存檔。")
            return
        try:
            out = self.model.save(make_backup=True)
            messagebox.showinfo(APP_TITLE, f"已儲存：\n{out}\n（已在原檔旁建立備份）")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"儲存失敗：\n{e}")

    def on_save_as(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "請先載入存檔。")
            return
        path = filedialog.asksaveasfilename(
            title="另存新檔",
            defaultextension=".dat",
            initialfile="sav_edited.dat",
            filetypes=[("DAT 檔", "*.dat"), ("JSON 檔", "*.json"), ("所有檔案", "*.*")]
        )
        if path:
            try:
                out = self.model.save(out_path=path, make_backup=True)
                messagebox.showinfo(APP_TITLE, f"已儲存：\n{out}\n（原檔已備份）")
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"儲存失敗：\n{e}")

    def on_quit(self):
        self.destroy()

    def on_about(self):
        messagebox.showinfo(APP_TITLE, "繁中介面存檔修改器（JSON）。\n提示：預設僅顯示玩家隊伍 team=0，可切換為顯示全部 NPC。")

    def load_path(self, path):
        ok = self.model.load(path)
        if not ok:
            raise RuntimeError("載入失敗")
        # 填入全局屬性
        self.gold_var.set(str(self.model.get_gold()))
        self.rep_var.set(str(self.model.get_rep()))
        self.refresh_table()
        self.title(f"{APP_TITLE} — {os.path.basename(path)}")

    def refresh_table(self):
        # 清空表格
        for i in self.tree.get_children():
            self.tree.delete(i)

        only_team = self.model.player_team if self.show_only_player_var.get() else None
        search = self.search_var.get().strip().lower()
        minlvl = safe_int(self.filter_min_level_var.get(), 0) or 0
        only_us = self.only_underscore_var.get()

        # 準備資料
        rows = []
        for idx, npc in self.model.iter_roster(only_team=only_team):
            s = self.model.npc_summary(npc)
            name = str(s.get('unitname') or "")
            lvl = s.get('level') or 0
            if only_us and "_" not in name:
                continue
            if search and search not in name.lower():
                continue
            if lvl < minlvl:
                continue
            rows.append((idx, s))

        # 排序（如有指定）
        if self.sort_column:
            key = self.sort_column
            def kfunc(item):
                s = item[1]
                v = s.get(key)
                # 字串/數字混用處理
                try:
                    return (0, int(v))
                except Exception:
                    return (1, str(v))
            rows.sort(key=kfunc, reverse=self.sort_reverse)
        else:
            # 預設：team asc, level desc, name asc
            rows.sort(key=lambda item: (item[1].get('team', 0), -(item[1].get('level') or 0), str(item[1].get('unitname') or "")))

        # 插入（斑馬紋 / 關鍵字高亮）
        even_bg = self.tag_colors["even"]
        odd_bg = self.tag_colors["odd"]
        match_bg = self.tag_colors["match"]

        for n, (idx, s) in enumerate(rows):
            name = str(s.get('unitname') or "")
            values = (
                idx, s.get('id'), s.get('unitId'), s.get('team'),
                name, s.get('level'), s.get('potentialPoint'), s.get('skillPoint'),
                s.get('livingSkillPoint')
            )
            tag = "even" if n % 2 == 0 else "odd"
            tags = (tag,)
            if self.search_var.get().strip() and self.search_var.get().strip().lower() in name.lower():
                tags = tags + ("match",)
            self.tree.insert("", "end", iid=str(idx), values=values, tags=tags)

        # 標籤顏色
        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)
        self.tree.tag_configure("match", background=match_bg)

    def on_update_meta(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "請先載入存檔。")
            return
        self.model.set_gold(self.gold_var.get())
        self.model.set_rep(self.rep_var.get())
        messagebox.showinfo(APP_TITLE, "已更新全局屬性（暫存於記憶體）。請至【檔案→儲存】寫回。")

    def on_apply_selected(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "請先載入存檔。")
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(APP_TITLE, "請先在表格中選取至少一名角色。")
            return

        fields = []
        if self.level_var.get().strip():
            fields.append(("level", self.level_var.get()))
        if self.potential_var.get().strip():
            fields.append(("potentialPoint", self.potential_var.get()))
        if self.skill_var.get().strip():
            fields.append(("skillPoint", self.skill_var.get()))
        if self.living_skill_var.get().strip():
            fields.append(("livingSkillPoint", self.living_skill_var.get()))

        if not fields:
            messagebox.showwarning(APP_TITLE, "請至少輸入一個欄位的數值。")
            return

        mode = self.bulk_mode_var.get()  # add / set
        count = 0
        for iid in sel:
            idx = int(iid)
            if idx < 0 or idx >= len(self.model.npcs):
                continue
            npc = self.model.npcs[idx]
            for key, val in fields:
                v = safe_int(val, None)
                if v is None:
                    continue
                old = npc.get(key) or 0
                if mode == "add":
                    npc[key] = max(0, old + v)
                else:
                    npc[key] = max(0, v)
            count += 1

        self.refresh_table()
        messagebox.showinfo(APP_TITLE, f"已套用至 {count} 名角色。請至【檔案→儲存】寫回。")

    def on_sort_column(self, col):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        self.refresh_table()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
