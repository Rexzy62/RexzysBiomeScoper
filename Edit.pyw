import tkinter as tk
from tkinter import ttk, simpledialog
import configparser
import os

# --- MultiSelectDropdown Widget Class ---
class MultiSelectDropdown(tk.Frame):
    def __init__(self, master=None, options=None, initial_selection=None):
        super().__init__(master)
        self.options = options if options is not None else []
        self.selected_options = set(initial_selection) if initial_selection is not None else set()

        self.combobox_var = tk.StringVar(self)
        self._update_combobox_display()

        style = ttk.Style()
        style.configure("TCombobox", fieldbackground="white", background="lightgray")

        self.combobox = ttk.Combobox(self, textvariable=self.combobox_var, state="readonly", style="TCombobox")
        self.combobox.pack(fill='x', expand=True)
        self.combobox.bind("<<ComboboxSelected>>", self._show_multi_select_dialog)
        self.combobox.bind("<Button-1>", self._show_multi_select_dialog) # Also open on click

    def _update_combobox_display(self):
        if self.selected_options:
            display_text = ", ".join(sorted(list(self.selected_options)))
        else:
            display_text = "" # Or "Select Biomes..."
        self.combobox_var.set(display_text)

    def _show_multi_select_dialog(self, event=None):
        dialog = tk.Toplevel(self.master)
        dialog.title("Select Options")
        dialog.grab_set()
        dialog.transient(self.master)

        check_frame = ttk.Frame(dialog)
        check_frame.pack(padx=10, pady=10, fill='both', expand=True)

        check_vars = {}
        for option in self.options:
            var = tk.BooleanVar(value=(option in self.selected_options))
            cb = ttk.Checkbutton(check_frame, text=option, variable=var)
            cb.pack(anchor='w', padx=5, pady=2)
            check_vars[option] = var

        def on_ok():
            new_selection = set()
            for option, var in check_vars.items():
                if var.get():
                    new_selection.add(option)
            self.selected_options = new_selection
            self._update_combobox_display()
            dialog.destroy()

        ok_button = ttk.Button(dialog, text="OK", command=on_ok)
        ok_button.pack(pady=5)

        self.update_idletasks()
        x = self.master.winfo_x() + self.winfo_x() + self.combobox.winfo_x()
        y = self.master.winfo_y() + self.winfo_y() + self.combobox.winfo_y() + self.combobox.winfo_height()
        dialog.geometry(f"+{x}+{y}")

        self.wait_window(dialog)

    def get_selected(self):
        return list(self.selected_options)
    
    def set_selected(self, new_selection):
        self.selected_options = set(new_selection)
        self._update_combobox_display()

# --- Configuration Handling ---
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
config = configparser.ConfigParser()

def load_settings():
    config.read(CONFIG_FILE)
    settings = {}
    if 'Main' in config:
        settings['PrivateServerLinkEnable'] = config.getboolean('Main', 'PrivateServerLinkEnable', fallback=False)
        
        send_message_str = config.get('Main', 'EnableOnThisBiome', fallback='')
        settings['EnableOnThisBiome'] = [item.strip() for item in send_message_str.split(',') if item.strip()]

        ping_on_str = config.get('Main', 'PingOnThisBiome', fallback='')
        settings['PingOnThisBiome'] = [item.strip() for item in ping_on_str.split(',') if item.strip()]

        settings['StatusEnabled'] = config.getboolean('Main', 'StatusEnabled', fallback=False)
        settings['EmojiEnabled'] = config.getboolean('Main', 'EmojiEnabled', fallback=False)
    return settings

def save_settings():
    if 'Main' not in config:
        config['Main'] = {}
    
    config['Main']['PrivateServerLinkEnable'] = str(private_server_link_var.get())
    
    config['Main']['EnableOnThisBiome'] = ", ".join(send_message_dropdown.get_selected())
    config['Main']['PingOnThisBiome'] = ", ".join(ping_dropdown.get_selected())

    config['Main']['StatusEnabled'] = str(enable_aura_var.get())
    config['Main']['EmojiEnabled'] = str(enable_emojis_var.get())

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    print(f"Settings saved to {CONFIG_FILE}")


def confirm_action():
    save_settings()
    print("Confirm action triggered and settings saved.")
    
# --- Main GUI Setup ---
root = tk.Tk()
root.title("Settings")
root.geometry("600x200")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=2)
main_frame.grid_columnconfigure(2, weight=1)
main_frame.grid_rowconfigure(0, weight=1)

settings_frame = ttk.LabelFrame(main_frame, text="Settings")
settings_frame.grid(row=0, column=0, columnspan=3, rowspan=1, padx=5, pady=5, sticky="nsew")

settings_frame.grid_columnconfigure(0, weight=1)
settings_frame.grid_columnconfigure(1, weight=2)
settings_frame.grid_columnconfigure(2, weight=1)
settings_frame.grid_rowconfigure(0, weight=1)


# Group Box: Private Server
private_server_frame = ttk.LabelFrame(settings_frame, text="Private Server")
private_server_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

private_server_link_var = tk.BooleanVar(value=False)
private_server_link_checkbox = ttk.Checkbutton(private_server_frame, text="Send Invite Link", variable=private_server_link_var)
private_server_link_checkbox.pack(padx=10, pady=10, anchor="w")

# Group Box: Biomes
biomes_frame = ttk.LabelFrame(settings_frame, text="Biomes")
biomes_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
biomes_frame.grid_rowconfigure(0, weight=1)
biomes_frame.grid_rowconfigure(1, weight=1)

# Send Message On
ttk.Label(biomes_frame, text="Send Message on").pack(pady=(5, 0))
biome_options = ["NORMAL", "WINDY" ,"SNOWY", "RAINY", "SANDSTORM", "STARFALL", "CORUPPTION", "NULL", "GLITCHED", "DREAMSPACE", "GRAVEYARD", "BLOODRAIN", "PUMPKIN MOON"]
send_message_dropdown = MultiSelectDropdown(biomes_frame, options=biome_options)
send_message_dropdown.pack(padx=10, pady=5, fill='x', expand=True)

# Ping On
ttk.Label(biomes_frame, text="Ping on").pack(pady=(10, 0))
ping_dropdown = MultiSelectDropdown(biomes_frame, options=biome_options)
ping_dropdown.pack(padx=10, pady=5, fill='x', expand=True)


# Group Box: Other
other_frame = ttk.LabelFrame(settings_frame, text="Other")
other_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
# Configure this column to make the button grow
other_frame.grid_columnconfigure(0, weight=1)

enable_aura_var = tk.BooleanVar(value=False)
enable_aura_checkbox = ttk.Checkbutton(other_frame, text="Enable aura", variable=enable_aura_var)
enable_aura_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")

enable_emojis_var = tk.BooleanVar(value=False)
enable_emojis_checkbox = ttk.Checkbutton(other_frame, text="Enable Emojis", variable=enable_emojis_var)
enable_emojis_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")

# Removed: re_download_button = ttk.Button(...)

# Confirm button - make it fill the available width
confirm_button = ttk.Button(other_frame, text="Confirm", command=confirm_action)
# Using grid to place it and sticky="ew" to make it fill the width
confirm_button.grid(row=2, column=0, padx=10, pady=(15, 5), sticky="ew") # Increased pady top for spacing


# --- Load settings when the GUI starts ---
initial_settings = load_settings()
private_server_link_var.set(initial_settings.get('PrivateServerLinkEnable', False))
send_message_dropdown.set_selected(initial_settings.get('EnableOnThisBiome', []))
ping_dropdown.set_selected(initial_settings.get('PingOnThisBiome', []))
enable_aura_var.set(initial_settings.get('StatusEnabled', False))
enable_emojis_var.set(initial_settings.get('EmojiEnabled', False))



root.mainloop()
