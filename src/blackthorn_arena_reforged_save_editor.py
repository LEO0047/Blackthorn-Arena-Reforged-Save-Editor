
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blackthorn Arena: Reforged - Save Editor (JSON)
Author: ChatGPT
Tested with JSON save provided by user.
Usage:
    python blackthorn_arena_reforged_save_editor.py
Features:
- Load JSON save (sav.dat) and parse gladiators & meta (wealth, reputation)
- Show roster (default: team == 0, likely player's team) with filter/search
- Edit selected gladiators' level, potentialPoint, skillPoint, livingSkillPoint
- Bulk-add or set values
- Edit top-level wealth (gold) & reputation
- Backup original file on save
- Save As... to avoid overwriting
Notes:
- The app assumes save is a single JSON object (as observed).
- "team == 0" seemed to correspond to the player's roster in our sample.
- You can toggle to view/edit ALL NPCs if needed.
DISCLAIMER: Back up your save before using. Use at your own risk.
"""
import json
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ui_style import init_style, apply_palette as style_apply_palette, card as style_card

APP_TITLE = "Blackthorn Arena: Reforged - Save Editor (JSON)"
DEFAULT_FILENAME = "sav.dat"

def safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default

class SaveModel:
    def __init__(self):
        self.path = None
        self.data = None
        self.npcs = []
        self.gold_key = 'wealth'           # observed top-level wealth key
        self.reputation_key = 'reputation' # observed top-level rep key
        self.team_guess = 0                # team==0 looked like player's roster

    def load(self, path):
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.npcs = self.data.get('npcs', [])
        if isinstance(self.npcs, list):
            # filter out dead characters
            self.npcs = [npc for npc in self.npcs if not self.is_dead(npc)]
        else:
            self.npcs = []
        # ensure backing data matches filtered list
        self.data['npcs'] = self.npcs
        return True

    def save(self, out_path=None, make_backup=True):
        if self.data is None or self.path is None:
            raise RuntimeError("No save loaded")
        src = self.path
        dst = out_path or self.path
        if make_backup and os.path.exists(src):
            ts = time.strftime("%Y%m%d-%H%M%S")
            backup = f"{src}.bak.{ts}"
            try:
                with open(src, "rb") as rf, open(backup, "wb") as wf:
                    wf.write(rf.read())
            except Exception as e:
                print("WARN: failed to create backup:", e)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, separators=(",", ":"), indent=None)
        return dst

    def get_gold(self):
        return self.data.get(self.gold_key)

    def set_gold(self, value):
        self.data[self.gold_key] = safe_int(value, 0)

    def get_rep(self):
        return self.data.get(self.reputation_key)

    def set_rep(self, value):
        self.data[self.reputation_key] = safe_int(value, 0)

    def iter_roster(self, only_team=None):
        """
        Yield tuples: (index_in_npcs, npc_dict)
        If only_team is None -> iterate all; else only team==only_team.
        """
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
        """Return True if the given NPC appears to be dead."""
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

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x640")
        self.minsize(960, 560)

        # style / theme
        self.style = init_style(self)
        self.theme_var = tk.StringVar(value="Light")
        self.tag_colors = {}
        self.apply_palette(self.theme_var.get())

        self.model = SaveModel()

        # UI state
        self.show_all_var = tk.BooleanVar(value=False)
        self.search_var = tk.StringVar(value="")
        self.filter_min_level_var = tk.StringVar(value="")
        self.gold_var = tk.StringVar(value="")
        self.rep_var = tk.StringVar(value="")

        # editor fields
        self.level_var = tk.StringVar(value="")
        self.potential_var = tk.StringVar(value="")
        self.skill_var = tk.StringVar(value="")
        self.living_skill_var = tk.StringVar(value="")

        self.bulk_mode_var = tk.StringVar(value="add")  # "add" or "set"

        self.create_menu()
        self.create_widgets()

        # try to auto-load DEFAULT_FILENAME in cwd if present
        if os.path.exists(DEFAULT_FILENAME):
            try:
                self.load_path(DEFAULT_FILENAME)
            except Exception as e:
                print("Auto-load failed:", e)

    # ---------- UI ----------
    def create_menu(self):
        mbar = tk.Menu(self)
        filem = tk.Menu(mbar, tearoff=False)
        filem.add_command(label="Open Save...", command=self.on_open)
        filem.add_command(label="Save", command=self.on_save)
        filem.add_command(label="Save As...", command=self.on_save_as)
        filem.add_separator()
        filem.add_command(label="Quit", command=self.on_quit)
        mbar.add_cascade(label="File", menu=filem)

        viewm = tk.Menu(mbar, tearoff=False)
        viewm.add_radiobutton(label="Light Theme", variable=self.theme_var,
                               value="Light", command=self.on_theme_change)
        viewm.add_radiobutton(label="Dark Theme", variable=self.theme_var,
                               value="Dark", command=self.on_theme_change)
        mbar.add_cascade(label="View", menu=viewm)

        helpm = tk.Menu(mbar, tearoff=False)
        helpm.add_command(label="About", command=self.on_about)
        mbar.add_cascade(label="Help", menu=helpm)

        self.config(menu=mbar)

    def create_widgets(self):
        root = ttk.Frame(self, padding=8)
        root.pack(fill="both", expand=True)

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True)

        # ----- General Tab -----
        tab_gen = ttk.Frame(nb)
        nb.add(tab_gen, text="General")
        meta = style_card(tab_gen, "Meta")
        ttk.Label(meta, text="Wealth (Gold):").pack(side="left")
        ttk.Entry(meta, textvariable=self.gold_var, width=8).pack(side="left", padx=(4,10))
        ttk.Label(meta, text="Reputation:").pack(side="left")
        ttk.Entry(meta, textvariable=self.rep_var, width=8).pack(side="left", padx=(4,10))
        ttk.Button(meta, text="Update Meta", command=self.on_update_meta).pack(side="left", padx=(4,8))

        # ----- Gladiators Tab -----
        tab_glad = ttk.Frame(nb)
        nb.add(tab_glad, text="Gladiators")

        filters = style_card(tab_glad, "Filters")
        ttk.Checkbutton(filters, text="Show ALL NPCs (not just team 0)",
                        variable=self.show_all_var, command=self.refresh_table).pack(side="left", padx=(8,8))
        ttk.Label(filters, text="Search name:").pack(side="left")
        ttk.Entry(filters, textvariable=self.search_var, width=20).pack(side="left", padx=(4,10))
        ttk.Label(filters, text="Min level:").pack(side="left")
        ttk.Entry(filters, textvariable=self.filter_min_level_var, width=6).pack(side="left", padx=(4,10))
        ttk.Button(filters, text="Apply Filters", command=self.refresh_table).pack(side="left", padx=(4,12))

        table_card = style_card(tab_glad, "Roster")
        table_frame = ttk.Frame(table_card)
        table_frame.pack(fill="both", expand=True)

        columns = ("idx","id","unitId","team","unitname","level","potentialPoint","skillPoint","livingSkillPoint")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        for col, w in zip(columns, (60,60,60,60,280,60,120,90,120)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)
        yscroll.pack(side="right", fill="y")

        editor = style_card(tab_glad, "Edit Selected Gladiators")
        grid = ttk.Frame(editor)
        grid.pack(fill="x", padx=8, pady=4)

        r=0
        ttk.Label(grid, text="Level:").grid(row=r, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.level_var, width=8).grid(row=r, column=1, sticky="w", padx=4)
        ttk.Label(grid, text="Potential Points:").grid(row=r, column=2, sticky="w")
        ttk.Entry(grid, textvariable=self.potential_var, width=8).grid(row=r, column=3, sticky="w", padx=4)
        ttk.Label(grid, text="Skill Points:").grid(row=r, column=4, sticky="w")
        ttk.Entry(grid, textvariable=self.skill_var, width=8).grid(row=r, column=5, sticky="w", padx=4)
        ttk.Label(grid, text="Living Skill Points:").grid(row=r, column=6, sticky="w")
        ttk.Entry(grid, textvariable=self.living_skill_var, width=8).grid(row=r, column=7, sticky="w", padx=4)

        r+=1
        ttk.Label(grid, text="Bulk Mode:").grid(row=r, column=0, sticky="w", pady=(6,0))
        ttk.Radiobutton(grid, text="Add (±)", variable=self.bulk_mode_var, value="add").grid(row=r, column=1, sticky="w", pady=(6,0))
        ttk.Radiobutton(grid, text="Set (=)", variable=self.bulk_mode_var, value="set").grid(row=r, column=2, sticky="w", pady=(6,0))
        ttk.Button(grid, text="Apply to Selected", command=self.on_apply_selected).grid(row=r, column=3, sticky="w", padx=8, pady=(6,0))

        ttk.Label(editor, text="Hints: Use modest numbers first (e.g., +5 to +10 points) to avoid breaking balance. Back up your save!").pack(anchor="w", padx=8, pady=(2,8))

        # ----- Placeholder Tabs -----
        tab_traits = ttk.Frame(nb)
        nb.add(tab_traits, text="Traits")
        style_card(tab_traits, "Coming soon")

        tab_items = ttk.Frame(nb)
        nb.add(tab_items, text="Items")
        style_card(tab_items, "Coming soon")

        tab_arena = ttk.Frame(nb)
        nb.add(tab_arena, text="Arena")
        style_card(tab_arena, "Coming soon")

    # ---------- Menu actions ----------
    def on_open(self):
        path = filedialog.askopenfilename(
            title="Open Blackthorn Arena save (JSON)",
            filetypes=[("JSON files","*.json"),("All files","*.*")],
            initialfile=DEFAULT_FILENAME
        )
        if path:
            self.load_path(path)

    def on_save(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "Load a save first.")
            return
        try:
            out = self.model.save(make_backup=True)
            messagebox.showinfo(APP_TITLE, f"Saved to:\n{out}\nBackup created alongside original.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Save failed:\n{e}")

    def on_save_as(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "Load a save first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save As...",
            defaultextension=".dat",
            initialfile="sav_edited.dat",
            filetypes=[("DAT","*.dat"),("JSON","*.json"),("All files","*.*")]
        )
        if path:
            try:
                out = self.model.save(out_path=path, make_backup=True)
                messagebox.showinfo(APP_TITLE, f"Saved to:\n{out}\nBackup created for original.")
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"Save failed:\n{e}")

    def on_quit(self):
        self.destroy()

    def on_about(self):
        messagebox.showinfo(APP_TITLE, "Simple JSON save editor for Blackthorn Arena: Reforged.\nBack up your save before editing.")

    # ---------- Data Loading ----------
    def load_path(self, path):
        ok = self.model.load(path)
        if not ok:
            raise RuntimeError("Failed to load save file")
        # populate meta
        self.gold_var.set(str(self.model.get_gold()))
        self.rep_var.set(str(self.model.get_rep()))
        self.refresh_table()
        self.title(f"{APP_TITLE}  —  {os.path.basename(path)}")

    def refresh_table(self):
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)

        only_team = None if self.show_all_var.get() else self.model.team_guess
        search = self.search_var.get().strip().lower()
        minlvl = safe_int(self.filter_min_level_var.get(), 0)

        for n, (idx, npc) in enumerate(self.model.iter_roster(only_team=only_team)):
            s = self.model.npc_summary(npc)
            name = str(s.get('unitname') or "")
            lvl = s.get('level') or 0
            if search and search not in name.lower():
                continue
            if lvl < minlvl:
                continue
            values = (
                idx, s.get('id'), s.get('unitId'), s.get('team'),
                name, lvl, s.get('potentialPoint'), s.get('skillPoint'),
                s.get('livingSkillPoint')
            )
            tag = "even" if n % 2 == 0 else "odd"
            tags = (tag,)
            if search and search in name.lower():
                tags = tags + ("match",)
            self.tree.insert("", "end", iid=str(idx), values=values, tags=tags)

        self.tree.tag_configure("even", background=self.tag_colors.get("even"))
        self.tree.tag_configure("odd", background=self.tag_colors.get("odd"))
        self.tree.tag_configure("match", background=self.tag_colors.get("match"))

    def on_update_meta(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "Load a save first.")
            return
        self.model.set_gold(self.gold_var.get())
        self.model.set_rep(self.rep_var.get())
        messagebox.showinfo(APP_TITLE, "Meta updated in memory. Use File → Save to write changes.")

    def on_apply_selected(self):
        if not self.model.data:
            messagebox.showwarning(APP_TITLE, "Load a save first.")
            return

        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(APP_TITLE, "Select at least one gladiator in the table.")
            return

        # Prepare edits
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
            messagebox.showwarning(APP_TITLE, "Enter at least one field value to apply.")
            return

        mode = self.bulk_mode_var.get()  # "add" or "set"
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
        messagebox.showinfo(APP_TITLE, f"Applied changes to {count} gladiator(s). Remember to Save!")

    # ---------- Theme ----------
    def on_theme_change(self):
        self.apply_palette(self.theme_var.get())
        self.refresh_table()

    def apply_palette(self, kind):
        self.tag_colors = style_apply_palette(self, self.style, kind)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
