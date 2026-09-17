import os
import subprocess


def create_shortcuts():
    desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    target_bat = os.path.join(project_dir, "start.bat")
    icon_path = os.path.join(project_dir, "soundmaster.ico")

    desktop_shortcut = os.path.join(desktop_dir, "SoundMaster.lnk")
    project_shortcut = os.path.join(project_dir, "SoundMaster.lnk")

    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell

# Desktop shortcut
$sc1 = $WshShell.CreateShortcut('{desktop_shortcut}')
$sc1.TargetPath = '{target_bat}'
$sc1.WorkingDirectory = '{project_dir}'
$sc1.IconLocation = '{icon_path},0'
$sc1.Description = 'SoundMaster - Background Audio Controller'
$sc1.Save()

# Project shortcut
$sc2 = $WshShell.CreateShortcut('{project_shortcut}')
$sc2.TargetPath = '{target_bat}'
$sc2.WorkingDirectory = '{project_dir}'
$sc2.IconLocation = '{icon_path},0'
$sc2.Description = 'SoundMaster - Background Audio Controller'
$sc2.Save()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
    print(f"Created shortcut at: {desktop_shortcut}")
    print(f"Created shortcut at: {project_shortcut}")


if __name__ == "__main__":
    create_shortcuts()
