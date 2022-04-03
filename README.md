# Openpilot Pixel3 Installer

## Run Installer
- clone ```https://github.com/lukasloetkolben/pixel3_installer.git && cd pixel3_installer```
- run ```sudo ./main.py``` and follow the instructions.


## Unlock Bootloader

- Go to Settings > About Phone
- Tap Software Info > Build Number
- Tap Build Number seven times
- Go to Settings > System > Advanced > Developer Options 
- Enable USB debugging
- Enable OEM unlocking
- Enter Fastboot Mode
- Run ```fastboot flashing unlock```

## Wipe Data
- Download TWRP-3.3.0 https://eu.dl.twrp.me/blueline/twrp-3.3.0-0-blueline.img.html
- Enter Fastboot Mode
- Run ```fastboot boot twrp-3.3.0-0-blueline.img```
  - Go to WIPE
  - Select "Data" & "Cache"
  - Swipe to wipe!'