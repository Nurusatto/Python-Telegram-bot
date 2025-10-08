def normalize_text(text: str | None) -> str:
    if not text:  # если None или пустая строка
        return ""
     
    replacements = {
        "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H", "К": "K",
        "М": "M", "О": "O", "Р": "P", "Т": "T", "Х": "X", "У": "Y"
    }
    for ru, en in replacements.items():
        text = text.replace(ru, en)
    return text.upper().strip()
