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
    }
  ]
}
```

### Options:
- `key`: Any key or combination (`"8"`, `"9"`, `"0"`, `"f9"`, `"ctrl+alt+m"`, `"num 1"`, etc.).
- `action`:
  - `"play_pause"` (or `"media"`): Toggles play/pause for media (e.g. YouTube playback).
  - `"mute"` (default if omitted): Toggles mute/unmute for the application's audio session.
- `process`: 
  - `"focused"` (or `"current"` / `"active"`): Targets whatever game or window is currently active/focused in the foreground!
  - Or a specific `.exe` name (e.g., `brave.exe`, `discord.exe`, `spotify.exe`).
- `description`: Friendly name for logging.
- `play_beep_feedback`: If `true`, plays a quick subtle sound cue when you press the hotkey:
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
