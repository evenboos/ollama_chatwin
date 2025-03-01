# 颜色常量
MAIN_BG = "#F4F8FF"
NAV_BG = "#0032A0"
TITLE_BG = "#6BA8FF"
CARD_BG = "#E0EEF0"
BORDER_COLOR = "#C0D8E0"
PRIMARY_COLOR = "#6BA8FF"

# 公共样式表
STYLES = {
    "main_window": f"""
        FluentWindow {{
            background-color: {MAIN_BG};
        }}
        QWidget#mainInterface {{
            border-radius: 10px;
        }}
    """,
    "chat_display": f"""
        TextEdit {{
            background-color: {CARD_BG};
            border: 2px solid {BORDER_COLOR};
            border-radius: 8px;
        }}
    """,
    "preview_card": f"""
        QWidget {{
            background-color: {CARD_BG};
            border-radius: 8px;
            border: 2px solid {BORDER_COLOR};
        }}
    """,
    "navigation": f"""
        NavigationPanel {{
            background-color: {NAV_BG};
            border-radius: 8px;
            margin: 10px;
        }}
    """
}