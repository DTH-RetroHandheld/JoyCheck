

XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

EXLIBS="$controlfolder/exlibs"
if [ -d "$EXLIBS" ]; then
  export PYTHONPATH="$EXLIBS${PYTHONPATH:+:$PYTHONPATH}"
fi

source $controlfolder/control.txt
source $controlfolder/device_info.txt
source $controlfolder/tasksetter

get_controls

gamedir="/$directory/ports/JoyCheck"
cd "$gamedir/"

# Grab text output...
$ESUDO chmod 666 /dev/tty0
printf "\033c" > /dev/tty0


mkdir -p "$gamedir/logs"
$ESUDO chmod 666 /dev/tty0 || true
printf "\033c" > /dev/tty0 || true

echo "JoyCheck: starting..." | tee -a "$gamedir/run.log" > /dev/tty0

if type set_affinity >/dev/null 2>&1; then
  set_affinity || true
fi
if type set_priority >/dev/null 2>&1; then
  set_priority || true
fi

python3 app.py 2>&1 | tee -a "$gamedir/run.log" > /dev/tty0
