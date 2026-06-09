import os
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, subtitle=None):
    print()
    print("╔══════════════════════════════════════════════╗")
    print(f"║    {title:<41}║")
    if subtitle:
        print(f"║    {subtitle:<41}║")
    print("╚══════════════════════════════════════════════╝")
    print()

def print_welcome(name, role):
    now = datetime.now().strftime("%d-%m-%Y  %H:%M")
    if role == "ADMIN":
        title = "ADMIN PANEL"
        subtitle = f"Welcome, {name}  |  {now}"
    elif role == "MANAGER":
        title = f"Welcome, {name}!  |  {now}"
        subtitle = None
    else:
        title = f"Welcome, {name}!"
        subtitle = datetime.now().strftime("%d-%b-%Y")
    print_header(title, subtitle)

def print_separator():
    print("──────────────────────────────────────────────")

def print_success(msg):
    print(f"\n{msg} ✓\n")

def print_error(msg):
    print(f"\n⚠  Error: {msg}\n")

def print_warning(msg):
    print(f"\n⚠  {msg}\n")

def get_input(prompt="Enter option: "):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

def get_menu_choice(options, prompt="Enter option: "):
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print()
    choice = get_input(prompt)
    return choice

def confirm(msg):
    print(f"\n{msg}")
    choice = get_input("[Y] Yes     [B] Cancel\n> ").upper()
    return choice == "Y"

def print_table(headers, rows, col_widths=None):
    if not col_widths:
        col_widths = []
        for i, h in enumerate(headers):
            max_w = len(str(h))
            for row in rows:
                if i < len(row):
                    max_w = max(max_w, len(str(row[i])))
            col_widths.append(min(max_w + 2, 20))

    header_line = ""
    for i, h in enumerate(headers):
        header_line += str(h).ljust(col_widths[i])
    print(header_line)

    for row in rows:
        line = ""
        for i, cell in enumerate(row):
            if i < len(col_widths):
                line += str(cell).ljust(col_widths[i])
        print(line)
