import time
import sdl2

# Helper to normalize signed 16-bit to [-1.0, 1.0]
def _norm(value: int) -> float:
    if value < 0:
        return max(-1.0, value / 32768.0)
    return min(1.0, value / 32767.0)


BUTTON_NAMES = {
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_A', 0): 'A',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_B', 1): 'B',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_X', 2): 'X',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_Y', 3): 'Y',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_LEFTSHOULDER', 9): 'LB',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_RIGHTSHOULDER', 10): 'RB',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_BACK', 4): 'SELECT',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_START', 6): 'START',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_GUIDE', 5): 'GUIDE/FN',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_LEFTSTICK', 7): 'L3',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_RIGHTSTICK', 8): 'R3',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_UP', 11): 'DU',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_DOWN', 12): 'DD',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_LEFT', 13): 'DL',
    getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_RIGHT', 14): 'DR',
}


class Controller:
    def __init__(self, ctrl_ptr, instance_id: int, name: str):
        self.ctrl = ctrl_ptr
        self.instance_id = instance_id
        self.name = name
        self.axes = {
            sdl2.SDL_CONTROLLER_AXIS_LEFTX: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_LEFTY: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_RIGHTX: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_RIGHTY: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT: 0.0,
            sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT: 0.0,
        }
        self.buttons = {btn: 0 for btn in range(sdl2.SDL_CONTROLLER_BUTTON_MAX)}
        self.prev_axes = dict(self.axes)
        self.prev_buttons = dict(self.buttons)
        self.down_time = {}  # btn -> monotonic when pressed

    def poll(self):
        # Axes
        for axis in self.axes.keys():
            raw = sdl2.SDL_GameControllerGetAxis(self.ctrl, axis)
            self.axes[axis] = _norm(raw)
        # Buttons with timestamps
        now = time.monotonic()
        for btn in self.buttons.keys():
            cur = 1 if sdl2.SDL_GameControllerGetButton(self.ctrl, btn) else 0
            prev = self.prev_buttons.get(btn, 0)
            self.buttons[btn] = cur
            if cur == 1 and prev == 0:
                self.down_time[btn] = now
            elif cur == 0 and prev == 1:
                # release; keep timestamp or remove
                self.down_time.pop(btn, None)
            self.prev_buttons[btn] = cur

    def diffs(self, axis_step=0.2):
        events = []
        # Buttons: already updated prev in poll; but emit changes by comparing last known states
        # we can emit based on last change we just applied; to avoid duplicates, rely on prev stored before change
        # Here we will not re-emit; instead, only axes diffs to keep log shorter
        pass
        # Axes (log uses step to reduce noise)
        for axis, cur in self.axes.items():
            prev = self.prev_axes.get(axis, 0.0)
            if abs(cur - prev) >= axis_step:
                aname = {
                    sdl2.SDL_CONTROLLER_AXIS_LEFTX: 'LX',
                    sdl2.SDL_CONTROLLER_AXIS_LEFTY: 'LY',
                    sdl2.SDL_CONTROLLER_AXIS_RIGHTX: 'RX',
                    sdl2.SDL_CONTROLLER_AXIS_RIGHTY: 'RY',
                    sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT: 'LT',
                    sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT: 'RT',
                }.get(axis, f"AX{axis}")
                events.append(f"{self.name}: {aname}={cur:+.2f}")
                self.prev_axes[axis] = cur
        return events

    def combo_exit_pressed(self, window_ms=200) -> bool:
        back = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_BACK', 4)
        start = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_START', 6)
        if self.buttons.get(back, 0) == 1 and self.buttons.get(start, 0) == 1:
            t_back = self.down_time.get(back, None)
            t_start = self.down_time.get(start, None)
            if t_back is None or t_start is None:
                return False
            dt_ms = abs((t_back - t_start) * 1000.0)
            return dt_ms <= float(window_ms)
        return False

    def close(self):
        if self.ctrl:
            sdl2.SDL_GameControllerClose(self.ctrl)
            self.ctrl = None


class DeviceManager:
    def __init__(self):
        self.devices = {}  # instance_id -> Controller

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
        name_ptr = sdl2.SDL_GameControllerName(ctrl)
        name = name_ptr.decode() if name_ptr else f"Controller {instance_id}"
        self.devices[instance_id] = Controller(ctrl, instance_id, name)
        print(f"[add] {name} (iid={instance_id})")

    def remove_by_instance_id(self, instance_id: int):
        dev = self.devices.pop(instance_id, None)
        if dev:
            print(f"[remove] {dev.name} (iid={instance_id})")
            dev.close()

    def update_states(self):
        for dev in list(self.devices.values()):
            dev.poll()

    def diff_events(self, axis_step=0.2):
        out = []
        for dev in self.devices.values():
            out.extend(dev.diffs(axis_step=axis_step))
        return out

    def check_combo_exit(self, window_ms=200) -> bool:
        for dev in self.devices.values():
            if dev.combo_exit_pressed(window_ms=window_ms):
                return True
        return False
