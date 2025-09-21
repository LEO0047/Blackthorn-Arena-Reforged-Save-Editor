#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""黑荊棘角鬥場：重鑄版 存檔修改器（CustomTkinter 深色介面，多語系準備）"""
from __future__ import annotations

import json
import os
import time
from typing import Dict, List, Tuple

try:
    import customtkinter as ctk
except ImportError as exc:  # pragma: no cover - 以便顯示友善訊息
    print("CustomTkinter is required. Please install it with: pip install customtkinter>=5.2")
    raise SystemExit(1) from exc

from tkinter import filedialog, messagebox

DEFAULT_FILENAME = "sav.dat"
DEFAULT_LANGUAGE = "zh"

LANG_DISPLAY_NAMES = {
    "zh": "繁體中文",
    "en": "English",
}

TRANSLATIONS = {
    "zh": {
        "app_title": "黑荊棘角鬥場：重鑄版 存檔修改器（JSON）",
        "title_label": "黑荊棘角鬥場：重鑄版 存檔修改器",
        "btn_open": "開啟存檔",
        "btn_save": "儲存",
        "btn_about": "關於",
        "language_menu_label": "介面語言",
        "dialog_open_title": "選取 Blackthorn 存檔（JSON）",
        "dialog_open_filter": "存檔 / JSON",
        "dialog_all_files": "所有檔案",
        "dialog_save_as_title": "另存新檔",
        "dialog_save_as_default_name": "sav_edited.dat",
        "dialog_save_as_dat": "DAT 檔",
        "dialog_save_as_json": "JSON 檔",
        "list_header": "角鬥士清單",
        "show_player_only": "只顯示玩家隊伍 (team=0)",
        "only_underscore": "只顯示名字含底線 _",
        "search_placeholder": "搜尋名字",
        "min_level_placeholder": "等級下限",
        "apply_filters": "套用篩選",
        "column_select": "選取",
        "col_idx": "索引",
        "col_id": "ID",
        "col_unit_id": "單位ID",
        "col_team": "隊伍",
        "col_name": "名稱",
        "col_level": "等級",
        "col_potential": "潛力點",
        "col_skill": "技能點",
        "col_living_skill": "生活技能點",
        "global_section_title": "全局屬性",
        "gold_label": "金錢 (wealth)：",
        "rep_label": "聲望 (reputation)：",
        "update_meta_btn": "更新全局屬性",
        "save_as_btn": "另存新檔",
        "bulk_section_title": "批次編輯（套用至選取的角色）",
        "stat_level": "等級",
        "stat_potential": "潛力點",
        "stat_skill": "技能點",
        "stat_living_skill": "生活技能點",
        "stat_strength": "力量",
        "stat_endurance": "耐力",
        "stat_agility": "敏捷",
        "stat_precision": "精準",
        "stat_intelligence": "智力",
        "stat_willpower": "意志力",
        "mode_label": "模式",
        "mode_add": "加值 (±)",
        "mode_set": "設值 (=)",
        "apply_selected_btn": "套用到選取",
        "hint_text": "建議：先用「加值」小幅調整（+5～+10），避免過度破壞平衡。",
        "about_message": "繁中介面存檔修改器（JSON）。\n提示：預設僅顯示玩家隊伍 team=0，可切換為顯示全部 NPC。",
        "message_load_first": "請先載入存檔。",
        "message_select_first": "請先在清單中選取至少一名角色。",
        "message_enter_field": "請至少輸入一個欄位的數值。",
        "message_update_meta_done": "已更新全局屬性（暫存於記憶體）。請至【檔案→儲存】寫回。",
        "message_apply_done": "已套用至 {count} 名角色。請至【檔案→儲存】寫回。",
        "message_saved": "已儲存：\n{path}\n（已在原檔旁建立備份）",
        "message_saved_as": "已儲存：\n{path}\n（原檔已備份）",
        "message_save_failed": "儲存失敗：\n{error}",
        "status_ready": "準備就緒",
        "status_auto_load_failed": "自動載入失敗",
        "status_loaded": "已載入：{path}",
        "status_saved": "存檔已儲存並備份",
        "status_save_as_done": "另存新檔成功",
        "status_save_failed": "儲存失敗",
        "status_showing": "顯示 {total} 名角色，已選取 {selected} 名",
        "status_selected": "已選取 {count} 名角色",
        "status_meta_updated": "已更新全局屬性",
        "status_batch_done": "批次套用完成，共 {count} 名",
    },
    "en": {
        "app_title": "Blackthorn Arena: Reforged Save Editor (JSON)",
        "title_label": "Blackthorn Arena: Reforged Save Editor",
        "btn_open": "Open Save",
        "btn_save": "Save",
        "btn_about": "About",
        "language_menu_label": "Language",
        "dialog_open_title": "Select Blackthorn save (JSON)",
        "dialog_open_filter": "Save / JSON",
        "dialog_all_files": "All files",
        "dialog_save_as_title": "Save As",
        "dialog_save_as_default_name": "sav_edited.dat",
        "dialog_save_as_dat": "DAT files",
        "dialog_save_as_json": "JSON files",
        "list_header": "Gladiator Roster",
        "show_player_only": "Only show player team (team=0)",
        "only_underscore": "Only names containing '_'",
        "search_placeholder": "Search name",
        "min_level_placeholder": "Minimum level",
        "apply_filters": "Apply filters",
        "column_select": "Select",
        "col_idx": "Index",
        "col_id": "ID",
        "col_unit_id": "Unit ID",
        "col_team": "Team",
        "col_name": "Name",
        "col_level": "Level",
        "col_potential": "Potential",
        "col_skill": "Skill",
        "col_living_skill": "Living Skill",
        "global_section_title": "Global Attributes",
        "gold_label": "Wealth:",
        "rep_label": "Reputation:",
        "update_meta_btn": "Update global attributes",
        "save_as_btn": "Save As",
        "bulk_section_title": "Batch edit (apply to selected gladiators)",
        "stat_level": "Level",
        "stat_potential": "Potential",
        "stat_skill": "Skill",
        "stat_living_skill": "Living skill",
        "stat_strength": "Strength",
        "stat_endurance": "Endurance",
        "stat_agility": "Agility",
        "stat_precision": "Precision",
        "stat_intelligence": "Intelligence",
        "stat_willpower": "Willpower",
        "mode_label": "Mode",
        "mode_add": "Add (±)",
        "mode_set": "Set (=)",
        "apply_selected_btn": "Apply to selection",
        "hint_text": "Tip: use \"Add\" with small increments (+5 to +10) to keep balance.",
        "about_message": "Save editor with a dark CustomTkinter UI.\nTip: the default view shows only team=0 gladiators; switch to see all NPCs.",
        "message_load_first": "Please load a save file first.",
        "message_select_first": "Select at least one gladiator from the list.",
        "message_enter_field": "Enter a value for at least one field.",
        "message_update_meta_done": "Global attributes updated in memory. Use File → Save to write changes.",
        "message_apply_done": "Applied to {count} gladiators. Use File → Save to write changes.",
        "message_saved": "Saved to:\n{path}\n(A backup was created next to the original file.)",
        "message_saved_as": "Saved to:\n{path}\n(The original file was backed up.)",
        "message_save_failed": "Save failed:\n{error}",
        "status_ready": "Ready",
        "status_auto_load_failed": "Automatic load failed",
        "status_loaded": "Loaded: {path}",
        "status_saved": "Save completed with backup",
        "status_save_as_done": "Saved as new file",
        "status_save_failed": "Save failed",
        "status_showing": "Showing {total} gladiators, {selected} selected",
        "status_selected": "Selected {count} gladiators",
        "status_meta_updated": "Global attributes updated",
        "status_batch_done": "Batch edit applied to {count} gladiators",
    },
}

COLUMN_DEFINITIONS: List[Tuple[str, str, int]] = [
    ("idx", "col_idx", 70),
    ("id", "col_id", 90),
    ("unitId", "col_unit_id", 90),
    ("team", "col_team", 70),
    ("unitname", "col_name", 240),
    ("level", "col_level", 80),
    ("potentialPoint", "col_potential", 100),
    ("skillPoint", "col_skill", 100),
    ("livingSkillPoint", "col_living_skill", 120),
]

EVEN_ROW_COLOR = "#23283a"
ODD_ROW_COLOR = "#1c2133"
MATCH_ROW_COLOR = "#34405f"
SELECTED_BORDER_COLOR = "#4f83ff"


class Translator:
    def __init__(self, translations: Dict[str, Dict[str, str]], default: str = "zh") -> None:
        self.translations = translations
        self.default = default if default in translations else next(iter(translations))
        self.current = self.default

    def set_language(self, language: str) -> None:
        if language in self.translations:
            self.current = language

    def translate(self, key: str, **kwargs) -> str:
        template = self.translations.get(self.current, {}).get(key)
        if template is None:
            template = self.translations.get(self.default, {}).get(key, key)
        try:
            return template.format(**kwargs)
        except Exception:
            return template


def safe_int(value, default=None):
    try:
        return int(value)
    except Exception:
        return default


class SaveModel:
    def __init__(self):
        self.path = None
        self.data = None
        self.npcs = []
        self.gold_key = "wealth"
        self.reputation_key = "reputation"
        self.player_team = 0

    def load(self, path):
        self.path = path
        with open(path, "r", encoding="utf-8") as fh:
            self.data = json.load(fh)
        self.npcs = self.data.get("npcs", [])
        if isinstance(self.npcs, list):
            self.npcs = [npc for npc in self.npcs if not self.is_dead(npc)]
        else:
            self.npcs = []
        self.data["npcs"] = self.npcs
        return True

    def save(self, out_path=None, make_backup=True):
        if self.data is None or self.path is None:
            raise RuntimeError("尚未載入存檔")
        src = self.path
        dst = out_path or self.path
        if make_backup and os.path.exists(src):
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup = f"{src}.bak.{timestamp}"
            try:
                with open(src, "rb") as rf, open(backup, "wb") as wf:
                    wf.write(rf.read())
            except Exception as exc:
                print("WARN: 備份失敗:", exc)
        with open(dst, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, separators=(",", ":"), indent=None)
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
            if only_team is None or npc.get("team") == only_team:
                yield idx, npc

    @staticmethod
    def npc_summary(npc):
        return {
            "id": npc.get("id"),
            "unitId": npc.get("unitId"),
            "team": npc.get("team"),
            "unitname": npc.get("unitname"),
            "level": npc.get("level"),
            "potentialPoint": npc.get("potentialPoint"),
            "skillPoint": npc.get("skillPoint"),
            "livingSkillPoint": npc.get("livingSkillPoint"),
        }

    @staticmethod
    def is_dead(npc):
        if not isinstance(npc, dict):
            return False
        if npc.get("isDead") or npc.get("dead"):
            return True
        death_date = npc.get("deathDate")
        if isinstance(death_date, (int, float)) and death_date > 0:
            return True
        state = npc.get("state")
        if isinstance(state, str) and state.lower() == "dead":
            return True
        gladiator_state = npc.get("gladiatorState")
        if isinstance(gladiator_state, (int, float)) and gladiator_state >= 5:
            return True
        for key in ("hp", "HP", "currentHp", "curHp", "currentHP"):
            hp = npc.get(key)
            if isinstance(hp, (int, float)) and hp <= 0:
                return True
        return False


class App(ctk.CTk):
    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        super().__init__()

        self.translator = Translator(TRANSLATIONS, default=DEFAULT_LANGUAGE)
        self.language_display_to_key = {LANG_DISPLAY_NAMES[k]: k for k in self.translator.translations}
        self.language_key_to_display = {v: k for k, v in self.language_display_to_key.items()}

        self.model = SaveModel()
        self.show_only_player_var = ctk.BooleanVar(value=True)
        self.only_underscore_var = ctk.BooleanVar(value=False)
        self.search_var = ctk.StringVar(value="")
        self.filter_min_level_var = ctk.StringVar(value="")

        self.gold_var = ctk.StringVar(value="")
        self.rep_var = ctk.StringVar(value="")

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

        self.bulk_mode_var = ctk.StringVar(value="add")

        self.sort_column = None
        self.sort_reverse = False

        self.selected_indices: set[int] = set()
        self.row_vars: Dict[int, ctk.BooleanVar] = {}
        self.row_frames: Dict[int, ctk.CTkFrame] = {}
        self.current_rows: List[Tuple[int, Dict[str, object]]] = []

        self.status_var = ctk.StringVar(value="")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_title_bar()
        self._build_main_area()
        self._build_status_bar()

        self.bind("<Control-o>", lambda event: self.on_open())
        self.bind("<Control-s>", lambda event: self.on_save())

        self._apply_translations()
        self.set_status(self.tr("status_ready"))

        if os.path.exists(DEFAULT_FILENAME):
            try:
                self.load_path(DEFAULT_FILENAME)
            except Exception as exc:
                print("自動載入失敗:", exc)
                self.set_status(self.tr("status_auto_load_failed"))

    def tr(self, key: str, **kwargs) -> str:
        return self.translator.translate(key, **kwargs)

    def _build_title_bar(self) -> None:
        bar = ctk.CTkFrame(self, corner_radius=0, fg_color="#161b2a")
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)
        bar.columnconfigure(1, weight=0)

        self.title_label = ctk.CTkLabel(
            bar,
            text="",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#f4f6ff",
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=14, sticky="w")

        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=16, pady=10, sticky="e")

        self.open_btn = ctk.CTkButton(
            btn_frame,
            text="",
            command=self.on_open,
            corner_radius=20,
            fg_color="#5a67d8",
            hover_color="#4854bd",
            width=120,
        )
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="",
            command=self.on_save,
            corner_radius=20,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            width=120,
        )
        self.about_btn = ctk.CTkButton(
            btn_frame,
            text="",
            command=self.on_about,
            corner_radius=20,
            fg_color="#374151",
            hover_color="#4b5563",
            width=80,
        )
        self.language_label = ctk.CTkLabel(
            btn_frame,
            text="",
            text_color="#cbd5ff",
        )
        language_values = list(self.language_display_to_key.keys())
        self.language_menu = ctk.CTkOptionMenu(
            btn_frame,
            values=language_values,
            command=self._on_language_change,
            width=130,
        )
        self.language_menu.set(self.language_key_to_display[self.translator.current])

        self.open_btn.grid(row=0, column=0, padx=(0, 8))
        self.save_btn.grid(row=0, column=1, padx=(0, 8))
        self.about_btn.grid(row=0, column=2, padx=(0, 12))
        self.language_label.grid(row=0, column=3, padx=(0, 6))
        self.language_menu.grid(row=0, column=4)

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

        self.list_header_label = ctk.CTkLabel(
            panel,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e0e6ff",
        )
        self.list_header_label.grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        filter_frame = ctk.CTkFrame(panel, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=18, pady=6, sticky="ew")
        filter_frame.columnconfigure(5, weight=1)

        self.show_player_chk = ctk.CTkCheckBox(
            filter_frame,
            text="",
            variable=self.show_only_player_var,
            command=self.refresh_table,
        )
        self.underscore_chk = ctk.CTkCheckBox(
            filter_frame,
            text="",
            variable=self.only_underscore_var,
            command=self.refresh_table,
        )
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            width=160,
        )
        self.level_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.filter_min_level_var,
            width=100,
        )
        self.apply_filter_btn = ctk.CTkButton(
            filter_frame,
            text="",
            command=self.refresh_table,
            width=120,
        )
        self.show_player_chk.grid(row=0, column=0, padx=(0, 12), pady=4, sticky="w")
        self.underscore_chk.grid(row=0, column=1, padx=(0, 12), pady=4, sticky="w")
        self.search_entry.grid(row=0, column=2, padx=(0, 10), pady=4, sticky="w")
        self.level_entry.grid(row=0, column=3, padx=(0, 12), pady=4, sticky="w")
        self.apply_filter_btn.grid(row=0, column=4, padx=(0, 12), pady=4, sticky="e")

        header_frame = ctk.CTkFrame(panel, fg_color="#111521", corner_radius=12)
        header_frame.grid(row=2, column=0, padx=18, pady=(10, 6), sticky="ew")
        header_frame.columnconfigure(0, weight=0)
        for i in range(1, len(COLUMN_DEFINITIONS) + 1):
            header_frame.columnconfigure(i, weight=0)

        self.select_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#9aa4d1",
            width=60,
        )
        self.select_label.grid(row=0, column=0, padx=(12, 6), pady=8, sticky="w")

        self.header_buttons: Dict[str, ctk.CTkButton] = {}
        for column_index, (key, title_key, width) in enumerate(COLUMN_DEFINITIONS, start=1):
            btn = ctk.CTkButton(
                header_frame,
                text="",
                command=lambda c=key: self.on_sort_column(c),
                corner_radius=12,
                fg_color="#1f2537",
                hover_color="#2c3146",
                width=width,
            )
            btn.grid(row=0, column=column_index, padx=6, pady=8, sticky="w")
            self.header_buttons[title_key] = btn

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

        self.meta_title = ctk.CTkLabel(
            meta_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f1f3ff",
        )
        self.meta_title.grid(row=0, column=0, columnspan=2, padx=16, pady=(14, 6), sticky="w")

        self.gold_label = ctk.CTkLabel(meta_frame, text="", text_color="#cbd5ff")
        self.gold_entry = ctk.CTkEntry(meta_frame, textvariable=self.gold_var, width=140)
        self.rep_label = ctk.CTkLabel(meta_frame, text="", text_color="#cbd5ff")
        self.rep_entry = ctk.CTkEntry(meta_frame, textvariable=self.rep_var, width=140)
        self.update_meta_btn = ctk.CTkButton(meta_frame, text="", command=self.on_update_meta)
        self.save_as_btn = ctk.CTkButton(meta_frame, text="", command=self.on_save_as, fg_color="#3f3f46", hover_color="#51525b")

        self.gold_label.grid(row=1, column=0, padx=(16, 4), pady=6, sticky="w")
        self.gold_entry.grid(row=1, column=1, padx=(0, 16), pady=6, sticky="w")
        self.rep_label.grid(row=2, column=0, padx=(16, 4), pady=6, sticky="w")
        self.rep_entry.grid(row=2, column=1, padx=(0, 16), pady=6, sticky="w")
        self.update_meta_btn.grid(row=3, column=0, padx=16, pady=(12, 14), sticky="w")
        self.save_as_btn.grid(row=3, column=1, padx=(0, 16), pady=(12, 14), sticky="e")

        bulk_frame = ctk.CTkFrame(panel, fg_color="#151929", corner_radius=16)
        bulk_frame.grid(row=1, column=0, padx=18, pady=(10, 20), sticky="nsew")
        bulk_frame.columnconfigure(1, weight=1)

        self.bulk_title = ctk.CTkLabel(
            bulk_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f1f3ff",
        )
        self.bulk_title.grid(row=0, column=0, columnspan=4, padx=16, pady=(14, 10), sticky="w")

        form = ctk.CTkFrame(bulk_frame, fg_color="transparent")
        form.grid(row=1, column=0, columnspan=4, padx=16, pady=4, sticky="ew")
        for i in range(8):
            form.columnconfigure(i, weight=1 if i in (4, 5) else 0)

        entries = [
            ("stat_level", self.level_var),
            ("stat_potential", self.potential_var),
            ("stat_skill", self.skill_var),
            ("stat_living_skill", self.living_skill_var),
            ("stat_strength", self.strength_var),
            ("stat_endurance", self.endurance_var),
            ("stat_agility", self.agility_var),
            ("stat_precision", self.precision_var),
            ("stat_intelligence", self.intelligence_var),
            ("stat_willpower", self.willpower_var),
        ]

        self.bulk_labels: Dict[str, ctk.CTkLabel] = {}
        self.bulk_entries: Dict[str, ctk.CTkEntry] = {}

        for idx, (name_key, var) in enumerate(entries[:4]):
            column = idx * 2
            label = ctk.CTkLabel(form, text="", text_color="#cbd5ff")
            entry = ctk.CTkEntry(form, textvariable=var, width=100)
            label.grid(row=0, column=column, padx=(0, 6), pady=6, sticky="w")
            entry.grid(row=0, column=column + 1, padx=(0, 18), pady=6, sticky="w")
            self.bulk_labels[name_key] = label
            self.bulk_entries[name_key] = entry

        for idx, (name_key, var) in enumerate(entries[4:]):
            row = 1 + idx // 4
            column = (idx % 4) * 2
            label = ctk.CTkLabel(form, text="", text_color="#cbd5ff")
            entry = ctk.CTkEntry(form, textvariable=var, width=100)
            label.grid(row=row, column=column, padx=(0, 6), pady=6, sticky="w")
            entry.grid(row=row, column=column + 1, padx=(0, 18), pady=6, sticky="w")
            self.bulk_labels[name_key] = label
            self.bulk_entries[name_key] = entry

        self.mode_label = ctk.CTkLabel(bulk_frame, text="", text_color="#cbd5ff")
        self.mode_menu = ctk.CTkOptionMenu(
            bulk_frame,
            values=[],
            command=self._on_mode_change,
            width=160,
        )
        self.apply_btn = ctk.CTkButton(
            bulk_frame,
            text="",
            command=self.on_apply_selected,
            fg_color="#10b981",
            hover_color="#059669",
            width=180,
        )
        self.hint_label = ctk.CTkLabel(
            bulk_frame,
            text="",
            wraplength=360,
            text_color="#9aa4d1",
            anchor="w",
            justify="left",
        )

        self.mode_label.grid(row=2, column=0, padx=16, pady=(12, 6), sticky="w")
        self.mode_menu.grid(row=2, column=1, padx=(0, 16), pady=(12, 6), sticky="w")
        self.apply_btn.grid(row=2, column=2, padx=(16, 16), pady=(12, 6), sticky="e")
        self.hint_label.grid(row=3, column=0, columnspan=4, padx=16, pady=(6, 16), sticky="w")

    def _build_status_bar(self) -> None:
        bar = ctk.CTkFrame(self, corner_radius=0, fg_color="#161b2a")
        bar.grid(row=2, column=0, sticky="ew")
        self.status_label = ctk.CTkLabel(bar, textvariable=self.status_var, text_color="#cbd5ff")
        self.status_label.pack(anchor="w", padx=18, pady=6)

    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _on_language_change(self, selection: str) -> None:
        language = self.language_display_to_key.get(selection)
        if not language:
            return
        if language == self.translator.current:
            return
        self.translator.set_language(language)
        self._apply_translations()
        if self.model.data:
            self.refresh_table()
        else:
            self.set_status(self.tr("status_ready"))

    def _apply_translations(self) -> None:
        app_title = self.tr("app_title")
        if self.model.path:
            title = f"{app_title} — {os.path.basename(self.model.path)}"
        else:
            title = app_title
        self.title(title)
        self.title_label.configure(text=self.tr("title_label"))
        self.open_btn.configure(text=self.tr("btn_open"))
        self.save_btn.configure(text=self.tr("btn_save"))
        self.about_btn.configure(text=self.tr("btn_about"))
        self.language_label.configure(text=self.tr("language_menu_label"))
        self.language_menu.configure(values=list(self.language_display_to_key.keys()))
        self.language_menu.set(self.language_key_to_display[self.translator.current])

        self.list_header_label.configure(text=self.tr("list_header"))
        self.show_player_chk.configure(text=self.tr("show_player_only"))
        self.underscore_chk.configure(text=self.tr("only_underscore"))
        self.search_entry.configure(placeholder_text=self.tr("search_placeholder"))
        self.level_entry.configure(placeholder_text=self.tr("min_level_placeholder"))
        self.apply_filter_btn.configure(text=self.tr("apply_filters"))
        self.select_label.configure(text=self.tr("column_select"))
        for key, button in self.header_buttons.items():
            button.configure(text=self.tr(key))

        self.meta_title.configure(text=self.tr("global_section_title"))
        self.gold_label.configure(text=self.tr("gold_label"))
        self.rep_label.configure(text=self.tr("rep_label"))
        self.update_meta_btn.configure(text=self.tr("update_meta_btn"))
        self.save_as_btn.configure(text=self.tr("save_as_btn"))

        self.bulk_title.configure(text=self.tr("bulk_section_title"))
        for key, label in self.bulk_labels.items():
            label.configure(text=self.tr(key))
        self.mode_label.configure(text=self.tr("mode_label"))
        self.apply_btn.configure(text=self.tr("apply_selected_btn"))
        self.hint_label.configure(text=self.tr("hint_text"))

        self._update_mode_menu()

    def _update_mode_menu(self) -> None:
        add_display = self.tr("mode_add")
        set_display = self.tr("mode_set")
        values = [add_display, set_display]
        self.mode_display_to_key = {
            add_display: "add",
            set_display: "set",
        }
        self.mode_menu.configure(values=values)
        current_mode = self.bulk_mode_var.get()
        display = self._mode_display_for_key(current_mode)
        if display not in values:
            display = add_display
            self.bulk_mode_var.set("add")
        self.mode_menu.set(display)

    def _mode_display_for_key(self, key: str) -> str:
        if key == "set":
            return self.tr("mode_set")
        return self.tr("mode_add")

    def _build_row_frame(self, position: int, idx: int, summary: Dict[str, object], highlight: bool) -> None:
        bg_color = MATCH_ROW_COLOR if highlight else (EVEN_ROW_COLOR if position % 2 == 0 else ODD_ROW_COLOR)
        row_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=bg_color,
            corner_radius=10,
            border_width=2 if idx in self.selected_indices else 0,
            border_color=SELECTED_BORDER_COLOR,
        )
        row_frame.grid(row=position, column=0, sticky="ew", padx=6, pady=4)
        for column in range(len(COLUMN_DEFINITIONS) + 1):
            row_frame.grid_columnconfigure(column, weight=1 if column == 5 else 0)

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
            summary.get("id"),
            summary.get("unitId"),
            summary.get("team"),
            summary.get("unitname"),
            summary.get("level"),
            summary.get("potentialPoint"),
            summary.get("skillPoint"),
            summary.get("livingSkillPoint"),
        ]
        for column_index, value in enumerate(values, start=1):
            _, _, width = COLUMN_DEFINITIONS[column_index - 1]
            text = "" if value is None else str(value)
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                width=width,
                anchor="w",
                text_color="#e5e7ff",
            )
            label.grid(row=0, column=column_index, padx=(0, 12), pady=8, sticky="w")

    def _clear_roster_widgets(self) -> None:
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.row_vars.clear()
        self.row_frames.clear()

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
        self.set_status(self.tr("status_selected", count=len(self.selected_indices)))

    def on_open(self):
        path = filedialog.askopenfilename(
            title=self.tr("dialog_open_title"),
            filetypes=[
                (self.tr("dialog_open_filter"), "*.dat *.json"),
                (self.tr("dialog_all_files"), "*.*"),
            ],
            initialfile=DEFAULT_FILENAME,
        )
        if path:
            self.load_path(path)

    def on_save(self):
        if not self.model.data:
            messagebox.showwarning(self.tr("app_title"), self.tr("message_load_first"))
            return
        try:
            out_path = self.model.save(make_backup=True)
            messagebox.showinfo(self.tr("app_title"), self.tr("message_saved", path=out_path))
            self.set_status(self.tr("status_saved"))
        except Exception as exc:
            messagebox.showerror(self.tr("app_title"), self.tr("message_save_failed", error=exc))
            self.set_status(self.tr("status_save_failed"))

    def on_save_as(self):
        if not self.model.data:
            messagebox.showwarning(self.tr("app_title"), self.tr("message_load_first"))
            return
        path = filedialog.asksaveasfilename(
            title=self.tr("dialog_save_as_title"),
            defaultextension=".dat",
            initialfile=self.tr("dialog_save_as_default_name"),
            filetypes=[
                (self.tr("dialog_save_as_dat"), "*.dat"),
                (self.tr("dialog_save_as_json"), "*.json"),
                (self.tr("dialog_all_files"), "*.*"),
            ],
        )
        if not path:
            return
        try:
            out_path = self.model.save(out_path=path, make_backup=True)
            messagebox.showinfo(self.tr("app_title"), self.tr("message_saved_as", path=out_path))
            self.set_status(self.tr("status_save_as_done"))
        except Exception as exc:
            messagebox.showerror(self.tr("app_title"), self.tr("message_save_failed", error=exc))
            self.set_status(self.tr("status_save_failed"))

    def on_about(self):
        messagebox.showinfo(self.tr("app_title"), self.tr("about_message"))

    def load_path(self, path):
        ok = self.model.load(path)
        if not ok:
            raise RuntimeError("載入失敗")
        self.gold_var.set(str(self.model.get_gold()))
        self.rep_var.set(str(self.model.get_rep()))
        self.refresh_table()
        self._apply_translations()
        self.set_status(self.tr("status_loaded", path=path))

    def refresh_table(self):
        self._clear_roster_widgets()

        only_team = self.model.player_team if self.show_only_player_var.get() else None
        search = self.search_var.get().strip().lower()
        min_level = safe_int(self.filter_min_level_var.get(), 0) or 0
        only_underscore = self.only_underscore_var.get()

        rows: List[Tuple[int, Dict[str, object]]] = []
        for idx, npc in self.model.iter_roster(only_team=only_team):
            summary = self.model.npc_summary(npc)
            name = str(summary.get("unitname") or "")
            level = summary.get("level") or 0
            if only_underscore and "_" not in name:
                continue
            if search and search not in name.lower():
                continue
            if level < min_level:
                continue
            rows.append((idx, summary))

        if self.sort_column:
            key = self.sort_column

            def key_func(item):
                summary = item[1]
                value = summary.get(key)
                try:
                    return (0, int(value))
                except Exception:
                    return (1, str(value))

            rows.sort(key=key_func, reverse=self.sort_reverse)
        else:
            rows.sort(
                key=lambda item: (
                    item[1].get("team", 0),
                    -(item[1].get("level") or 0),
                    str(item[1].get("unitname") or ""),
                )
            )

        self.current_rows = rows
        valid_indices = {idx for idx, _ in rows}
        self.selected_indices.intersection_update(valid_indices)

        for position, (idx, summary) in enumerate(rows):
            name = str(summary.get("unitname") or "")
            highlight = bool(search and search in name.lower())
            self._build_row_frame(position, idx, summary, highlight)

        self.set_status(self.tr("status_showing", total=len(rows), selected=len(self.selected_indices)))

    def on_update_meta(self):
        if not self.model.data:
            messagebox.showwarning(self.tr("app_title"), self.tr("message_load_first"))
            return
        self.model.set_gold(self.gold_var.get())
        self.model.set_rep(self.rep_var.get())
        messagebox.showinfo(self.tr("app_title"), self.tr("message_update_meta_done"))
        self.set_status(self.tr("status_meta_updated"))

    def on_apply_selected(self):
        if not self.model.data:
            messagebox.showwarning(self.tr("app_title"), self.tr("message_load_first"))
            return
        if not self.selected_indices:
            messagebox.showwarning(self.tr("app_title"), self.tr("message_select_first"))
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
            messagebox.showwarning(self.tr("app_title"), self.tr("message_enter_field"))
            return

        mode = self.bulk_mode_var.get()
        count = 0
        for idx in sorted(self.selected_indices):
            if idx < 0 or idx >= len(self.model.npcs):
                continue
            npc = self.model.npcs[idx]
            for key, value in fields:
                parsed = safe_int(value, None)
                if parsed is None:
                    continue
                old = npc.get(key) or 0
                if mode == "add":
                    npc[key] = max(0, old + parsed)
                else:
                    npc[key] = max(0, parsed)
            count += 1

        self.refresh_table()
        messagebox.showinfo(self.tr("app_title"), self.tr("message_apply_done", count=count))
        self.set_status(self.tr("status_batch_done", count=count))

    def on_sort_column(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.refresh_table()

    def _on_mode_change(self, selection: str) -> None:
        mode = self.mode_display_to_key.get(selection, "add")
        self.bulk_mode_var.set(mode)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
