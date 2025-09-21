"""Modern GUI sample built with CustomTkinter.

Installation:
    pip install customtkinter

Run:
    python modern_customtk_app.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox


DATA_FIELDS = ("name", "title", "faction", "notes")
DEFAULT_DATA = [
    {
        "name": "Aldric",
        "title": "Arena Champion",
        "faction": "Blackthorn",
        "notes": "A veteran gladiator known for his strategic prowess.",
    },
    {
        "name": "Lyra",
        "title": "Master Tactician",
        "faction": "Silverclad",
        "notes": "Prefers agility and precision strikes in the arena.",
    },
    {
        "name": "Corvin",
        "title": "Quartermaster",
        "faction": "Free Cities",
        "notes": "Keeps the supplies flowing and morale high for the team.",
    },
]


@dataclass
class EntryData:
    name: str = ""
    title: str = ""
    faction: str = ""
    notes: str = ""

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, payload: dict) -> "EntryData":
        data = {field: str(payload.get(field, "")) for field in DATA_FIELDS}
        return cls(**data)


class ModernApp(ctk.CTk):
    """A modern master-detail editor example built with CustomTkinter."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        super().__init__()
        self.title("Blackthorn Manager")
        self.geometry("960x600")
        self.minsize(820, 520)

        # data
        self._data: List[EntryData] = [EntryData.from_json(item) for item in DEFAULT_DATA]
        self._selected_index: Optional[int] = 0
        self._current_path: Optional[Path] = None

        # configure layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_title_bar()
        self._build_main_area()
        self._build_status_bar()

        self._refresh_list()
        self._select_index(0)
        self._set_status("Ready")

    # ------------------------------------------------------------------
    # layout builders
    def _build_title_bar(self) -> None:
        title_bar = ctk.CTkFrame(self, corner_radius=0)
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.columnconfigure(0, weight=1)
        title_bar.columnconfigure(1, weight=0)

        title_label = ctk.CTkLabel(
            title_bar,
            text="Blackthorn Arena Data Manager",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        button_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        button_frame.grid(row=0, column=1, padx=12, pady=12, sticky="e")

        load_button = ctk.CTkButton(button_frame, text="載入資料", command=self._action_load)
        save_button = ctk.CTkButton(button_frame, text="儲存資料", command=self._action_save)
        load_button.grid(row=0, column=0, padx=(0, 8))
        save_button.grid(row=0, column=1)

    def _build_main_area(self) -> None:
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, padx=16, pady=12, sticky="nsew")
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_list_panel(main)
        self._build_form_panel(main)

    def _build_list_panel(self, parent: ctk.CTkFrame) -> None:
        list_container = ctk.CTkFrame(parent, corner_radius=12)
        list_container.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        list_container.rowconfigure(1, weight=1)

        header = ctk.CTkLabel(list_container, text="角色列表", font=ctk.CTkFont(size=16, weight="bold"))
        header.grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")

        self._list_frame = ctk.CTkScrollableFrame(list_container, width=220, corner_radius=8)
        self._list_frame.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsw")

        button_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        button_bar.grid(row=2, column=0, padx=12, pady=(0, 16), sticky="ew")
        button_bar.columnconfigure((0, 1), weight=1)

        add_button = ctk.CTkButton(button_bar, text="新增", command=self._action_add)
        delete_button = ctk.CTkButton(button_bar, text="刪除", command=self._action_delete)
        add_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        delete_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def _build_form_panel(self, parent: ctk.CTkFrame) -> None:
        form_container = ctk.CTkFrame(parent, corner_radius=12)
        form_container.grid(row=0, column=1, sticky="nsew")
        form_container.columnconfigure(0, weight=1)

        header = ctk.CTkLabel(form_container, text="角色資訊", font=ctk.CTkFont(size=16, weight="bold"))
        header.grid(row=0, column=0, padx=20, pady=(16, 6), sticky="w")

        self._name_var = ctk.StringVar()
        self._title_var = ctk.StringVar()
        self._faction_var = ctk.StringVar()
        self._notes_widget = ctk.CTkTextbox(form_container, height=200)

        self._add_labeled_entry(form_container, "姓名", self._name_var, 1)
        self._add_labeled_entry(form_container, "頭銜", self._title_var, 2)
        self._add_labeled_entry(form_container, "陣營", self._faction_var, 3)

        notes_label = ctk.CTkLabel(form_container, text="備註")
        notes_label.grid(row=4, column=0, padx=20, pady=(12, 4), sticky="w")
        self._notes_widget.grid(row=5, column=0, padx=20, pady=(0, 12), sticky="nsew")
        form_container.rowconfigure(5, weight=1)

        action_bar = ctk.CTkFrame(form_container, fg_color="transparent")
        action_bar.grid(row=6, column=0, padx=20, pady=(0, 16), sticky="e")

        apply_button = ctk.CTkButton(action_bar, text="套用變更", command=self._action_apply)
        apply_button.grid(row=0, column=0, padx=(0, 12))

    def _add_labeled_entry(self, parent: ctk.CTkFrame, label: str, var: ctk.StringVar, row: int) -> None:
        lbl = ctk.CTkLabel(parent, text=label)
        entry = ctk.CTkEntry(parent, textvariable=var)
        lbl.grid(row=row, column=0, padx=20, pady=(8, 2), sticky="w")
        entry.grid(row=row, column=0, padx=20, pady=(0, 4), sticky="ew")

    def _build_status_bar(self) -> None:
        status_bar = ctk.CTkFrame(self, corner_radius=0)
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.columnconfigure(0, weight=1)

        self._status_var = ctk.StringVar(value="準備就緒")
        status_label = ctk.CTkLabel(status_bar, textvariable=self._status_var, anchor="w")
        status_label.grid(row=0, column=0, padx=16, pady=6, sticky="ew")

    # ------------------------------------------------------------------
    # data helpers
    def _refresh_list(self) -> None:
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        for index, entry in enumerate(self._data):
            button = ctk.CTkButton(
                self._list_frame,
                text=f"{entry.name or '未命名'}\n{entry.title}",
                width=180,
                anchor="w",
                command=lambda idx=index: self._select_index(idx),
            )
            button.grid(row=index, column=0, padx=8, pady=6, sticky="ew")

    def _select_index(self, index: Optional[int]) -> None:
        if index is None or not (0 <= index < len(self._data)):
            self._selected_index = None
            self._clear_form()
            return

        self._selected_index = index
        entry = self._data[index]
        self._name_var.set(entry.name)
        self._title_var.set(entry.title)
        self._faction_var.set(entry.faction)
        self._notes_widget.delete("1.0", "end")
        self._notes_widget.insert("1.0", entry.notes)
        self._set_status(f"已選擇：{entry.name or '未命名'}")

    def _clear_form(self) -> None:
        self._name_var.set("")
        self._title_var.set("")
        self._faction_var.set("")
        self._notes_widget.delete("1.0", "end")

    def _gather_form(self) -> EntryData:
        return EntryData(
            name=self._name_var.get().strip(),
            title=self._title_var.get().strip(),
            faction=self._faction_var.get().strip(),
            notes=self._notes_widget.get("1.0", "end").strip(),
        )

    def _set_status(self, message: str) -> None:
        self._status_var.set(message)

    # ------------------------------------------------------------------
    # actions
    def _action_add(self) -> None:
        self._data.append(EntryData(name="新角色", title="", faction="", notes=""))
        self._refresh_list()
        self._select_index(len(self._data) - 1)
        self._set_status("已新增角色。")

    def _action_delete(self) -> None:
        if self._selected_index is None:
            self._set_status("請先選擇要刪除的角色。")
            return

        name = self._data[self._selected_index].name or "未命名"
        if messagebox.askyesno("確認刪除", f"確定要刪除『{name}』嗎？"):
            del self._data[self._selected_index]
            self._refresh_list()
            self._select_index(0 if self._data else None)
            self._set_status(f"已刪除角色：{name}")

    def _action_apply(self) -> None:
        if self._selected_index is None:
            self._set_status("請先選擇角色。")
            return

        self._data[self._selected_index] = self._gather_form()
        self._refresh_list()
        self._set_status("變更已套用。")

    def _action_load(self) -> None:
        path_str = filedialog.askopenfilename(
            title="選擇資料檔",
            filetypes=(("JSON Files", "*.json"), ("All Files", "*")),
        )
        if not path_str:
            return

        path = Path(path_str)
        try:
            with path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as exc:
            messagebox.showerror("載入失敗", f"讀取檔案時發生錯誤：\n{exc}")
            self._set_status("載入失敗。")
            return

        if not isinstance(payload, list):
            messagebox.showerror("格式錯誤", "檔案格式不正確，需為角色列表。")
            self._set_status("載入失敗。")
            return

        self._data = [EntryData.from_json(item) for item in payload]
        self._current_path = path
        self._refresh_list()
        self._select_index(0 if self._data else None)
        self._set_status(f"已載入檔案：{path.name}")

    def _action_save(self) -> None:
        if self._current_path is None:
            self._action_save_as()
            return

        self._write_file(self._current_path)

    def _action_save_as(self) -> None:
        path_str = filedialog.asksaveasfilename(
            title="儲存資料檔",
            defaultextension=".json",
            filetypes=(("JSON Files", "*.json"), ("All Files", "*")),
        )
        if not path_str:
            return
        path = Path(path_str)
        self._write_file(path)
        self._current_path = path

    def _write_file(self, path: Path) -> None:
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump([entry.to_json() for entry in self._data], f, ensure_ascii=False, indent=2)
        except Exception as exc:
            messagebox.showerror("儲存失敗", f"寫入檔案時發生錯誤：\n{exc}")
            self._set_status("儲存失敗。")
            return

        self._set_status(f"已儲存至 {path.name}")


def main() -> None:
    app = ModernApp()
    app.mainloop()


if __name__ == "__main__":
    main()
