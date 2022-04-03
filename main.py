import os
from pathlib import Path
import os, subprocess
from subprocess import PIPE, Popen

BASE = os.getcwd()


def goto_base():
    run_cmd(f'cd {BASE}')


def run_cmd(cmd: str):
    os.system(cmd)


def install_deps():
    cmd_apt = 'sudo apt install -y wget'
    run_cmd(cmd_apt)


def install_blueline():
    file = 'blueline-pq3a.190801.002-factory-f3d66c49.zip'
    folder = 'blueline-pq3a.190801.002'

    if not Path(BASE, file).is_file():
        run_cmd(f'wget https://dl.google.com/dl/android/aosp/{file}')

    if not Path(BASE, folder).is_dir():
        run_cmd(f'unzip {file}')

    run_cmd(f'{BASE}/{folder}/flash-all.sh')


def root_phone():
    run_cmd(
        'wget https://github.com/termux/termux-app/releases/download/v0.118.0/termux-app_v0.118.0+github-debug_arm64-v8a.apk')
    run_cmd('wget https://github.com/topjohnwu/Magisk/releases/download/v24.2/Magisk-v24.2.apk')
    run_cmd('adb install termux-app_v0.118.0+github-debug_arm64-v8a.apk')
    run_cmd('adb install Magisk-v24.2.apk')
    run_cmd('adb reboot bootloader')
    run_cmd('fastboot flash boot boot_magisk_patched.img')
    run_cmd('fastboot reboot')


def install_userspace():
    run_cmd(f'adb push {BASE}/userspace.tar.gz /sdcard/Download/')

    adb_shell = subprocess.Popen('adb shell', stdin=subprocess.PIPE)
    adb_shell.communicate(
        "su\ncd /data/data/com.termux/\nmkkdir files && cd files\ntar xvf /sdcard/Download/userspace.tar.gz\nmount -o remount,rw /dev/root /\nln -s /data/data/com.termux/files/usr /usr\nexit\nsu -c 'HOME=/data/data/com.termux/files/home PATH=\"/data/data/com.termux/files/usr/bin:/bin\" LD_LIBRARY_PATH=\"/data/data/com.termux/files/usr/lib\" bash'\nmkdir -p tmp && mount -t tmpfs -o size=2048M tmpfs /tmp\ncd ~\ntmux\napt-get update\napt-get install gawk findutils\nchmod 644 /data/data/com.termux/files/home/.ssh/config\nchown root:root /data/data/com.termux/files/home/.ssh/config\n./install.sh")


if __name__ == '__main__':
    install_deps()
    install_blueline()
    root_phone()