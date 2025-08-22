
import time
import sdl2

# Normalize signed 16-bit to [-1.0, 1.0]
def _norm(value: int) -> float:
    if value < 0:
        return max(-1.0, value / 32768.0)
    return min(1.0, value / 32767.0)


class Controller:
    def __init__(self, ctrl_ptr, instance_id: int, name: str):
        self.ctrl = ctrl_ptr
        self.instance_id = instance_id
        self.name = name

        # Axes and buttons snapshots
        self.axes = {
            sdl2.SDL_CONTROLLER_AXIS_LEFTX: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_LEFTY: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_RIGHTX: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_RIGHTY: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT: 0.0,
        }
        self.prev_axes = dict(self.axes)

        self.buttons = {btn: 0 for btn in range(sdl2.SDL_CONTROLLER_BUTTON_MAX)}
        self.prev_buttons = dict(self.buttons)

        self.down_time = {}   # btn -> t when pressed
        self._edge_buf = []   # list of (btn, pressed: bool)

    def update(self):
        """Poll current states and compute edges."""
        # Buttons
        for btn in range(sdl2.SDL_CONTROLLER_BUTTON_MAX):
            cur = sdl2.SDL_GameControllerGetButton(self.ctrl, btn)
            cur = 1 if cur else 0
            prev = self.buttons.get(btn, 0)
            if cur != prev:
                # edge
                self._edge_buf.append((btn, cur == 1))
                if cur == 1:
                    self.down_time[btn] = time.time()
                else:
                    self.down_time.pop(btn, None)
            self.prev_buttons[btn] = prev
            self.buttons[btn] = cur

        # Axes
        for axis in list(self.axes.keys()):
            raw = sdl2.SDL_GameControllerGetAxis(self.ctrl, axis)
            self.prev_axes[axis] = self.axes.get(axis, 0.0)
            self.axes[axis] = _norm(int(raw))

    def button_edges(self):
        """Return and clear edge buffer as [(btn, pressed_bool), ...]."""
        out = self._edge_buf[:]
        self._edge_buf.clear()
        return out

    def diffs(self, axis_step=0.2):
        """Return axis change events above threshold [(axis, prev, cur), ...]."""
        events = []
        for axis, cur in self.axes.items():
            prev = self.prev_axes.get(axis, 0.0)
            if abs(cur - prev) >= float(axis_step):
                events.append((axis, prev, cur))
        return events

    def combo_exit_pressed(self, window_ms=200) -> bool:
        back = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_BACK', 4)
        start = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_START', 6)
        if self.buttons.get(back, 0) == 1 and self.buttons.get(start, 0) == 1:
            t_back = self.down_time.get(back)
            t_start = self.down_time.get(start)
            if t_back is None or t_start is None:
                return False
            return abs((t_back - t_start) * 1000.0) <= float(window_ms)
        return False

    def close(self):
        if self.ctrl:
            sdl2.SDL_GameControllerClose(self.ctrl)
            self.ctrl = None


class DeviceManager:
    def __init__(self):
        self.devices = {}  # instance_id -> Controller
        self.initial_scan()

    def initial_scan(self):
        n = sdl2.SDL_NumJoysticks()
        for i in range(n):
            if sdl2.SDL_IsGameController(i):
                self.add_by_index(i)

    def add_by_index(self, device_index: int):
        ctrl = sdl2.SDL_GameControllerOpen(device_index)
        if not ctrl:
            return
        joy = sdl2.SDL_GameControllerGetJoystick(ctrl)
        instance_id = sdl2.SDL_JoystickInstanceID(joy)
        name = sdl2.SDL_GameControllerName(ctrl)
        name = name.decode('utf-8') if isinstance(name, (bytes, bytearray)) else str(name)
        self.devices[instance_id] = Controller(ctrl, instance_id, name)

    def remove_by_instance_id(self, instance_id: int):
        dev = self.devices.pop(instance_id, None)
        if dev:
            dev.close()

    def update_states(self):
        # Hotplug handling via events is optional; here we just poll existing devices
        for dev in list(self.devices.values()):
            dev.update()

    def diff_events(self, axis_step=0.2):
        out = []
        for dev in self.devices.values():
            out.extend(dev.diffs(axis_step=axis_step))
        return out

    def button_edges(self):
        out = []
        for iid, dev in self.devices.items():
            for btn, pressed in dev.button_edges():
                out.append((iid, btn, pressed))
        return out

    def check_combo_exit(self, window_ms=200) -> bool:
        for dev in self.devices.values():
            if dev.combo_exit_pressed(window_ms=window_ms):
                return True
        return False
