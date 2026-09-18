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


NUMPAD_SCAN_CODES = {
    # Numpad Digits
    "num 0": 82, "num0": 82, "numpad 0": 82, "numpad0": 82, "num_0": 82, "numpad_0": 82, "keypad 0": 82, "keypad0": 82,
    "num 1": 79, "num1": 79, "numpad 1": 79, "numpad1": 79, "num_1": 79, "numpad_1": 79, "keypad 1": 79, "keypad1": 79,
    "num 2": 80, "num2": 80, "numpad 2": 80, "numpad2": 80, "num_2": 80, "numpad_2": 80, "keypad 2": 80, "keypad2": 80,
    "num 3": 81, "num3": 81, "numpad 3": 81, "numpad3": 81, "num_3": 81, "numpad_3": 81, "keypad 3": 81, "keypad3": 81,
    "num 4": 75, "num4": 75, "numpad 4": 75, "numpad4": 75, "num_4": 75, "numpad_4": 75, "keypad 4": 75, "keypad4": 75,
    "num 5": 76, "num5": 76, "numpad 5": 76, "numpad5": 76, "num_5": 76, "numpad_5": 76, "keypad 5": 76, "keypad5": 76,
    "num 6": 77, "num6": 77, "numpad 6": 77, "numpad6": 77, "num_6": 77, "numpad_6": 77, "keypad 6": 77, "keypad6": 77,
    "num 7": 71, "num7": 71, "numpad 7": 71, "numpad7": 71, "num_7": 71, "numpad_7": 71, "keypad 7": 71, "keypad7": 71,
    "num 8": 72, "num8": 72, "numpad 8": 72, "numpad8": 72, "num_8": 72, "numpad_8": 72, "keypad 8": 72, "keypad8": 72,
    "num 9": 73, "num9": 73, "numpad 9": 73, "numpad9": 73, "num_9": 73, "numpad_9": 73, "keypad 9": 73, "keypad9": 73,
    # Arithmetic & symbols
    "num +": 78, "num+": 78, "numpad +": 78, "numpad+": 78, "num_add": 78, "num add": 78, "num plus": 78, "numpad_add": 78, "numpad add": 78, "numpad plus": 78, "keypad +": 78, "keypad+": 78,
    "num -": 74, "num-": 74, "numpad -": 74, "numpad-": 74, "num_sub": 74, "num sub": 74, "num subtract": 74, "num minus": 74, "numpad_sub": 74, "numpad sub": 74, "numpad subtract": 74, "numpad minus": 74, "keypad -": 74, "keypad-": 74,
    "num *": 55, "num*": 55, "numpad *": 55, "numpad*": 55, "num_multiply": 55, "num multiply": 55, "num mult": 55, "num star": 55, "numpad_multiply": 55, "numpad multiply": 55, "numpad mult": 55, "numpad star": 55, "keypad *": 55, "keypad*": 55,
    "num /": 53, "num/": 53, "numpad /": 53, "numpad/": 53, "num_divide": 53, "num divide": 53, "num div": 53, "num slash": 53, "numpad_divide": 53, "numpad divide": 53, "numpad div": 53, "numpad slash": 53, "keypad /": 53, "keypad/": 53,
    "num .": 83, "num.": 83, "numpad .": 83, "numpad.": 83, "num_decimal": 83, "num decimal": 83, "num dot": 83, "numpad_decimal": 83, "numpad decimal": 83, "numpad dot": 83, "keypad .": 83, "keypad.": 83,
    "num enter": 28, "num_enter": 28, "numpad enter": 28, "numpad_enter": 28, "keypad enter": 28, "keypadenter": 28,
}


def resolve_hotkey(hotkey_spec):
    """
    Resolves hotkey specifications to hardware scan codes when numpad keys are targeted.
    This prevents standard number / symbol keys on the main keyboard from triggering
    numpad-specific hotkeys.
    """
    if isinstance(hotkey_spec, int):
        return hotkey_spec

    key_str = str(hotkey_spec).strip()
    norm = key_str.lower()

    if norm in NUMPAD_SCAN_CODES:
        return NUMPAD_SCAN_CODES[norm]

    # Handle modifier combinations like 'ctrl+num 8' or 'alt+numpad +'
    if "+" in key_str and not norm.startswith("num +") and not norm.startswith("numpad +") and not norm.startswith("keypad +") and norm != "+":
        parts = [p.strip() for p in key_str.split("+")]
        resolved_parts = [NUMPAD_SCAN_CODES.get(p.lower(), p) for p in parts]
        if any(isinstance(p, int) for p in resolved_parts):
            return resolved_parts

    return key_str


def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "settings": {
                "play_beep_feedback": True
            },
            "hotkeys": [
                {
                    "key": "num *",
                    "action": "toggle_volume_target",
                    "targets": ["focused", "brave.exe"],
                    "description": "Switch Volume Target (Focused Game <-> Brave)"
                },
                {"key": "num 8", "action": "play_pause_and_mute", "process": "focused", "description": "Current Focused Game/Window (Play/Pause & Mute/Unmute)"},
                {"key": "num 7", "action": "play_pause", "process": "brave.exe", "description": "Brave Browser Media (Play/Pause)"},
                {"key": "num 0", "action": "mute", "process": "brave.exe", "description": "Brave Browser (Mute/Unmute)"},
                {"key": "num 9", "action": "mute", "process": "focused", "description": "Current Focused Game/Window (Mute/Unmute)"},
                {"key": "num -", "action": "volume_down", "process": "focused", "description": "Current Focused Game (Volume Down 10%)", "step": 0.10},
                {"key": "num +", "action": "volume_up", "process": "focused", "description": "Current Focused Game (Volume Up 10%)", "step": 0.10}
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

        resolved_key = resolve_hotkey(key)

        # Allow per-hotkey override for sound feedback if specified, else use global setting
        play_beep = item.get(
            "play_beep_feedback",
            item.get("play_sound", item.get("play_beep", item.get("sound", global_play_beep)))
        )

        if action in ("toggle_target", "toggle_volume_target", "switch_target", "switch_volume_target"):
            targets = item.get("targets", ["focused", item.get("process", "brave.exe")])
            print(f"  • Key [{key}] -> [Toggle Volume Target] {' <-> '.join(targets)} ({desc})")
            keyboard.add_hotkey(
                resolved_key,
                on_hotkey_toggle_target,
                args=(targets, desc, play_beep),
                suppress=False
            )
        elif action in ("both", "play_pause_and_mute", "mute_and_play_pause", "play_pause_mute", "mute_play_pause"):
            print(f"  • Key [{key}] -> [Play/Pause & Mute/Unmute] {desc} ({process})")
            keyboard.add_hotkey(
                resolved_key,
                on_hotkey_both,
                args=(process, desc, play_beep),
                suppress=False
            )
        elif action in ("play_pause", "media", "play_pause_media", "media_play_pause"):
            print(f"  • Key [{key}] -> [Play/Pause] {desc} ({process})")
            keyboard.add_hotkey(
                resolved_key,
                on_hotkey_media,
                args=(process, desc, play_beep),
                suppress=False
            )
        elif action in ("volume_down", "vol_down", "volume-", "voldown"):
            step = abs(float(item.get("step", 0.10)))
            print(f"  • Key [{key}] -> [Volume Down -{int(round(step*100))}%] {desc} ({process})")
            keyboard.add_hotkey(
                resolved_key,
                on_hotkey_volume,
                args=(process, -step, desc, play_beep),
                suppress=False
            )
        elif action in ("volume_up", "vol_up", "volume+", "volup"):
            step = abs(float(item.get("step", 0.10)))
            print(f"  • Key [{key}] -> [Volume Up +{int(round(step*100))}%] {desc} ({process})")
            keyboard.add_hotkey(
                resolved_key,
                on_hotkey_volume,
                args=(process, step, desc, play_beep),
                suppress=False
            )
        elif action in ("volume", "volume_change"):
            step = float(item.get("step", 0.10))
            direction = f"{'+' if step > 0 else ''}{int(round(step*100))}%"
            print(f"  • Key [{key}] -> [Volume Change {direction}] {desc} ({process})")
            keyboard.add_hotkey(
                resolved_key,
                on_hotkey_volume,
                args=(process, step, desc, play_beep),
                suppress=False
            )
        else:
            print(f"  • Key [{key}] -> [Mute/Unmute] {desc} ({process})")
            keyboard.add_hotkey(
                resolved_key,
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
