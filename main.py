import os
import sys
import json
import time
import winsound
import keyboard
from audio_controller import toggle_app_mute, toggle_media_play_pause, list_active_audio_apps

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "settings": {
                "play_beep_feedback": True
            },
            "hotkeys": [
                {"key": "8", "action": "play_pause", "process": "brave.exe", "description": "Brave Browser Media (Play/Pause)"},
                {"key": "0", "action": "mute", "process": "brave.exe", "description": "Brave Browser (Mute/Unmute)"},
                {"key": "9", "action": "mute", "process": "focused", "description": "Current Focused Game/Window (Mute/Unmute)"}
            ]
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def play_mute_feedback(muted: bool | None):
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


def play_media_feedback(success: bool):
    """Subtle audio beep feedback for media play/pause toggle."""
    try:
        if success:
            winsound.Beep(650, 100)
        else:
            winsound.Beep(300, 60)
            time.sleep(0.05)
            winsound.Beep(300, 60)
    except Exception:
        pass


def on_hotkey_mute(process_name: str, description: str, play_beep: bool):
    is_muted, count, resolved_name = toggle_app_mute(process_name)
    if is_muted is None:
        status = "NOT RUNNING / NO AUDIO DETECTED"
    else:
        status = "MUTED" if is_muted else "UNMUTED"

    print(f"[{time.strftime('%H:%M:%S')}] {description} [{resolved_name}]: {status} ({count} audio stream(s))")

    if play_beep:
        play_mute_feedback(is_muted)


def on_hotkey_media(process_name: str, description: str, play_beep: bool):
    success, msg = toggle_media_play_pause(process_name)
    print(f"[{time.strftime('%H:%M:%S')}] {description}: {msg}")

    if play_beep:
        play_media_feedback(success)


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
    print("           SoundMaster - Audio & Media Controller          ")
    print("=" * 60)
    print(f"Loaded {len(hotkeys)} hotkey binding(s) from config.json:\n")

    for item in hotkeys:
        key = item.get("key")
        action = item.get("action", "mute").lower().strip()
        process = item.get("process", "brave.exe")
        desc = item.get("description", process)
        if not key:
            continue

        if action in ("play_pause", "media", "play_pause_media", "media_play_pause"):
            print(f"  • Key [{key}] -> [Play/Pause] {desc} ({process})")
            keyboard.add_hotkey(
                key,
                on_hotkey_media,
                args=(process, desc, play_beep),
                suppress=False
            )
        else:
            print(f"  • Key [{key}] -> [Mute/Unmute] {desc} ({process})")
            keyboard.add_hotkey(
                key,
                on_hotkey_mute,
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
