from tkinter import ttk


def preferred_font_family():
    """Return the best available San Francisco style font family."""
    try:
        import tkinter.font as tkfont

        families = set(tkfont.families())
        # San Francisco variants that may exist on macOS
        for candidate in (
            ".SF NS Text",
            ".SF NS Display",
            "SF Pro Text",
            "SF Pro Display",
            "San Francisco",
        ):
            if candidate in families:
                return candidate
        if "Helvetica Neue" in families:
            return "Helvetica Neue"
        if "Arial" in families:
            return "Arial"
    except Exception:
        pass
    return "TkDefaultFont"


def init_style(root):
    """Initialize ttk.Style with Apple inspired fonts and spacing."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    family = preferred_font_family()
    base_font = (family, 13)
    header_font = (family, 14, "bold")

    style.configure("Treeview", font=base_font, rowheight=32)
    style.configure("Treeview.Heading", font=header_font)

    padding = (12, 6)
    style.configure("TButton", font=base_font, padding=padding)
    style.configure("TLabel", font=base_font)
    style.configure("TEntry", font=base_font, padding=padding)
    style.configure("TCheckbutton", font=base_font)
    style.configure("TRadiobutton", font=base_font)

    return style


def apply_palette(root, style, kind):
    """Apply the Apple inspired light or dark palette."""
    k = str(kind).lower()
    family = preferred_font_family()
    if k in ("dark", "\u6697\u8272"):
        bg = "#2b2b2b"
        fg = "#f5f5f7"
        panel = "#3a3a3c"
        accent = "#0a84ff"
        alt = "#333336"
        hint = "#8e8e93"
        accent_pressed = "#0060df"
        button_disabled_bg = "#48484a"
    else:
        bg = "#f8f8f8"
        fg = "#1c1c1e"
        panel = "#ffffff"
        accent = "#007aff"
        alt = "#eef0f5"
        hint = "#6e6e73"
        accent_pressed = "#0056d8"
        button_disabled_bg = "#d1d1d6"

    root.configure(bg=bg)
    style.configure(".", background=bg, foreground=fg)

    style.configure("Card.TFrame", background=panel, relief="flat")
    style.configure(
        "CardTitle.TLabel",
        background=panel,
        foreground=fg,
        font=(family, 15, "bold"),
    )
    style.configure("Hint.TLabel", background=panel, foreground=hint)

    style.configure("TButton", background=accent, foreground="white")
    style.map(
        "TButton",
        background=[
            ("pressed", accent_pressed),
            ("active", accent),
            ("disabled", button_disabled_bg),
        ],
        foreground=[("disabled", hint)],
    )

    style.map(
        "Treeview",
        background=[("selected", accent)],
        foreground=[("selected", "white")],
    )

    style.configure("TNotebook", background=bg, borderwidth=0)
    style.configure("TNotebook.Tab", background=alt, foreground=fg, padding=(14, 8))
    style.map(
        "TNotebook.Tab",
        background=[("selected", panel), ("!selected", alt)],
        foreground=[("selected", fg), ("!selected", fg)],
    )

    style.configure("TLabelframe", background=panel, foreground=fg)
    style.configure(
        "TLabelframe.Label",
        background=panel,
        foreground=fg,
        font=(family, 14, "bold"),
    )

    tag_colors = {
        "even": alt,
        "odd": panel,
        "match": "#d0e7ff" if k not in ("dark", "\u6697\u8272") else "#163a63",
    }
    return tag_colors


def card(parent, title=None, **pack):
    """Create a card container with generous padding and bold title."""
    frame = ttk.Frame(parent, style="Card.TFrame", padding=(18, 16, 18, 18))
    if not pack:
        pack = {"fill": "x", "pady": (0, 12)}
    frame.pack(**pack)
    if title:
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
    return frame
