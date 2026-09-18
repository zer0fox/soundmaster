import os
import sys
import json
import time
import winsound
import keyboard
from audio_controller import (
    toggle_app_mute,
    toggle_media_play_pause,
    change_app_volume,
    list_active_audio_apps
)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Runtime state for dynamic target switching (e.g. key 6 toggles volume between focused game & Brave)
current_volume_target = "focused"
current_target_index = 0


def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "settings": {
                "play_beep_feedback": True
            },
            "hotkeys": [
                {
                    "key": "6",
                    "action": "toggle_volume_target",
                    "targets": ["focused", "brave.exe"],
                    "description": "Switch Volume Target (Focused Game <-> Brave)"
                },
                {"key": "8", "action": "play_pause", "process": "brave.exe", "description": "Brave Browser Media (Play/Pause)"},
                {"key": "0", "action": "mute", "process": "brave.exe", "description": "Brave Browser (Mute/Unmute)"},
                {"key": "9", "action": "mute", "process": "focused", "description": "Current Focused Game/Window (Mute/Unmute)"},
                {"key": "-", "action": "volume_down", "process": "focused", "description": "Volume Down 10%", "step": 0.10},
                {"key": "=", "action": "volume_up", "process": "focused", "description": "Volume Up 10%", "step": 0.10}
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


def play_volume_feedback(volume_level: float | None):
    """Subtle audio beep feedback for volume change indicating relative level."""
    try:
        if volume_level is not None:
            # Frequency scales with volume percentage (0% = 400Hz, 100% = 1000Hz)
            freq = max(300, min(1200, int(400 + volume_level * 600)))
            winsound.Beep(freq, 60)
        else:
            winsound.Beep(300, 60)
            time.sleep(0.05)
            winsound.Beep(300, 60)
    except Exception:
        pass


def play_target_switch_feedback(target: str):
    """Distinct audio cues when switching between Focused Game and specific App mode."""
    try:
        if target.lower() in ("focused", "current", "active", "foreground"):
            # Switched back to Focused Game mode: 2 descending beeps (750Hz -> 500Hz)
            winsound.Beep(750, 70)
            time.sleep(0.03)
            winsound.Beep(500, 90)
        else:
            # Switched to App mode (e.g. Brave): 2 ascending high beeps (500Hz -> 850Hz)
            winsound.Beep(500, 70)
            time.sleep(0.03)
            winsound.Beep(850, 90)
    except Exception:
        pass


def on_hotkey_toggle_target(targets: list[str], description: str, play_beep: bool):
    global current_volume_target, current_target_index
    if not targets:
        return
    current_target_index = (current_target_index + 1) % len(targets)
    current_volume_target = targets[current_target_index]

    if current_volume_target.lower() in ("focused", "current", "active", "foreground"):
        target_display = "FOCUSED GAME / WINDOW (Default)"
    else:
        target_display = current_volume_target.upper()

    print(f"[{time.strftime('%H:%M:%S')}] {description}: Volume Target set to -> [{target_display}]")

    if play_beep:
        play_target_switch_feedback(current_volume_target)


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


def on_hotkey_both(process_name: str, description: str, play_beep: bool):
    success, media_msg = toggle_media_play_pause(process_name)
    is_muted, count, resolved_name = toggle_app_mute(process_name)
    if is_muted is None:
        status = "NOT RUNNING / NO AUDIO DETECTED"
    else:
        status = "MUTED" if is_muted else "UNMUTED"

    print(f"[{time.strftime('%H:%M:%S')}] {description} [{resolved_name}]: {media_msg} | {status} ({count} audio stream(s))")

    if play_beep:
        play_mute_feedback(is_muted)


def on_hotkey_volume(process_name: str, delta: float, description: str, play_beep: bool):
    # Dynamically resolve target if process is marked as focused/dynamic
    if process_name.lower() in ("focused", "current", "active", "foreground", "dynamic", "target"):
        actual_process = current_volume_target
    else:
        actual_process = process_name

    new_vol, count, resolved_name = change_app_volume(actual_process, delta)
    if new_vol is None:
        status = "NOT RUNNING / NO AUDIO DETECTED"
    else:
        percentage = int(round(new_vol * 100))
        status = f"VOLUME: {percentage}%"

    direction = f"{'+' if delta > 0 else ''}{int(round(delta * 100))}%"
    target_tag = f" [Mode: {actual_process}]" if actual_process != "focused" else ""
    print(f"[{time.strftime('%H:%M:%S')}] {description}{target_tag} [{resolved_name}] ({direction}): {status} ({count} audio stream(s))")

    if play_beep:
        play_volume_feedback(new_vol)


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
    settings = config.get("settings", {})
    global_play_beep = settings.get(
        "play_beep_feedback",
        settings.get("play_sound", settings.get("play_beep", settings.get("sound", config.get("play_beep_feedback", config.get("play_sound", True)))))
    )
    hotkeys = config.get("hotkeys", [])

    print("=" * 60)
    print("           SoundMaster - Audio & Media Controller          ")
    print("=" * 60)
    print(f"Sound feedback: {'ENABLED' if global_play_beep else 'DISABLED'}")
    print(f"Loaded {len(hotkeys)} hotkey binding(s) from config.json:\n")

    for item in hotkeys:
        key = item.get("key")
        action = item.get("action", "mute").lower().strip()
        process = item.get("process", "brave.exe")
        desc = item.get("description", process)
        if not key:
            continue

        # Allow per-hotkey override for sound feedback if specified, else use global setting
        play_beep = item.get(
            "play_beep_feedback",
            item.get("play_sound", item.get("play_beep", item.get("sound", global_play_beep)))
        )

        if action in ("toggle_target", "toggle_volume_target", "switch_target", "switch_volume_target"):
            targets = item.get("targets", ["focused", item.get("process", "brave.exe")])
            print(f"  • Key [{key}] -> [Toggle Volume Target] {' <-> '.join(targets)} ({desc})")
            keyboard.add_hotkey(
                key,
                on_hotkey_toggle_target,
                args=(targets, desc, play_beep),
                suppress=False
            )
        elif action in ("both", "play_pause_and_mute", "mute_and_play_pause", "play_pause_mute", "mute_play_pause"):
            print(f"  • Key [{key}] -> [Play/Pause & Mute/Unmute] {desc} ({process})")
            keyboard.add_hotkey(
                key,
                on_hotkey_both,
                args=(process, desc, play_beep),
                suppress=False
            )
        elif action in ("play_pause", "media", "play_pause_media", "media_play_pause"):
            print(f"  • Key [{key}] -> [Play/Pause] {desc} ({process})")
            keyboard.add_hotkey(
                key,
                on_hotkey_media,
                args=(process, desc, play_beep),
                suppress=False
            )
        elif action in ("volume_down", "vol_down", "volume-", "voldown"):
            step = abs(float(item.get("step", 0.10)))
            print(f"  • Key [{key}] -> [Volume Down -{int(round(step*100))}%] {desc} ({process})")
            keyboard.add_hotkey(
                key,
                on_hotkey_volume,
                args=(process, -step, desc, play_beep),
                suppress=False
            )
        elif action in ("volume_up", "vol_up", "volume+", "volup"):
            step = abs(float(item.get("step", 0.10)))
            print(f"  • Key [{key}] -> [Volume Up +{int(round(step*100))}%] {desc} ({process})")
            keyboard.add_hotkey(
                key,
                on_hotkey_volume,
                args=(process, step, desc, play_beep),
                suppress=False
            )
        elif action in ("volume", "volume_change"):
            step = float(item.get("step", 0.10))
            direction = f"{'+' if step > 0 else ''}{int(round(step*100))}%"
            print(f"  • Key [{key}] -> [Volume Change {direction}] {desc} ({process})")
            keyboard.add_hotkey(
                key,
                on_hotkey_volume,
                args=(process, step, desc, play_beep),
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
    print("[TIP]  If hotkeys do not respond inside certain games, run SoundMaster as Administrator.")
    print("[INFO] Press Ctrl+C in this window to exit.")
    print("=" * 60)

    try:
        # Keep running
        keyboard.wait()
    except KeyboardInterrupt:
        print("\nExiting SoundMaster.")


if __name__ == "__main__":
    main()
