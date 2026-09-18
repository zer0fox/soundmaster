# SoundMaster - Background Audio & Media Controller

SoundMaster runs in the background and lets you toggle mute/unmute or play/pause media (e.g., YouTube in Brave Browser) for specific applications or the **currently focused game/window** using customizable global hotkeys, even while playing full-screen games.

---

## ⚙️ Configuration (`config.json`)

Edit `config.json` to map keys to applications and actions:

```json
{
  "settings": {
    "play_beep_feedback": true
  },
  "hotkeys": [
    {
      "key": "6",
      "action": "toggle_volume_target",
      "targets": ["focused", "brave.exe"],
      "description": "Switch Volume Target (Focused Game <-> Brave)"
    },
    {
      "key": "7",
      "action": "play_pause_and_mute",
      "process": "focused",
      "description": "Current Focused Game/Window (Play/Pause & Mute/Unmute)"
    },
    {
      "key": "8",
      "action": "play_pause",
      "process": "brave.exe",
      "description": "Brave Browser Media (Play/Pause)"
    },
    {
      "key": "0",
      "action": "mute",
      "process": "brave.exe",
      "description": "Brave Browser (Mute/Unmute)"
    },
    {
      "key": "9",
      "action": "mute",
      "process": "focused",
      "description": "Current Focused Game/Window (Mute/Unmute)"
    },
    {
      "key": "-",
      "action": "volume_down",
      "process": "focused",
      "step": 0.10,
      "description": "Volume Down 10%"
    },
    {
      "key": "=",
      "action": "volume_up",
      "process": "focused",
      "step": 0.10,
      "description": "Volume Up 10%"
    }
  ]
}
```

### Options:
- `settings`:
  - `play_beep_feedback` (or `play_sound`): `true` (default) or `false`. Globally enables or disables beep sound feedback when pressing any hotkey.
- `key`: Any key or combination (`"6"`, `"-"`, `"="`, `"7"`, `"8"`, `"9"`, `"0"`, `"f9"`, `"ctrl+alt+m"`, `"num 1"`, etc.).
- `action`:
  - `"toggle_volume_target"`: Cycles the active volume target between the list of processes in `targets` (e.g., switches `-` and `=` volume keys between the focused game and Brave).
  - `"volume_down"` (or `"vol_down"`): Lowers application volume by `step` (default `0.10` / 10%).
  - `"volume_up"` (or `"vol_up"`): Increases application volume by `step` (default `0.10` / 10%).
  - `"play_pause_and_mute"` (or `"both"`): Simultaneously toggles media play/pause and mute/unmute.
  - `"play_pause"` (or `"media"`): Toggles play/pause for media (e.g. YouTube playback).
  - `"mute"` (default if omitted): Toggles mute/unmute for the application's audio session.
- `targets`: List of target processes to cycle through when using `"toggle_volume_target"` (e.g. `["focused", "brave.exe"]`).
- `step`: Optional volume change increment (e.g., `0.10` for 10%, `0.05` for 5%).
- `process`: 
  - `"focused"` (or `"current"` / `"active"`): Targets whatever game or window is currently active/focused in the foreground (or follows the target toggled by `toggle_volume_target`)!
  - Or a specific `.exe` name (e.g., `brave.exe`, `discord.exe`, `spotify.exe`).
- `description`: Friendly name for logging.
- `play_sound` / `play_beep_feedback`: (Optional per-hotkey) Set to `false` (or `true`) to override sound feedback for a specific hotkey.
- Sound feedback cues (when enabled):
  - **Rising double tone (500 -> 850 Hz)**: Volume target switched to App (e.g., Brave)
  - **Descending double tone (750 -> 500 Hz)**: Volume target switched back to Focused Game
  - **Dynamic pitch tone (400-1000 Hz)**: Volume level percentage feedback
  - **Medium tone (650 Hz)**: Media Play/Pause triggered
  - **Low pitch tone**: Muted
  - **High pitch tone**: Unmuted
  - **Double low tone**: Application not found / no audio detected

---

## 🔍 How to Find an App's Process Name

Run the scanner tool to see all processes currently registered with the Windows audio mixer:

```bash
python main.py --list
```

---

## ▶️ Running SoundMaster

- **Standard mode (with log window)**:
  Double-click `start.bat` or run:
  ```bash
  python main.py
  ```

- **Hidden background mode (no console window)**:
  ```bash
  pythonw main.py
  ```

> [!TIP]
> **Hotkeys not working in some games?**  
> If hotkeys don't trigger when focused inside games with anti-cheats (e.g., Easy Anti-Cheat, BattlEye, Vanguard) or games run with elevated privileges, **run your terminal / SoundMaster as Administrator**. Windows UIPI blocks non-elevated apps from capturing hotkeys over elevated game windows.
