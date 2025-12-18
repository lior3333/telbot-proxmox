import subprocess

def shutdown_host():
    subprocess.run(
        ["systemctl", "poweroff"],
        check=True
    )



