import os
import subprocess
import time
from pathlib import Path

# URLs
blueline_url = "https://dl.google.com/dl/android/aosp/blueline-pq3a.190801.002-factory-f3d66c49.zip"
termux_apk_url = "https://github.com/termux/termux-app/releases/download/v0.118.0/termux-app_v0.118.0+github-debug_arm64-v8a.apk"
magisk_apk_url = "https://github.com/topjohnwu/Magisk/releases/download/v24.2/Magisk-v24.2.apk"
patched_boot_img_url = "https://transfer.sh/ormqXH/boot_magisk_patched.img"
userspace_url = "https://transfer.sh/LVVEJE/userspace.tar.gz"
platform_tools_url = "https://dl.google.com/android/repository/platform-tools_r29.0.5-linux.zip"

BASE = os.getcwd()

fastboot_path = ""


def download_platform_tools():
    file = "platform-tools.zip"
    folder = "platform-tools"

    if not Path(BASE, folder).is_dir():
        if not Path(BASE, file).is_file():
            run_cmd(f"curl -L {platform_tools_url} --output platform-tools.zip")

        run_cmd(f'unzip {Path(BASE, file)}')
    global fastboot_path
    fastboot_path = Path(BASE, folder, "fastboot")

def goto_base():
    run_cmd(f'cd {BASE}')


def adb_reboot_bootloader():
    run_cmd('adb reboot bootloader')
    time.sleep(8)


def fastboot_reboot_bootloader():
    _subprocess([fastboot_path, 'reboot-bootloader'])
    time.sleep(5)


def _subprocess(arg_list):
    arg_list = [str(s) for s in arg_list]
    print("RUN " + " ".join(arg_list))
    return subprocess.check_output(arg_list)


def run_cmd(cmd: str):
    print(f"RUN {cmd}")
    os.system(cmd)


def install_deps():
    cmd_apt = 'sudo apt install -y wget curl android-tools-adb'
    run_cmd(cmd_apt)


def download_blueline():
    file = 'blueline-pq3a.190801.002-factory-f3d66c49.zip'
    folder = 'blueline-pq3a.190801.002'

    if not Path(BASE, file).is_file():
        run_cmd(f'wget {blueline_url}')

    if not Path(BASE, folder).is_dir():
        run_cmd(f'unzip {Path(BASE, file)}')


def install_blueline():
    adb_reboot_bootloader()
    folder = 'blueline-pq3a.190801.002'
    bootloader_img = Path(BASE, folder, 'bootloader-blueline-b1c1-0.1-5578427.img')
    _subprocess([fastboot_path, 'flash', 'bootloader', bootloader_img])
    fastboot_reboot_bootloader()
    radio_img = Path(BASE, folder, 'radio-blueline-g845-00017-190312-b-5369743.img')
    _subprocess([fastboot_path, 'flash', 'radio', radio_img])
    fastboot_reboot_bootloader()

    update_img = Path(BASE, folder, "image-blueline-pq3a.190801.002.zip")
    _subprocess([fastboot_path, '-w', 'update', update_img])


def root_phone():
    if not Path(BASE, "termux-app_v0.118.0+github-debug_arm64-v8a.apk").is_file():
        run_cmd(f'wget {termux_apk_url}')
    if not Path(BASE, "Magisk-v24.2.apk").is_file():
        run_cmd(f'wget {magisk_apk_url}')

    run_cmd('adb install termux-app_v0.118.0+github-debug_arm64-v8a.apk')
    run_cmd('adb install Magisk-v24.2.apk')
    adb_reboot_bootloader()

    if not Path(BASE, "boot_magisk_patched.img").is_file():
        run_cmd(f'wget {patched_boot_img_url}')

    _subprocess([fastboot_path, 'flash', 'boot', 'boot_magisk_patched.img'])
    _subprocess([fastboot_path, 'reboot'])


def adb_superuser():
    process = subprocess.Popen(
        "adb shell",
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    process.communicate(b"su\n")


def install_userspace():
    file = 'userspace.tar.gz'
    if not Path(BASE, file).is_file():
        run_cmd(f'wget {userspace_url}')

    run_cmd(f'adb push {BASE}/{file} /sdcard/Download/')

    process = subprocess.Popen(
        "adb shell",
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    process.communicate(b"su\n"
                        b"mkdir /data/data/com.termux/files/\n"
                        b"tar -xvzf /sdcard/Download/userspace.tar.gz -C /data/data/com.termux/files\n"
                        b"mount -o remount,rw /dev/root /\n"
                        b"ln -s /data/data/com.termux/files/usr /usr\n"
                        b"exit\n"
                        b"su -c 'HOME=/data/data/com.termux/files/home PATH=\"/data/data/com.termux/files/usr/bin:/bin\" LD_LIBRARY_PATH=\"/data/data/com.termux/files/usr/lib\" bash'\n"
                        b"mkdir -p /tmp\n"
                        b"mount -t tmpfs -o size=2048M tmpfs /tmp\n"
                        b"tmux\n"
                        b"apt-get update\n"
                        b"apt-get install gawk findutils\n"
                        b"chmod 644 /data/data/com.termux/files/home/.ssh/config\n"
                        b"chown root:root /data/data/com.termux/files/home/.ssh/config\n"
                        b"/data/data/com.termux/files/home/install.sh\n"
                        b"touch /EON\n"
                        b"git clone https://github.com/commaai/openpilot.git /data/openpilot --recurse-submodules -b pixel3\n"
                        b"cd openpilot\n"
                        b"scons -j4\n"
                        b"cp /data/openpilot/third_party/qt-plugins/aarch64/libqeglfs-surfaceflinger-integration.so /usr/libexec/qt/egldeviceintegrations/\n"
                        b"./launch_openpilot.sh\n")


def print_sep():

    print(100 * "#")
    print(100 * "#")

def run():
    download_platform_tools()
    print_sep()
    _ = input('Make sure your Bootloader is unlocked.\n'
              'Boot the phone to Android and make sure USB debugging (ADB) is activated!\n'
              'Press [ENTER] to confirm.')
    install_deps()
    download_blueline()
    install_blueline()
    print_sep()
    _ = input('WAIT UNTIL YOUR PHONE IS BOOTED!\n'
              '1.) Setup your Phone and connect to WIFI\n'
              '2.) Go to Settings > About Phone\n'
              '3.) Tap Software Info > Build Number\n'
              '4.) Tap Build Number seven times\n'
              '5.) Go to Settings > System > Advanced > Developer Options and enable USB debugging\n'
              'Press [ENTER] when you are done.')
    root_phone()
    print_sep()
    _ = input('WAIT UNTIL YOUR PHONE IS BOOTED!\n'
              'Press [ENTER] when the phone has booted.')
    adb_superuser()
    print_sep()
    _ = input('Open Magisk > Superuser and enable Superuser rights of Shell\n'
              'Press [ENTER] when you are done.')
    #install_userspace()


if __name__ == '__main__':
    run()
