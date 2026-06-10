import api
import ui
import re

def password_is_strong(pw):
    if len(pw) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", pw):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[0-9]", pw):
        return False, "Password must contain at least one number"
    return True, ""

def login_screen():
    while True:
        ui.clear_screen()
        ui.print_header("PROJECT & RESOURCE MANAGEMENT TOOL", "Learn & Code — Final Project")
        choice = ui.get_menu_choice(["Login", "Exit"])

        if choice == "1":
            username = ui.get_input("Username: ")
            if not username:
                continue
            password = ui.get_input("Password: ")
            if not password:
                continue
            try:
                api.login(username, password)
                user = api.get_me()
                
                if user.get("force_password_change"):
                    if not force_change_password():
                        continue
                    user = api.get_me()
                
                return user
            except api.APIError as e:
                ui.print_error(e.message)
                ui.get_input("Press Enter to continue...")
        elif choice == "2":
            print("\nGoodbye!")
            exit(0)
        else:
            ui.print_error("Invalid option")
            ui.get_input("Press Enter to continue...")

def force_change_password():
    ui.clear_screen()
    ui.print_header("CHANGE PASSWORD", "You must set a new password to continue.")
    
    while True:
        new_pw = ui.get_input("New Password        : ")
        if not new_pw:
            return False
        confirm_pw = ui.get_input("Confirm Password    : ")
        if not confirm_pw:
            return False
            
        if new_pw != confirm_pw:
            ui.print_error("Passwords do not match. Try again.")
            continue
            
        valid, msg = password_is_strong(new_pw)
        if not valid:
            ui.print_error(msg)
            continue
        
        ui.print_separator()
        print("[S] Save and Continue")
        choice = ui.get_input("> ").upper()
        if choice == "S":
            try:
                api.change_password(new_pw)
                ui.print_success("Password updated. Welcome!")
                ui.get_input("Press Enter to continue...")
                return True
            except api.APIError as e:
                ui.print_error(e.message)
        else:
            return False
