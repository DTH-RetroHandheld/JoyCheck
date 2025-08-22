import sdl2
from config import PAD
from ui import UIRenderer

class BodyRenderer:
    def __init__(self, ui: UIRenderer):
        self.ui = ui

    def draw(self, width: int, height: int, header_h: int, footer_h: int,
             stick_deadzone=0.15, trigger_deadzone=0.05, show_log=False):
        """Render main body using the device state and UIRenderer primitives."""
        devs = list(self.ui.devmgr.devices.values())
        dev = devs[0] if devs else None
        if not dev:
            self.ui.font.draw_text("NO CONTROLLER", PAD, header_h + PAD)
            return

        # Optional log panel
        right_margin = 0
        if show_log:
            log_w = max(240, int(width * 0.30))
            self.ui._draw_log(width - log_w - PAD, header_h + PAD,
                              log_w, height - header_h - footer_h - PAD*2)
            right_margin = log_w + PAD*2

        # Working area
        w = width - right_margin
        h = height - header_h - footer_h
        y0 = header_h

        # Key positions
        dpad_cx, dpad_cy   = int(w * 0.22), int(y0 + h * 0.30)
        abxy_cx, abxy_cy   = int(w * 0.78), int(y0 + h * 0.30)
        left_cx, left_cy   = int(w * 0.22), int(y0 + h * 0.74)
        right_cx, right_cy = int(w * 0.78), int(y0 + h * 0.74)
        f_cx, f_cy         = int(w * 0.50), int(y0 + h * 0.14)
        sel_cx, sel_cy     = int(w * 0.42), int(y0 + h * 0.46)
        start_cx, start_cy = int(w * 0.58), int(y0 + h * 0.46)

        base = min(w, h)
        abxy_r = int(base * 0.05)
        pill_w, pill_h = int(base * 0.12 * 1.2 * 1.3), int(base * 0.04 * 1.2 * 1.3)
        f_r = int(base * 0.02 * 1.5)
        abxy_delta = int(abxy_r * 2.3)
        abxy_span = 2 * abxy_delta + 2 * abxy_r
        dpad_size = abxy_span

        # Outer frame of body
        self.ui._draw_rect(sdl2.SDL_Rect(PAD, y0 + PAD, w - PAD*2, h - PAD*2), (90,95,100,255))

        # D-Pad
        self.ui._dpad(dpad_cx, dpad_cy, dpad_size, dev)

        # ABXY buttons
        A = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_A', 0)
        B = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_B', 1)
        X = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_X', 2)
        Y = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_Y', 3)
        self.ui._button_circle(abxy_cx, abxy_cy - abxy_delta, abxy_r, "X", dev.buttons.get(X,0)==1, (60,80,200,220), (40,44,48,255))
        self.ui._button_circle(abxy_cx - abxy_delta, abxy_cy, abxy_r, "Y", dev.buttons.get(Y,0)==1, (40,160,80,220), (40,44,48,255))
        self.ui._button_circle(abxy_cx + abxy_delta, abxy_r + abxy_cy, abxy_r, "A", dev.buttons.get(A,0)==1, (200,60,60,220), (40,44,48,255))
        self.ui._button_circle(abxy_cx, abxy_cy + abxy_delta, abxy_r, "B", dev.buttons.get(B,0)==1, (220,170,40,220), (40,44,48,255))

        # FN / GUIDE
        guide = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_GUIDE', 5)
        self.ui._button_circle(f_cx, f_cy, f_r, "F", dev.buttons.get(guide,0)==1, (180,220,160,230), (55,58,62,200))

        # Select / Start
        back = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_BACK', 4)
        start = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_START', 6)
        self.ui._pill(sel_cx, sel_cy, pill_w, pill_h, "SELECT", dev.buttons.get(back,0)==1)
        self.ui._pill(start_cx, start_cy, pill_w, pill_h, "START", dev.buttons.get(start,0)==1)

        # LB/RB + LT/RT
        lb = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_LEFTSHOULDER', 9)
        rb = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_RIGHTSHOULDER', 10)
        lt_axis = getattr(sdl2, 'SDL_CONTROLLER_AXIS_TRIGGERLEFT', 4)
        rt_axis = getattr(sdl2, 'SDL_CONTROLLER_AXIS_TRIGGERRIGHT', 5)
        lt_pressed = (dev.axes.get(lt_axis, 0.0) or 0.0) > 0.5
        rt_pressed = (dev.axes.get(rt_axis, 0.0) or 0.0) > 0.5

        corner_w = max(80, int(base * 0.16))
        corner_h = max(18, int(base * 0.05))
        y_top = y0 + PAD + corner_h//2 + 6
        # Left top
        lb_cx = PAD + corner_w//2 + 8
        lt_cx = lb_cx + corner_w + 10
        self.ui._pill(lb_cx, y_top, corner_w, corner_h, 'L1', dev.buttons.get(lb,0)==1)
        self.ui._pill(lt_cx, y_top, corner_w, corner_h, 'L2', lt_pressed)
        # Right top
        rb_cx = w - PAD - corner_w//2 - 8
        rt_cx = rb_cx - corner_w - 10
        self.ui._pill(rt_cx, y_top, corner_w, corner_h, 'R2', rt_pressed)
        self.ui._pill(rb_cx, y_top, corner_w, corner_h, 'R1', dev.buttons.get(rb,0)==1)

        # Sticks + L3/R3
        lx = dev.axes.get(getattr(sdl2, 'SDL_CONTROLLER_AXIS_LEFTX', 0), 0.0)
        ly = dev.axes.get(getattr(sdl2, 'SDL_CONTROLLER_AXIS_LEFTY', 1), 0.0)
        rx = dev.axes.get(getattr(sdl2, 'SDL_CONTROLLER_AXIS_RIGHTX', 2), 0.0)
        ry = dev.axes.get(getattr(sdl2, 'SDL_CONTROLLER_AXIS_RIGHTY', 3), 0.0)
        self.ui._stick(left_cx, left_cy, int(base * 0.156), lx, ly, stick_deadzone)
        self.ui._stick(right_cx, right_cy, int(base * 0.156), rx, ry, stick_deadzone)

        l3_btn = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_LEFTSTICK', 7)
        r3_btn = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_RIGHTSTICK', 8)
        mini_w = int(base * 0.12 * 1.6); mini_h = max(12, int(base * 0.04 * 1.1))
        self.ui._pill(left_cx, left_cy + int(base * 0.156) + 18, mini_w, mini_h, 'L3', dev.buttons.get(l3_btn,0)==1)
        self.ui._pill(right_cx, right_cy + int(base * 0.156) + 18, mini_w, mini_h, 'R3', dev.buttons.get(r3_btn,0)==1)
