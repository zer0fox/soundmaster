import os
import sys
import queue
import tkinter as tk
from tkinter import ttk, messagebox

import keyboard
import main as core

ACTIONS = [
    ("mute", "Mute / Unmute"),
    ("play_pause", "Play / Pause"),
    ("play_pause_and_mute", "Play / Pause & Mute"),
    ("volume_up", "Volume Up"),
    ("volume_down", "Volume Down"),
    ("toggle_volume_target", "Switch Volume Target"),
]
ACTION_LABELS = dict(ACTIONS)
LABEL_TO_ACTION = {label: key for key, label in ACTIONS}
SOUND_OPTIONS = ("Use global", "On", "Off")
SOUND_KEYS = ("play_beep_feedback", "play_sound", "play_beep", "sound")
RECORD_PROMPT = "Press a key..."

KEYPAD_NAMES = {
    82: "num 0", 79: "num 1", 80: "num 2", 81: "num 3", 75: "num 4",
    76: "num 5", 77: "num 6", 71: "num 7", 72: "num 8", 73: "num 9",
    78: "num +", 74: "num -", 55: "num *", 53: "num /", 83: "num .", 28: "num enter",
}


class QueueWriter:
    def __init__(self, q):
        self.q = q

    def write(self, text):
        if text:
            self.q.put(text)

    def flush(self):
        pass


def get_item_sound(item):
    for k in SOUND_KEYS:
        if k in item:
            return "On" if item[k] else "Off"
    return "Use global"


def set_item_sound(item, option):
    for k in SOUND_KEYS:
        item.pop(k, None)
    if option != "Use global":
        item["play_beep_feedback"] = option == "On"


class HotkeyDialog(tk.Toplevel):
    def __init__(self, app, item):
        super().__init__(app.root)
        self.item = item
        self.result = None
        self.capture_hook = None
        self.captured = queue.Queue()

        self.title("Hotkey")
        self.resizable(False, False)
        self.transient(app.root)
        self.protocol("WM_DELETE_WINDOW", self.close)

        action = item.get("action", "mute")
        if "targets" in item:
            target_text = ", ".join(item["targets"])
        else:
            target_text = item.get("process", "focused")

        self.key_var = tk.StringVar(value=item.get("key", ""))
        self.action_var = tk.StringVar(value=ACTION_LABELS.get(action, action))
        self.target_var = tk.StringVar(value=target_text)
        self.step_var = tk.StringVar(value=str(int(round(abs(float(item.get("step", 0.10))) * 100))))
        self.desc_var = tk.StringVar(value=item.get("description", ""))
        self.sound_var = tk.StringVar(value=get_item_sound(item))

        f = ttk.Frame(self, padding=12)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Key:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(f, textvariable=self.key_var, state="readonly", width=28).grid(row=0, column=1, sticky="we", pady=4)
        ttk.Button(f, text="Record", command=self.record).grid(row=0, column=2, padx=(6, 0))

        ttk.Label(f, text="Action:").grid(row=1, column=0, sticky="w", pady=4)
        action_box = ttk.Combobox(f, textvariable=self.action_var, values=[l for _, l in ACTIONS], state="readonly")
        action_box.grid(row=1, column=1, columnspan=2, sticky="we", pady=4)
        action_box.bind("<<ComboboxSelected>>", lambda _e: self.update_fields())

        ttk.Label(f, text="Target:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(f, textvariable=self.target_var).grid(row=2, column=1, columnspan=2, sticky="we", pady=4)
        ttk.Label(
            f, foreground="gray",
            text="'focused' = active window, or an exe like brave.exe.\nSwitch Volume Target: comma-separated list.",
        ).grid(row=3, column=1, columnspan=2, sticky="w")

        ttk.Label(f, text="Volume step (%):").grid(row=4, column=0, sticky="w", pady=4)
        self.step_box = ttk.Spinbox(f, from_=1, to=100, textvariable=self.step_var, width=6)
        self.step_box.grid(row=4, column=1, sticky="w", pady=4)

        ttk.Label(f, text="Description:").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(f, textvariable=self.desc_var, width=40).grid(row=5, column=1, columnspan=2, sticky="we", pady=4)

        ttk.Label(f, text="Sound feedback:").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Combobox(f, textvariable=self.sound_var, values=SOUND_OPTIONS, state="readonly", width=12).grid(
            row=6, column=1, sticky="w", pady=4
        )

        btns = ttk.Frame(f)
        btns.grid(row=7, column=0, columnspan=3, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Save", command=self.save).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=self.close).pack(side="left")

        self.update_fields()
        self.grab_set()

    def update_fields(self):
        action = LABEL_TO_ACTION.get(self.action_var.get(), self.action_var.get())
        self.step_box.configure(state="normal" if action in ("volume_up", "volume_down") else "disabled")
        if action == "toggle_volume_target" and "," not in self.target_var.get():
            self.target_var.set("focused, brave.exe")

    def record(self):
        self.stop_capture()
        # Unbind existing hotkeys so pressing the key doesn't trigger its current action
        core.clear_hotkeys()
        self.key_var.set(RECORD_PROMPT)
        self.capture_hook = keyboard.hook(self.on_capture)
        self.after(50, self.poll_capture)

    def on_capture(self, event):
        if event.event_type != keyboard.KEY_DOWN:
            return
        name = (event.name or "").lower()
        if not name or name in keyboard.all_modifiers or name == "num lock":
            return
        if getattr(event, "is_keypad", False) and event.scan_code in KEYPAD_NAMES:
            name = KEYPAD_NAMES[event.scan_code]
        mods = [m for m in ("ctrl", "alt", "shift", "windows") if keyboard.is_pressed(m)]
        self.captured.put("+".join(mods + [name]))

    def poll_capture(self):
        try:
            key = self.captured.get_nowait()
        except queue.Empty:
            if self.capture_hook:
                self.after(50, self.poll_capture)
            return
        self.stop_capture()
        self.key_var.set(key)

    def stop_capture(self):
        if self.capture_hook:
            keyboard.unhook(self.capture_hook)
            self.capture_hook = None

    def save(self):
        key = self.key_var.get().strip()
        if not key or key == RECORD_PROMPT:
            messagebox.showwarning("Hotkey", "Please record a key first.", parent=self)
            return

        label = self.action_var.get()
        action = LABEL_TO_ACTION.get(label, label)
        item = dict(self.item)
        item["key"] = key
        item["action"] = action

        targets = [t.strip() for t in self.target_var.get().split(",") if t.strip()] or ["focused"]
        if action == "toggle_volume_target":
            item["targets"] = targets
            item.pop("process", None)
        else:
            item["process"] = targets[0]
            item.pop("targets", None)

        if action in ("volume_up", "volume_down"):
            try:
                pct = float(self.step_var.get())
            except ValueError:
                messagebox.showwarning("Hotkey", "Volume step must be a number.", parent=self)
                return
            item["step"] = round(max(1.0, min(100.0, pct)) / 100, 4)
        elif action in ACTION_LABELS:
            item.pop("step", None)

        item["description"] = self.desc_var.get().strip() or f"{label} ({', '.join(targets)})"
        set_item_sound(item, self.sound_var.get())
        self.result = item
        self.close()

    def close(self):
        self.stop_capture()
        self.destroy()


class SoundMasterApp:
    def __init__(self, root):
        self.root = root
        self.config = core.load_config()
        self.log_queue = queue.Queue()
        sys.stdout = sys.stderr = QueueWriter(self.log_queue)

        root.title("SoundMaster")
        root.geometry("860x540")
        root.minsize(640, 400)
        try:
            root.iconbitmap(os.path.join(core.BASE_DIR, "soundmaster.ico"))
        except tk.TclError:
            pass

        top = ttk.Frame(root, padding=(10, 10, 10, 0))
        top.pack(fill="x")
        self.sound_var = tk.BooleanVar(value=bool(core.get_global_play_beep(self.config)))
        ttk.Checkbutton(
            top, text="Play sound feedback when a hotkey is pressed",
            variable=self.sound_var, command=self.on_toggle_sound,
        ).pack(side="left")

        table = ttk.Frame(root, padding=10)
        table.pack(fill="both", expand=True)
        cols = ("key", "action", "target", "sound", "description")
        self.tree = ttk.Treeview(table, columns=cols, show="headings", selectmode="browse", height=8)
        for col, title, width in (
            ("key", "Key", 90), ("action", "Action", 150), ("target", "Target", 150),
            ("sound", "Sound", 80), ("description", "Description", 320),
        ):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, stretch=(col == "description"))
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="left", fill="y")
        self.tree.bind("<Double-1>", self.edit_selected)

        btns = ttk.Frame(root, padding=(10, 0))
        btns.pack(fill="x")
        ttk.Button(btns, text="Add", command=self.add_hotkey).pack(side="left")
        ttk.Button(btns, text="Edit", command=self.edit_selected).pack(side="left", padx=6)
        ttk.Button(btns, text="Remove", command=self.remove_selected).pack(side="left")

        log_frame = ttk.LabelFrame(root, text="Activity", padding=6)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.log = tk.Text(log_frame, height=10, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)

        self.refresh()
        self.apply_hotkeys()
        self.poll_log()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, item in enumerate(self.config.get("hotkeys", [])):
            action = item.get("action", "mute")
            target = " <-> ".join(item["targets"]) if "targets" in item else item.get("process", "")
            self.tree.insert("", "end", iid=str(i), values=(
                item.get("key", ""), ACTION_LABELS.get(action, action), target,
                get_item_sound(item), item.get("description", ""),
            ))

    def save(self):
        core.save_config(self.config)
        print("[INFO] Saved config.json")

    def apply_hotkeys(self):
        core.clear_hotkeys()
        print("[INFO] Hotkeys loaded:")
        core.register_all_hotkeys(self.config)

    def on_toggle_sound(self):
        self.config.setdefault("settings", {})["play_beep_feedback"] = self.sound_var.get()
        self.save()
        self.apply_hotkeys()

    def selected_index(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def open_dialog(self, item):
        dlg = HotkeyDialog(self, item)
        self.root.wait_window(dlg)
        return dlg.result

    def add_hotkey(self):
        result = self.open_dialog({"action": "mute", "process": "focused"})
        if result:
            self.config.setdefault("hotkeys", []).append(result)
            self.save()
            self.refresh()
        self.apply_hotkeys()

    def edit_selected(self, _event=None):
        idx = self.selected_index()
        if idx is None:
            return
        result = self.open_dialog(self.config["hotkeys"][idx])
        if result:
            self.config["hotkeys"][idx] = result
            self.save()
            self.refresh()
        self.apply_hotkeys()

    def remove_selected(self):
        idx = self.selected_index()
        if idx is None:
            return
        key = self.config["hotkeys"][idx].get("key", "")
        if messagebox.askyesno("Remove Hotkey", f"Remove binding for [{key}]?", parent=self.root):
            del self.config["hotkeys"][idx]
            self.save()
            self.refresh()
            self.apply_hotkeys()

    def poll_log(self):
        chunks = []
        while True:
            try:
                chunks.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        if chunks:
            self.log.configure(state="normal")
            self.log.insert("end", "".join(chunks))
            self.log.see("end")
            self.log.configure(state="disabled")
        self.root.after(100, self.poll_log)


def run_gui():
    root = tk.Tk()
    SoundMasterApp(root)
    root.mainloop()