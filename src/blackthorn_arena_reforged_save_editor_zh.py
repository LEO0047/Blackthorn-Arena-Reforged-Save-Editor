#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黑荊棘角鬥場：重鑄版 存檔修改器（繁中介面, 強化視覺）
作者：ChatGPT
用途：編輯 JSON 格式的存檔（通常為 sav.dat）

主要功能
- 讀取 / 顯示角鬥士名單（預設只顯示玩家隊伍 team==0，可切換「全部 NPC」）
- 搜尋、等級下限篩選、只看名字含底線 _ 的角色
 - 批次編輯：等級 / 潛力點 potentialPoint / 技能點 skillPoint / 生活技能點 livingSkillPoint / 基礎能力（BSstrength、BSendurance、
BSagility、BSprecision、BSintelligence、BSwillpower）
- 全局屬性：金錢（wealth）、聲望（reputation）
- 自動備份：儲存時會在原始檔旁建立 .bak.時間戳

免責：請先備份存檔，風險自負。
"""
from __future__ import annotations

import json
import os
import time
from typing import Dict, List, Tuple

import customtkinter as ctk
from tkinter import filedialog, messagebox

APP_TITLE = "黑荊棘角鬥場：重鑄版 存檔修改器（JSON）"
DEFAULT_FILENAME = "sav.dat"

COLUMN_DEFINITIONS: List[Tuple[str, str, int]] = [
    ("idx", "索引", 70),
    ("id", "ID", 90),
    ("unitId", "單位ID", 90),
    ("team", "隊伍", 70),
    ("unitname", "名稱", 240),
    ("level", "等級", 80),
    ("potentialPoint", "潛力點", 100),
    ("skillPoint", "技能點", 100),
    ("livingSkillPoint", "生活技能點", 120),
]

EVEN_ROW_COLOR = "#23283a"
ODD_ROW_COLOR = "#1c2133"
MATCH_ROW_COLOR = "#34405f"
SELECTED_BORDER_COLOR = "#4f83ff"


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
        if isinstance(self.npcs, list):
            # 過濾死亡的角色
            self.npcs = [npc for npc in self.npcs if not self.is_dead(npc)]
        else:
            self.npcs = []
        # 確保內部資料與名單一致
        self.data['npcs'] = self.npcs
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
            if not isinstance(npc, dict) or self.is_dead(npc):
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

    @staticmethod
    def is_dead(npc):
        """判斷角色是否已死亡"""
        if not isinstance(npc, dict):
            return False
        if npc.get('isDead') or npc.get('dead'):
            return True
        death_date = npc.get('deathDate')
        if isinstance(death_date, (int, float)) and death_date > 0:
            return True
        state = npc.get('state')
        if isinstance(state, str) and state.lower() == 'dead':
            return True
        gl_state = npc.get('gladiatorState')
        if isinstance(gl_state, (int, float)) and gl_state >= 5:
            return True
        for key in ('hp', 'HP', 'currentHp', 'curHp', 'currentHP'):
            hp = npc.get(key)
            if isinstance(hp, (int, float)) and hp <= 0:
                return True
        return False


# ---------- 介面 ----------
class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1200x720")
        self.minsize(1040, 640)
        self.configure(fg_color="#111521")

        # 內部狀態
        self.model = SaveModel()
        self.show_only_player_var = ctk.BooleanVar(value=True)
        self.only_underscore_var = ctk.BooleanVar(value=False)
        self.search_var = ctk.StringVar(value="")
        self.filter_min_level_var = ctk.StringVar(value="")

        # 全域屬性
        self.gold_var = ctk.StringVar(value="")
        self.rep_var = ctk.StringVar(value="")

        # 編輯欄位
        self.level_var = ctk.StringVar(value="")
        self.potential_var = ctk.StringVar(value="")
        self.skill_var = ctk.StringVar(value="")
        self.living_skill_var = ctk.StringVar(value="")
        self.strength_var = ctk.StringVar(value="")
        self.endurance_var = ctk.StringVar(value="")
        self.agility_var = ctk.StringVar(value="")
        self.precision_var = ctk.StringVar(value="")
        self.intelligence_var = ctk.StringVar(value="")
        self.willpower_var = ctk.StringVar(value="")

        self.bulk_mode_var = ctk.StringVar(value="add")  # add / set

        # 排序狀態
        self.sort_column = None
        self.sort_reverse = False

        # 選取狀態
        self.selected_indices: set[int] = set()
        self.row_vars: Dict[int, ctk.BooleanVar] = {}
        self.row_frames: Dict[int, ctk.CTkFrame] = {}
        self.current_rows: List[Tuple[int, Dict[str, object]]] = []

        # 狀態列
        self.status_var = ctk.StringVar(value="準備就緒")

        # 版面配置
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_title_bar()
        self._build_main_area()
        self._build_status_bar()

        # 快捷鍵
        self.bind("<Control-o>", lambda e: self.on_open())
        self.bind("<Control-s>", lambda e: self.on_save())

        # 嘗試自動載入
        if os.path.exists(DEFAULT_FILENAME):
            try:
                self.load_path(DEFAULT_FILENAME)
            except Exception as e:
                print("自動載入失敗:", e)
                self.set_status("自動載入失敗")

    # ------------------------------------------------------------------
    # UI 建構
    def _build_title_bar(self) -> None:
        bar = ctk.CTkFrame(self, corner_radius=0, fg_color="#161b2a")
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)
        bar.columnconfigure(1, weight=0)

        title_label = ctk.CTkLabel(
            bar,
            text="黑荊棘角鬥場：重鑄版 存檔修改器",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#f4f6ff",
        )
        title_label.grid(row=0, column=0, padx=20, pady=14, sticky="w")

        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=16, pady=10, sticky="e")

        open_btn = ctk.CTkButton(
            btn_frame,
            text="開啟存檔",
            command=self.on_open,
            corner_radius=20,
            fg_color="#5a67d8",
            hover_color="#4854bd",
            width=120,
        )
        save_btn = ctk.CTkButton(
            btn_frame,
            text="儲存",
            command=self.on_save,
            corner_radius=20,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            width=120,
        )
        about_btn = ctk.CTkButton(
            btn_frame,
            text="關於",
            command=self.on_about,
            corner_radius=20,
            fg_color="#374151",
            hover_color="#4b5563",
            width=80,
        )
        open_btn.grid(row=0, column=0, padx=(0, 8))
        save_btn.grid(row=0, column=1, padx=(0, 8))
        about_btn.grid(row=0, column=2)

    def _build_main_area(self) -> None:
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, padx=18, pady=16, sticky="nsew")
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        self._build_list_panel(main)
        self._build_editor_panel(main)

    def _build_list_panel(self, parent: ctk.CTkFrame) -> None:
        panel = ctk.CTkFrame(
            parent,
            corner_radius=18,
            fg_color="#1b1f2d",
            border_width=1,
            border_color="#262d3f",
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(3, weight=1)

        header = ctk.CTkLabel(
            panel,
            text="角鬥士清單",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e0e6ff",
        )
        header.grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        filter_frame = ctk.CTkFrame(panel, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=18, pady=6, sticky="ew")
        filter_frame.columnconfigure(5, weight=1)

        show_player_chk = ctk.CTkCheckBox(
            filter_frame,
            text="只顯示玩家隊伍 (team=0)",
            variable=self.show_only_player_var,
            command=self.refresh_table,
        )
        underscore_chk = ctk.CTkCheckBox(
            filter_frame,
            text="只顯示名字含底線 _",
            variable=self.only_underscore_var,
            command=self.refresh_table,
        )
        search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="搜尋名字",
            width=160,
        )
        level_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.filter_min_level_var,
            placeholder_text="等級下限",
            width=100,
        )
        apply_btn = ctk.CTkButton(
            filter_frame,
            text="套用篩選",
            command=self.refresh_table,
            width=120,
        )
        show_player_chk.grid(row=0, column=0, padx=(0, 12), pady=4, sticky="w")
        underscore_chk.grid(row=0, column=1, padx=(0, 12), pady=4, sticky="w")
        search_entry.grid(row=0, column=2, padx=(0, 10), pady=4, sticky="w")
        level_entry.grid(row=0, column=3, padx=(0, 12), pady=4, sticky="w")
        apply_btn.grid(row=0, column=4, padx=(0, 12), pady=4, sticky="e")

        header_frame = ctk.CTkFrame(panel, fg_color="#111521", corner_radius=12)
        header_frame.grid(row=2, column=0, padx=18, pady=(10, 6), sticky="ew")
        header_frame.columnconfigure(0, weight=0)
        for i in range(1, len(COLUMN_DEFINITIONS) + 1):
            header_frame.columnconfigure(i, weight=0)

        select_label = ctk.CTkLabel(
            header_frame,
            text="選取",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#9aa4d1",
            width=60,
        )
        select_label.grid(row=0, column=0, padx=(12, 6), pady=8, sticky="w")

        for col_index, (key, title, width) in enumerate(COLUMN_DEFINITIONS, start=1):
            btn = ctk.CTkButton(
                header_frame,
                text=title,
                command=lambda c=key: self.on_sort_column(c),
                corner_radius=12,
                fg_color="#1f2537",
                hover_color="#2c3146",
                width=width,
            )
            btn.grid(row=0, column=col_index, padx=6, pady=8, sticky="w")

        self.scroll_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll_frame.grid(row=3, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _build_editor_panel(self, parent: ctk.CTkFrame) -> None:
        panel = ctk.CTkFrame(
            parent,
            corner_radius=18,
            fg_color="#1b1f2d",
            border_width=1,
            border_color="#262d3f",
        )
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        meta_frame = ctk.CTkFrame(panel, fg_color="#151929", corner_radius=16)
        meta_frame.grid(row=0, column=0, padx=18, pady=(20, 10), sticky="ew")
        meta_frame.columnconfigure(1, weight=1)

        meta_title = ctk.CTkLabel(
            meta_frame,
            text="全局屬性",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f1f3ff",
        )
        meta_title.grid(row=0, column=0, columnspan=2, padx=16, pady=(14, 6), sticky="w")

        gold_label = ctk.CTkLabel(meta_frame, text="金錢 (wealth)：", text_color="#cbd5ff")
        gold_entry = ctk.CTkEntry(meta_frame, textvariable=self.gold_var, width=140)
        rep_label = ctk.CTkLabel(meta_frame, text="聲望 (reputation)：", text_color="#cbd5ff")
        rep_entry = ctk.CTkEntry(meta_frame, textvariable=self.rep_var, width=140)
        update_btn = ctk.CTkButton(meta_frame, text="更新全局屬性", command=self.on_update_meta)
        save_as_btn = ctk.CTkButton(meta_frame, text="另存新檔", command=self.on_save_as, fg_color="#3f3f46", hover_color="#51525b")

        gold_label.grid(row=1, column=0, padx=(16, 4), pady=6, sticky="w")
        gold_entry.grid(row=1, column=1, padx=(0, 16), pady=6, sticky="w")
        rep_label.grid(row=2, column=0, padx=(16, 4), pady=6, sticky="w")
        rep_entry.grid(row=2, column=1, padx=(0, 16), pady=6, sticky="w")
        update_btn.grid(row=3, column=0, padx=16, pady=(12, 14), sticky="w")
        save_as_btn.grid(row=3, column=1, padx=(0, 16), pady=(12, 14), sticky="e")

        bulk_frame = ctk.CTkFrame(panel, fg_color="#151929", corner_radius=16)
        bulk_frame.grid(row=1, column=0, padx=18, pady=(10, 20), sticky="nsew")
        bulk_frame.columnconfigure(1, weight=1)

        bulk_title = ctk.CTkLabel(
            bulk_frame,
            text="批次編輯（套用至選取的角色）",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f1f3ff",
        )
        bulk_title.grid(row=0, column=0, columnspan=4, padx=16, pady=(14, 10), sticky="w")

        form = ctk.CTkFrame(bulk_frame, fg_color="transparent")
        form.grid(row=1, column=0, columnspan=4, padx=16, pady=4, sticky="ew")
        for i in range(8):
            form.columnconfigure(i, weight=1 if i in (4, 5) else 0)

        entries = [
            ("等級", self.level_var),
            ("潛力點", self.potential_var),
            ("技能點", self.skill_var),
            ("生活技能點", self.living_skill_var),
            ("力量", self.strength_var),
            ("耐力", self.endurance_var),
            ("敏捷", self.agility_var),
            ("精準", self.precision_var),
            ("智力", self.intelligence_var),
            ("意志力", self.willpower_var),
        ]

        for idx, (name, var) in enumerate(entries[:4]):
            column = idx * 2
            label = ctk.CTkLabel(form, text=name, text_color="#cbd5ff")
            entry = ctk.CTkEntry(form, textvariable=var, width=100)
            label.grid(row=0, column=column, padx=(0, 6), pady=6, sticky="w")
            entry.grid(row=0, column=column + 1, padx=(0, 18), pady=6, sticky="w")

        for idx, (name, var) in enumerate(entries[4:]):
            r = 1 + idx // 4
            c = (idx % 4) * 2
            label = ctk.CTkLabel(form, text=name, text_color="#cbd5ff")
            entry = ctk.CTkEntry(form, textvariable=var, width=100)
            label.grid(row=r, column=c, padx=(0, 6), pady=6, sticky="w")
            entry.grid(row=r, column=c + 1, padx=(0, 18), pady=6, sticky="w")

        mode_label = ctk.CTkLabel(bulk_frame, text="模式", text_color="#cbd5ff")
        mode_menu = ctk.CTkOptionMenu(
            bulk_frame,
            values=["加值 (±)", "設值 (=)"],
            command=self._on_mode_change,
            width=160,
        )
        mode_menu.set("加值 (±)")
        apply_btn = ctk.CTkButton(
            bulk_frame,
            text="套用到選取",
            command=self.on_apply_selected,
            fg_color="#10b981",
            hover_color="#059669",
            width=180,
        )
        hint_label = ctk.CTkLabel(
            bulk_frame,
            text="建議：先用「加值」小幅調整（+5～+10），避免過度破壞平衡。",
            wraplength=360,
            text_color="#9aa4d1",
            anchor="w",
            justify="left",
        )

        mode_label.grid(row=2, column=0, padx=16, pady=(12, 6), sticky="w")
        mode_menu.grid(row=2, column=1, padx=(0, 16), pady=(12, 6), sticky="w")
        apply_btn.grid(row=2, column=2, padx=(16, 16), pady=(12, 6), sticky="e")
        hint_label.grid(row=3, column=0, columnspan=4, padx=16, pady=(6, 16), sticky="w")

    def _build_status_bar(self) -> None:
        bar = ctk.CTkFrame(self, corner_radius=0, fg_color="#161b2a")
        bar.grid(row=2, column=0, sticky="ew")
        label = ctk.CTkLabel(bar, textvariable=self.status_var, text_color="#cbd5ff")
        label.pack(anchor="w", padx=18, pady=6)

    # ------------------------------------------------------------------
    # 公用方法
    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _on_mode_change(self, selection: str) -> None:
        if "設值" in selection:
            self.bulk_mode_var.set("set")
        else:
            self.bulk_mode_var.set("add")

    def _clear_roster_widgets(self) -> None:
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.row_vars.clear()
        self.row_frames.clear()

    def _create_row(self, position: int, idx: int, summary: Dict[str, object], highlight: bool) -> None:
        bg_color = MATCH_ROW_COLOR if highlight else (EVEN_ROW_COLOR if position % 2 == 0 else ODD_ROW_COLOR)
        row_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=bg_color,
            corner_radius=10,
            border_width=2 if idx in self.selected_indices else 0,
            border_color=SELECTED_BORDER_COLOR,
        )
        row_frame.grid(row=position, column=0, sticky="ew", padx=6, pady=4)
        for c in range(len(COLUMN_DEFINITIONS) + 1):
            weight = 1 if c == 5 else 0
            row_frame.grid_columnconfigure(c, weight=weight)

        var = ctk.BooleanVar(value=(idx in self.selected_indices))
        self.row_vars[idx] = var
        self.row_frames[idx] = row_frame

        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=var,
            command=lambda i=idx: self.on_toggle_select(i),
            fg_color="#3b82f6",
            hover_color="#2563eb",
        )
        checkbox.grid(row=0, column=0, padx=(12, 8), pady=8)

        values = [
            idx,
            summary.get('id'),
            summary.get('unitId'),
            summary.get('team'),
            summary.get('unitname'),
            summary.get('level'),
            summary.get('potentialPoint'),
            summary.get('skillPoint'),
            summary.get('livingSkillPoint'),
        ]
        for col_index, value in enumerate(values, start=1):
            key, _, width = COLUMN_DEFINITIONS[col_index - 1]
            text = "" if value is None else str(value)
            anchor = "w"
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                width=width,
                anchor=anchor,
                text_color="#e5e7ff",
            )
            label.grid(row=0, column=col_index, padx=(0, 12), pady=8, sticky="w")

    def on_toggle_select(self, idx: int) -> None:
        var = self.row_vars.get(idx)
        if not var:
            return
        if var.get():
            self.selected_indices.add(idx)
        else:
            self.selected_indices.discard(idx)
        frame = self.row_frames.get(idx)
        if frame:
            frame.configure(border_width=2 if idx in self.selected_indices else 0)
        self.set_status(f"已選取 {len(self.selected_indices)} 名角色")

    # ------------------------------------------------------------------
    # 事件
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
            self.set_status("存檔已儲存並備份")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"儲存失敗：\n{e}")
            self.set_status("儲存失敗")

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
                self.set_status("另存新檔成功")
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"儲存失敗：\n{e}")
                self.set_status("另存失敗")

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
        self.set_status(f"已載入：{path}")

    def refresh_table(self):
        self._clear_roster_widgets()

        only_team = self.model.player_team if self.show_only_player_var.get() else None
        search = self.search_var.get().strip().lower()
        minlvl = safe_int(self.filter_min_level_var.get(), 0) or 0
        only_us = self.only_underscore_var.get()

        rows: List[Tuple[int, Dict[str, object]]] = []
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

        if self.sort_column:
            key = self.sort_column

            def kfunc(item):
                s = item[1]
                v = s.get(key)
                try:
                    return (0, int(v))
                except Exception:
                    return (1, str(v))

            rows.sort(key=kfunc, reverse=self.sort_reverse)
        else:
            rows.sort(key=lambda item: (item[1].get('team', 0), -(item[1].get('level') or 0), str(item[1].get('unitname') or "")))

        self.current_rows = rows
        valid_indices = {idx for idx, _ in rows}
        self.selected_indices.intersection_update(valid_indices)

        for position, (idx, summary) in enumerate(rows):
            name = str(summary.get('unitname') or "")
            highlight = bool(search and search in name.lower())
            self._create_row(position, idx, summary, highlight)

        self.set_status(f"顯示 {len(rows)} 名角色，已選取 {len(self.selected_indices)} 名")

    def on_update_meta(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "請先載入存檔。")
            return
        self.model.set_gold(self.gold_var.get())
        self.model.set_rep(self.rep_var.get())
        messagebox.showinfo(APP_TITLE, "已更新全局屬性（暫存於記憶體）。請至【檔案→儲存】寫回。")
        self.set_status("已更新全局屬性")

    def on_apply_selected(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "請先載入存檔。")
            return
        if not self.selected_indices:
            messagebox.showwarning(APP_TITLE, "請先在清單中選取至少一名角色。")
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
        if self.strength_var.get().strip():
            fields.append(("BSstrength", self.strength_var.get()))
        if self.endurance_var.get().strip():
            fields.append(("BSendurance", self.endurance_var.get()))
        if self.agility_var.get().strip():
            fields.append(("BSagility", self.agility_var.get()))
        if self.precision_var.get().strip():
            fields.append(("BSprecision", self.precision_var.get()))
        if self.intelligence_var.get().strip():
            fields.append(("BSintelligence", self.intelligence_var.get()))
        if self.willpower_var.get().strip():
            fields.append(("BSwillpower", self.willpower_var.get()))

        if not fields:
            messagebox.showwarning(APP_TITLE, "請至少輸入一個欄位的數值。")
            return

        mode = self.bulk_mode_var.get()  # add / set
        count = 0
        for idx in sorted(self.selected_indices):
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
        self.set_status(f"批次套用完成，共 {count} 名")

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
