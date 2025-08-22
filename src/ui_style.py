import tkinter as tk
from tkinter import ttk

def prefers_msjh():
    """Return Microsoft JhengHei font if available (commonly on Windows)."""
    try:
        import tkinter.font as tkfont
        fams = set(tkfont.families())
        if "Microsoft JhengHei UI" in fams:
            return "Microsoft JhengHei UI"
        if "Microsoft JhengHei" in fams:
            return "Microsoft JhengHei"
    except Exception:
        pass
    return None

def init_style(root):
    """Initialize ttk.Style with larger fonts and row height."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    fn = prefers_msjh()
    base_font = (fn or "TkDefaultFont", 11)
    header_font = (fn or "TkDefaultFont", 12, "bold")

    style.configure("Treeview", font=base_font, rowheight=28)
    style.configure("Treeview.Heading", font=header_font)
    style.map("Treeview", background=[("selected", "#0e639c")], foreground=[("selected", "white")])
    style.configure("TButton", font=base_font, padding=6)
    style.configure("TLabel", font=base_font)
    style.configure("TEntry", font=base_font)
    style.configure("TCheckbutton", font=base_font)
    style.configure("TRadiobutton", font=base_font)

    return style

def apply_palette(root, style, kind):
    """Apply light or dark palette. Returns tag colors for tree rows."""
    k = str(kind).lower()
    if k in ("dark", "\u6697\u8272"):  # "暗色"
        bg = "#1e1e1e"
        fg = "#e6e6e6"
        panel = "#252526"
        accent = "#0e639c"
        alt = "#2a2a2a"
    else:
        bg = "#fafafa"
        fg = "#202020"
        panel = "#ffffff"
        accent = "#0e639c"
        alt = "#f0f3f8"

    root.configure(bg=bg)
    style.configure(".", background=bg, foreground=fg)
    style.configure("Card.TFrame", background=panel, relief="flat")
    style.configure("CardTitle.TLabel", background=panel, foreground=fg, font=("TkDefaultFont", 12, "bold"))
    style.configure("Hint.TLabel", background=panel, foreground="#666666")
    # Labelframe styling for apps that use it
    style.configure("TLabelframe", background=panel, foreground=fg)
    style.configure("TLabelframe.Label", background=panel, foreground=fg, font=("TkDefaultFont", 12, "bold"))

    tag_colors = {
        "even": alt,
        "odd": panel,
        "match": "#fff2ab" if k not in ("dark", "\u6697\u8272") else "#4d3f00",
    }
    return tag_colors
