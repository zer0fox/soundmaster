import os
import sys
import json
import time
import winsound
import keyboard
from audio_controller import toggle_app_mute, list_active_audio_apps

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "settings": {
                "play_beep_feedback": True
            },
            "hotkeys": [
                {"key": "0", "process": "brave.exe", "description": "Brave Browser"},
                {"key": "9", "process": "focused", "description": "Current Focused Game/Window"}
            ]
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def play_feedback(muted: bool | None):
    """Subtle audio beep so you know the mute status while inside full screen games."""
    try:
        if muted is True:
            # Low beep for Muted
            winsound.Beep(450, 120)
        elif muted is False:
            # Higher beep for Unmuted
            winsound.Beep(850, 120)
        else:
            # Double short low beep if app is not found/running
            winsound.Beep(300, 60)
            time.sleep(0.05)
            winsound.Beep(300, 60)
    except Exception:
        pass


def on_hotkey_pressed(process_name: str, description: str, play_beep: bool):
    is_muted, count, resolved_name = toggle_app_mute(process_name)
    if is_muted is None:
        status = "NOT RUNNING / NO AUDIO DETECTED"
    else:
        status = "MUTED" if is_muted else "UNMUTED"

    print(f"[{time.strftime('%H:%M:%S')}] {description} [{resolved_name}]: {status} ({count} audio stream(s))")

    if play_beep:
        play_feedback(is_muted)


def main():
    if "--list" in sys.argv or "-l" in sys.argv:
        print("Scanning active audio applications...")
        apps = list_active_audio_apps()
        if apps:
            print("Found active audio processes:")
            for app in apps:
                print(f"  - {app}")
        else:
            print("No active audio processes currently playing/registered.")
        return

    config = load_config()
    play_beep = config.get("settings", {}).get("play_beep_feedback", True)
    hotkeys = config.get("hotkeys", [])

    print("=" * 60)
    print("           SoundMaster - Background Audio Muter           ")
    print("=" * 60)
    print(f"Loaded {len(hotkeys)} hotkey binding(s) from config.json:\n")

    for item in hotkeys:
        key = item.get("key")
        process = item.get("process")
        desc = item.get("description", process)
        if not key or not process:
            continue

        print(f"  • Key [{key}] -> {desc} ({process})")
        # Register global hotkey
        keyboard.add_hotkey(
            key,
            on_hotkey_pressed,
            args=(process, desc, play_beep),
            suppress=False
        )

    print("\n[INFO] SoundMaster is now running in the background.")
    print("[INFO] Press your configured hotkeys at any time (even inside full-screen games).")
    print("[INFO] Press Ctrl+C in this window to exit.")
    print("=" * 60)

    try:
        # Keep running
        keyboard.wait()
    except KeyboardInterrupt:
        print("\nExiting SoundMaster.")


if __name__ == "__main__":
    main()
