import ctypes
import sys
import comtypes
import psutil
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume


def get_foreground_process() -> tuple[int | None, str | None]:
    """Returns (pid, process_name) of the currently focused / active foreground window."""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if not hwnd:
        return None, None
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return None, None
    try:
        proc = psutil.Process(pid.value)
        return pid.value, proc.name()
    except Exception:
        return pid.value, None


def toggle_app_mute(app_target: str) -> tuple[bool | None, int, str]:
    """
    Toggles the mute state of all audio sessions matching app_target.
    app_target can be:
      - 'focused', 'current', or 'active': targets whatever window/game currently has focus
      - an executable name, e.g. 'brave', 'brave.exe'
    
    Returns:
        (new_mute_state, matched_sessions_count, resolved_process_name)
        new_mute_state: True if muted, False if unmuted, None if no session was found.
    """
    comtypes.CoInitialize()
    try:
        target_lower = app_target.lower().strip()
        is_focused_mode = target_lower in ("focused", "current", "active", "foreground")
        target_pid = None
        target_proc_name = None

        if is_focused_mode:
            target_pid, target_proc_name = get_foreground_process()
            if not target_pid:
                return None, 0, "No Active Window"
            display_name = target_proc_name or f"PID:{target_pid}"
        else:
            if not target_lower.endswith(".exe"):
                target_lower += ".exe"
            display_name = target_lower

        sessions = AudioUtilities.GetAllSessions()
        matched_volumes = []
        is_any_unmuted = False
        resolved_name = display_name

        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            process = session.Process

            matches = False
            if process:
                proc_name = process.name().lower()
                proc_pid = process.pid

                if is_focused_mode:
                    # Match by PID or process name of the active foreground window
                    if (target_pid and proc_pid == target_pid) or (target_proc_name and proc_name == target_proc_name.lower()):
                        matches = True
                        resolved_name = process.name()
                else:
                    if proc_name == target_lower:
                        matches = True
                        resolved_name = process.name()

            if matches:
                matched_volumes.append(volume)
                if volume.GetMute() == 0:
                    is_any_unmuted = True

        if not matched_volumes:
            return None, 0, resolved_name

        # If any matched session is unmuted, mute all. Otherwise unmute all.
        new_mute_state = 1 if is_any_unmuted else 0

        for volume in matched_volumes:
            volume.SetMute(new_mute_state, None)

        return bool(new_mute_state), len(matched_volumes), resolved_name
    finally:
        comtypes.CoUninitialize()


def list_active_audio_apps() -> list[str]:
    """Returns a list of unique process names currently having active audio sessions."""
    comtypes.CoInitialize()
    try:
        sessions = AudioUtilities.GetAllSessions()
        apps = set()
        for session in sessions:
            if session.Process:
                apps.add(session.Process.name())
        return sorted(list(apps))
    finally:
        comtypes.CoUninitialize()
