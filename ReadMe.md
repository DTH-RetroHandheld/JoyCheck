# JoyCheck (PortMaster)

A controller tester for Linux retro handhelds running **PortMaster**. It shows button, axis, and D-Pad states in real time. Use it for quick checks after remapping or swapping controllers.

## Features
- Real-time visualization of Button / Axis / Hat (D-Pad).
- Hot-swap support for multiple controllers.
- Fullscreen layout optimized for handhelds.
- Optional logging for diagnostics.

## Requirements
- **PortMaster** installed.

## Installation
**ArkOS and Rocknix**  
Copy the **JoyCheck** folder and the **JoyCheck.sh** file to:
```
/roms/ports
```

**muOS**  
Copy the **JoyCheck** folder to:
```
/ports
```
Copy the **JoyCheck.sh** file to:
```
/roms/ports
```

**CrossMix**  
Copy the **JoyCheck** folder and the **JoyCheck.sh** file to:
```
/Data/ports
```

Make the launcher executable (adjust path if different):
```
chmod +x /roms/ports/JoyCheck.sh
```

## Usage
- Launch from **PortMaster → Ports → JoyCheck**.
- Plug in or pair controllers before launch for immediate detection.
- Hot-swap is supported. If a device is not detected, exit and relaunch.

## Logs and troubleshooting
- Default log: `/roms/ports/joycheck/run.log`.
- If inputs do not appear:
  - Check USB/Bluetooth connections and system mappings.
  - Ensure `JoyCheck.sh` is executable.
  - Confirm the PortMaster paths match your firmware layout.

## Compatibility
- Verified with PortMaster **2025.07.14-1510**: https://github.com/PortsMaster/PortMaster-GUI/releases

## Credits & attribution
- Portions of design and workflow were informed by **PortMaster-GUI**. PortMaster and PortMaster-GUI are separate projects. JoyCheck is an independent project and is **not affiliated with or endorsed by** those maintainers.
- All trademarks and product names are the property of their respective owners.

## License and copyright
- **License:** MIT
- **Copyright © 2025 To Hung Duong** <HungDuongWP@gmail.com>
- Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction under the terms of the MIT License.
- If you redistribute JoyCheck in source or binary form, please retain this notice and the MIT license text.
- Contact: <HungDuongWP@gmail.com>
