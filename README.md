# SoundMaster - Background Per-App Audio Muter

SoundMaster runs in the background and lets you toggle mute/unmute for specific applications or the **currently focused game/window** using customizable global hotkeys, even while playing full-screen games.

---

## ⚙️ Configuration (`config.json`)

Edit `config.json` to map keys to applications:

```json
{
  "settings": {
    "play_beep_feedback": true
  },
  "hotkeys": [
    {
      "key": "0",
      "process": "brave.exe",
      "description": "Brave Browser"
    },
    {
      "key": "9",
      "process": "focused",
      "description": "Current Focused Game/Window"
    },
    {
      "key": "ctrl+shift+m",
      "process": "spotify.exe",
      "description": "Spotify"
    }
  ]
}
```

### Options:
- `key`: Any key or combination (`"9"`, `"0"`, `"f9"`, `"ctrl+alt+m"`, `"num 1"`, etc.).
- `process`: 
  - `"focused"` (or `"current"` / `"active"`): **Mutes whatever game or window is currently active/focused in the foreground!**
  - Or a specific `.exe` name (e.g., `brave.exe`, `discord.exe`, `spotify.exe`).
- `description`: Friendly name for logging.
- `play_beep_feedback`: If `true`, plays a quick subtle sound cue when you press the hotkey:
  - **Low pitch tone**: Muted
  - **High pitch tone**: Unmuted
  - **Double low tone**: Application not found or no audio detected

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
