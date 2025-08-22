from pathlib import Path
import math
import sdl2
import sdl2.surface
import sdl2.sdlttf as sdlttf

from config import PAD, PANEL_BG, PANEL_ACCENT, AXIS_BAR_BG, AXIS_BAR_FG

try:
    from port_gui.gui import FontManager
except Exception:
    FontManager = None


class EventLog:
    def __init__(self, max_lines=200):
        from collections import deque
        self.lines = deque(maxlen=max_lines)
    def add(self, text: str):
        self.lines.append(text)
    def tail(self, n):
        n = max(0, n)
        if n >= len(self.lines):
            return list(self.lines)
        return list(self.lines)[-n:]
    def clear(self):
        self.lines.clear()


class TinyFont:
    GLYPHS = {
        'A':[0b01110,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
        'B':[0b11110,0b10001,0b11110,0b10001,0b10001,0b10001,0b11110],
        'C':[0b01110,0b10001,0b10000,0b10000,0b10000,0b10001,0b01110],
        'D':[0b11110,0b10001,0b10001,0b10001,0b10001,0b10001,0b11110],
        'E':[0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b11111],
        'F':[0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b10000],
        'G':[0b01110,0b10001,0b10000,0b10111,0b10001,0b10001,0b01110],
        'H':[0b10001,0b10001,0b11111,0b10001,0b10001,0b10001,0b10001],
        'I':[0b01110,0b00100,0b00100,0b00100,0b00100,0b00100,0b01110],
        'J':[0b00111,0b00010,0b00010,0b00010,0b10010,0b10010,0b01100],
        'K':[0b10001,0b10010,0b10100,0b11000,0b10100,0b10010,0b10001],
        'L':[0b10000,0b10000,0b10000,0b10000,0b10000,0b10000,0b11111],
        'M':[0b10001,0b11011,0b10101,0b10101,0b10001,0b10001,0b10001],
        'N':[0b10001,0b11001,0b10101,0b10011,0b10001,0b10001,0b10001],
        'O':[0b01110,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
        'P':[0b11110,0b10001,0b10001,0b11110,0b10000,0b10000,0b10000],
        'Q':[0b01110,0b10001,0b10001,0b10001,0b10101,0b10010,0b01101],
        'R':[0b11110,0b10001,0b10001,0b11110,0b10100,0b10010,0b10001],
        'S':[0b01111,0b10000,0b10000,0b01110,0b00001,0b00001,0b11110],
        'T':[0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b00100],
        'U':[0b10001,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
        'V':[0b10001,0b10001,0b10001,0b10001,0b01010,0b01010,0b00100],
        'W':[0b10001,0b10001,0b10001,0b10101,0b10101,0b11011,0b10001],
        'X':[0b10001,0b01010,0b00100,0b00100,0b00100,0b01010,0b10001],
        'Y':[0b10001,0b01010,0b00100,0b00100,0b00100,0b00100,0b00100],
        'Z':[0b11111,0b00001,0b00010,0b00100,0b01000,0b10000,0b11111],
        '0':[0b01110,0b10001,0b10011,0b10101,0b11001,0b10001,0b01110],
        '1':[0b00100,0b01100,0b00100,0b00100,0b00100,0b00100,0b01110],
        '2':[0b01110,0b10001,0b00001,0b00010,0b00100,0b01000,0b11111],
        '3':[0b11110,0b00001,0b00001,0b00110,0b00001,0b00001,0b11110],
        '4':[0b00010,0b00110,0b01010,0b10010,0b11111,0b00010,0b00010],
        '5':[0b11111,0b10000,0b11110,0b00001,0b00001,0b10001,0b01110],
        '6':[0b00110,0b01000,0b10000,0b11110,0b10001,0b10001,0b01110],
        '7':[0b11111,0b00001,0b00010,0b00100,0b01000,0b10000,0b10000],
        '8':[0b01110,0b10001,0b10001,0b01110,0b10001,0b10001,0b01110],
        '9':[0b01110,0b10001,0b10001,0b01111,0b00001,0b00010,0b01100],
        ' ': [0b00000]*7,
    }
    W, H = 5, 7
    def __init__(self, renderer, scale=2):
        self.ren = renderer
        self.scale = max(1, int(scale))
    def size(self, text):
        return ((self.W+1)*self.scale*len(text), self.H*self.scale)
    def draw(self, text, x, y):
        sx = self.scale
        for ch in str(text).upper():
            glyph = self.GLYPHS.get(ch, self.GLYPHS[' '])
            for row, bits in enumerate(glyph):
                for col in range(self.W):
                    if bits & (1 << (self.W - 1 - col)):
                        rx = x + col * sx
                        ry = y + row * sx
                        sdl2.SDL_SetRenderDrawColor(self.ren, 230, 230, 230, 255)
                        sdl2.SDL_RenderFillRect(self.ren, sdl2.SDL_Rect(rx, ry, sx, sx))
            x += (self.W + 1) * sx


class Font:
    def __init__(self, renderer):
        self.renderer = renderer
        self.color = sdl2.SDL_Color(230, 230, 230, 255)
        self.ttf = None
        self.fm = None
        self.tiny = None
        if FontManager is not None:
            try:
                self.fm = FontManager(renderer)
                font_path = Path("Roboto-Regular.ttf")
                if font_path.exists():
                    self.fm.load(str(font_path))
            except Exception:
                self.fm = None
        if self.fm is None:
            if sdlttf.TTF_WasInit() == 0:
                sdlttf.TTF_Init()
            font_path = Path("Roboto-Regular.ttf")
            if font_path.exists():
                self.ttf = sdlttf.TTF_OpenFont(bytes(str(font_path), "utf-8"), 18)
        if self.fm is None and self.ttf is None:
            self.tiny = TinyFont(renderer, scale=2)
    def text_size(self, text):
        if self.ttf:
            w = sdl2.Sint32()
            h = sdl2.Sint32()
            if sdlttf.TTF_SizeUTF8(self.ttf, text.encode("utf-8"), w, h) == 0:
                return int(w.value), int(h.value)
        if self.tiny:
            return self.tiny.size(text)
        return (len(text)*8, 16)
    def draw_text(self, text: str, x: int, y: int):
        if self.fm is not None:
            try:
                self.fm.draw(text, x, y)
                return
            except Exception:
                pass
        if self.ttf:
            surf = sdlttf.TTF_RenderUTF8_Blended(self.ttf, text.encode("utf-8"), self.color)
            if surf:
                tex = sdl2.SDL_CreateTextureFromSurface(self.renderer, surf)
                dst = sdl2.SDL_Rect(x, y, surf.contents.w, surf.contents.h)
                sdl2.SDL_RenderCopy(self.renderer, tex, None, dst)
                sdl2.SDL_DestroyTexture(tex)
                sdl2.SDL_FreeSurface(surf)
                return
        if self.tiny is not None:
            self.tiny.draw(text, x, y)
    def draw_center(self, text: str, cx: int, cy: int):
        w, h = self.text_size(text)
        self.draw_text(text, cx - w//2, cy - h//2)


class UIRenderer:
    def __init__(self, renderer, devmgr, eventlog: EventLog):
        self.ren = renderer
        self.devmgr = devmgr
        self.log = eventlog
        self.font = Font(renderer)

    def _fill_rect(self, rect, color):
        sdl2.SDL_SetRenderDrawColor(self.ren, *color)
        sdl2.SDL_RenderFillRect(self.ren, rect)
    def _draw_rect(self, rect, color):
        sdl2.SDL_SetRenderDrawColor(self.ren, *color)
        sdl2.SDL_RenderDrawRect(self.ren, rect)
    def _draw_circle(self, cx, cy, r, color):
        sdl2.SDL_SetRenderDrawColor(self.ren, *color)
        steps = max(24, int(r * 0.8))
        for i in range(steps):
            ang = 2 * math.pi * i / steps
            x = int(cx + r * math.cos(ang))
            y = int(cy + r * math.sin(ang))
            sdl2.SDL_RenderDrawPoint(self.ren, x, y)
    def _fill_circle(self, cx, cy, r, color):
        sdl2.SDL_SetRenderDrawColor(self.ren, *color)
        for dy in range(-r, r + 1):
            w = int((r*r - dy*dy) ** 0.5)
            sdl2.SDL_RenderDrawLine(self.ren, cx - w, cy + dy, cx + w, cy + dy)
    def _fill_triangle(self, p1, p2, p3, color):
        sdl2.SDL_SetRenderDrawColor(self.ren, *color)
        pts = sorted([p1, p2, p3], key=lambda p: p[1])
        (x1,y1),(x2,y2),(x3,y3)=pts
        def interp(y, xa,ya, xb,yb):
            if yb==ya: return xa
            return xa + (xb-xa)*(y-ya)/(yb-ya)
        y = int(y1)
        while y <= int(y3):
            if y < y2:
                xa = interp(y, x1,y1, x2,y2)
                xb = interp(y, x1,y1, x3,y3)
            else:
                xa = interp(y, x2,y2, x3,y3)
                xb = interp(y, x1,y1, x3,y3)
            if xa>xb: xa,xb=xb,xa
            sdl2.SDL_RenderDrawLine(self.ren, int(xa), y, int(xb), y)
            y += 1

    def _stick(self, cx, cy, r, xval, yval, deadzone):
        self._fill_circle(cx, cy, r, (40, 44, 48, 255))
        self._draw_circle(cx, cy, r, (100, 105, 110, 255))
        self._draw_circle(cx, cy, int(r*0.86), (140,145,150,255))
        dzr = int(r*0.86*max(0.0, min(1.0, deadzone)))
        if dzr > 0:
            self._draw_circle(cx, cy, dzr, (200, 180, 120, 180))
        sdl2.SDL_SetRenderDrawColor(self.ren, 120,125,130,200)
        sdl2.SDL_RenderDrawLine(self.ren, cx - r, cy, cx + r, cy)
        sdl2.SDL_RenderDrawLine(self.ren, cx, cy - r, cx, cy + r)
        px = cx + int(int(r*0.86) * max(-1.0, min(1.0, xval)))
        py = cy + int(int(r*0.86) * max(-1.0, min(1.0, yval)))
        self._fill_rect(sdl2.SDL_Rect(px - 3, py - 3, 6, 6), (220, 230, 210, 255))

    def _button_circle(self, cx, cy, r, label, pressed, color_on, color_off):
        col = color_on if pressed else color_off
        self._fill_circle(cx, cy, r, col)
        self._draw_circle(cx, cy, r, (230,230,230,220))
        self.font.draw_center(label, cx, cy)

    def _pill(self, cx, cy, w, h, label, pressed):
        x = cx - w//2
        y = cy - h//2
        self._fill_rect(sdl2.SDL_Rect(x, y, w, h), (80,160,120,200) if pressed else (55,58,62,200))
        self._draw_rect(sdl2.SDL_Rect(x, y, w, h), PANEL_ACCENT)
        self.font.draw_center(label, cx, cy)

    def _dpad(self, cx, cy, size, dev):
        arm = size // 3
        gap = max(8, size // 8)  # increased spacing between D-Pad buttons
        up_r = sdl2.SDL_Rect(cx - arm//2, cy - gap - arm, arm, arm)
        down_r = sdl2.SDL_Rect(cx - arm//2, cy + gap, arm, arm)
        left_r = sdl2.SDL_Rect(cx - gap - arm, cy - arm//2, arm, arm)
        right_r = sdl2.SDL_Rect(cx + gap, cy - arm//2, arm, arm)
        hub_r = sdl2.SDL_Rect(cx - arm//2, cy - arm//2, arm, arm)
        def draw_btn(rect, pressed):
            self._fill_rect(rect, (80,160,120,200) if pressed else (55,58,62,200))
            self._draw_rect(rect, PANEL_ACCENT)
        btn_up = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_UP', 11)
        btn_down = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_DOWN', 12)
        btn_left = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_LEFT', 13)
        btn_right = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_DPAD_RIGHT', 14)
        draw_btn(up_r,    dev.buttons.get(btn_up,0)==1)
        draw_btn(down_r,  dev.buttons.get(btn_down,0)==1)
        draw_btn(left_r,  dev.buttons.get(btn_left,0)==1)
        draw_btn(right_r, dev.buttons.get(btn_right,0)==1)
        self._fill_rect(hub_r, (45,48,52,200))
        self._draw_rect(hub_r, PANEL_ACCENT)
        arrow_col = (230,230,230,220)
        m = 4
        self._fill_triangle((up_r.x + up_r.w//2, up_r.y + m),
                            (up_r.x + m, up_r.y + up_r.h - m),
                            (up_r.x + up_r.w - m, up_r.y + up_r.h - m),
                            arrow_col)
        self._fill_triangle((down_r.x + down_r.w//2, down_r.y + down_r.h - m),
                            (down_r.x + m, down_r.y + m),
                            (down_r.x + down_r.w - m, down_r.y + m),
                            arrow_col)
        self._fill_triangle((left_r.x + m, left_r.y + left_r.h//2),
                            (left_r.x + left_r.w - m, left_r.y + m),
                            (left_r.x + left_r.w - m, left_r.y + left_r.h - m),
                            arrow_col)
        self._fill_triangle((right_r.x + right_r.w - m, right_r.y + right_r.h//2),
                            (right_r.x + m, right_r.y + m),
                            (right_r.x + m, right_r.y + right_r.h - m),
                            arrow_col)

    def _draw_log(self, x, y, w, h):
        self._fill_rect(sdl2.SDL_Rect(x, y, w, h), PANEL_BG)
        self._draw_rect(sdl2.SDL_Rect(x, y, w, h), PANEL_ACCENT)
        self.font.draw_text("LOG C TO CLEAR  L TO TOGGLE", x + 8, y + 8)
        line_h = 18
        max_lines = max(1, (h - 30) // line_h)
        lines = self.log.tail(max_lines)
        py = y + 28
        for ln in lines:
            self.font.draw_text(ln, x + 8, py)
            py += line_h
    # === Split methods ===
    def draw_header(self, width: int, header_h: int, stats: dict):
        from ui_header import HeaderRenderer
        HeaderRenderer(self).draw(width, header_h, stats or {})
    def draw_footer(self, width: int, height: int, footer_h: int):
        from ui_footer import FooterRenderer
        FooterRenderer(self).draw(width, height, footer_h)
    def draw_body(self, width: int, height: int, header_h: int, footer_h: int,
                  stick_deadzone=0.15, trigger_deadzone=0.05, show_log=False):
        from ui_body import BodyRenderer
        BodyRenderer(self).draw(width, height, header_h, footer_h,
                                stick_deadzone, trigger_deadzone, show_log)



    def draw(self, width: int, height: int, stick_deadzone=0.15, trigger_deadzone=0.05, stats=None, fn_key=False, show_log=False):
        pad = max(8, int(min(width, height) * 0.015))
        header_h = int(height * 0.10)
        footer_h = int(height * 0.10)
        # header
        self._fill_rect(sdl2.SDL_Rect(0, 0, width, header_h), (32, 35, 38, 255))
        self._draw_rect(sdl2.SDL_Rect(0, 0, width, header_h), (90, 95, 100, 255))
        hdr = f"JoyCheck  DEVS:{stats.get('devices',0) if stats else 0}  FPS:{stats.get('fps',0) if stats else 0}  DZ STICK:{stick_deadzone:.2f}  DZ TRIG:{trigger_deadzone:.2f}"
        _hw,_hh = self.font.text_size(hdr)
        _hy = max(0, (header_h - _hh)//2)
        self.font.draw_text(hdr, pad, _hy)
        # footer
        self._fill_rect(sdl2.SDL_Rect(0, height - footer_h, width, footer_h), (32, 35, 38, 255))
        self._draw_rect(sdl2.SDL_Rect(0, height - footer_h, width, footer_h), (90, 95, 100, 255))
        _ft = "DuongTH - HungDuongWP@gmail.com"
        _fw,_fh = self.font.text_size(_ft)
        _fy = height - footer_h + max(0, (footer_h - _fh)//2)
        self.font.draw_text(_ft, pad, _fy)

        devs = list(self.devmgr.devices.values())
        dev = devs[0] if devs else None
        if not dev:
            self.font.draw_text("NO CONTROLLER", pad, header_h + pad)
            return

        right_margin = 0
        if show_log:
            log_w = max(240, int(width * 0.30))
            self._draw_log(width - log_w - pad, header_h + pad, log_w, height - header_h - footer_h - pad*2)
            right_margin = log_w + pad*2

        w = width - right_margin
        h = height - header_h - footer_h
        y0 = header_h

        # centers
        dpad_cx, dpad_cy = int(w * 0.22), int(y0 + h * 0.30)
        abxy_cx, abxy_cy = int(w * 0.78), int(y0 + h * 0.30)
        left_cx, left_cy = int(w * 0.22), int(y0 + h * 0.74)
        right_cx, right_cy = int(w * 0.78), int(y0 + h * 0.74)
        f_cx, f_cy = int(w * 0.50), int(y0 + h * 0.14)
        sel_cx, sel_cy = int(w * 0.42), int(y0 + h * 0.46)
        start_cx, start_cy = int(w * 0.58), int(y0 + h * 0.46)

        base = min(w, h)
        abxy_r = int(base * 0.05)
        # Select/Start bigger
        pill_w, pill_h = int(base * 0.12 * 1.2 * 1.3), int(base * 0.04 * 1.2 * 1.3)
        f_r = int(base * 0.02 * 1.5)

        # ABXY span to match D-pad
        abxy_delta = int(abxy_r * 2.3)
        abxy_span = 2 * abxy_delta + 2 * abxy_r
        dpad_size = abxy_span

        self._draw_rect(sdl2.SDL_Rect(pad, y0 + pad, w - pad*2, h - pad*2), PANEL_ACCENT)

        # D-Pad
        self._dpad(dpad_cx, dpad_cy, dpad_size, dev)

        # ABXY plus layout
        A = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_A', 0)
        B = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_B', 1)
        X = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_X', 2)
        Y = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_Y', 3)
        self._button_circle(abxy_cx, abxy_cy - abxy_delta, abxy_r, "X",
                            dev.buttons.get(X,0)==1, (60,80,200,220), (40,44,48,255))
        self._button_circle(abxy_cx - abxy_delta, abxy_cy, abxy_r, "Y",
                            dev.buttons.get(Y,0)==1, (40,160,80,220), (40,44,48,255))
        self._button_circle(abxy_cx + abxy_delta, abxy_cy, abxy_r, "A",
                            dev.buttons.get(A,0)==1, (200,60,60,220), (40,44,48,255))
        self._button_circle(abxy_cx, abxy_cy + abxy_delta, abxy_r, "B",
                            dev.buttons.get(B,0)==1, (220,170,40,220), (40,44,48,255))

        # FN circle
        guide = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_GUIDE', 5)
        fn_pressed = dev.buttons.get(guide,0)==1
        self._button_circle(f_cx, f_cy, f_r, "F", fn_pressed, (180, 220, 160, 230), (55,58,62,200))

        # Select / Start pills
        back = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_BACK', 4)
        start = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_START', 6)
        self._pill(sel_cx, sel_cy, pill_w, pill_h, "SELECT", dev.buttons.get(back,0)==1)
        self._pill(start_cx, start_cy, pill_w, pill_h, "START", dev.buttons.get(start,0)==1)

        # Corner shoulders/triggers (horizontal)
        lb = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_LEFTSHOULDER', 9)
        rb = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_RIGHTSHOULDER', 10)
        lt_axis = getattr(sdl2, 'SDL_CONTROLLER_AXIS_TRIGGERLEFT', 4)
        rt_axis = getattr(sdl2, 'SDL_CONTROLLER_AXIS_TRIGGERRIGHT', 5)
        lt_pressed = (dev.axes.get(lt_axis, 0.0) or 0.0) > 0.5
        rt_pressed = (dev.axes.get(rt_axis, 0.0) or 0.0) > 0.5

        corner_w = max(80, int(base * 0.16))
        corner_h = max(18, int(base * 0.05))
        y_top = y0 + pad + corner_h//2 + 6
        # Left top: LB (left)  LT (right)
        lb_cx = pad + corner_w//2 + 8
        lt_cx = lb_cx + corner_w + 10
        self._pill(lb_cx, y_top, corner_w, corner_h, 'L1', dev.buttons.get(lb,0)==1)
        self._pill(lt_cx, y_top, corner_w, corner_h, 'L2', lt_pressed)
        # Right top: RT (left)  RB (right)
        rb_cx = w - pad - corner_w//2 - 8
        rt_cx = rb_cx - corner_w - 10
        self._pill(rt_cx, y_top, corner_w, corner_h, 'R2', rt_pressed)
        self._pill(rb_cx, y_top, corner_w, corner_h, 'R1', dev.buttons.get(rb,0)==1)

        # Sticks and L3/R3 pills
        lx = dev.axes.get(sdl2.SDL_CONTROLLER_AXIS_LEFTX, 0.0)
        ly = dev.axes.get(sdl2.SDL_CONTROLLER_AXIS_LEFTY, 0.0)
        rx = dev.axes.get(sdl2.SDL_CONTROLLER_AXIS_RIGHTX, 0.0)
        ry = dev.axes.get(sdl2.SDL_CONTROLLER_AXIS_RIGHTY, 0.0)
        self._stick(left_cx, left_cy, int(base * 0.156), lx, ly, stick_deadzone)
        self._stick(right_cx, right_cy, int(base * 0.156), rx, ry, stick_deadzone)

        l3_btn = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_LEFTSTICK', 7)
        r3_btn = getattr(sdl2, 'SDL_CONTROLLER_BUTTON_RIGHTSTICK', 8)
        mini_w = int(base * 0.12 * 1.6)
        mini_h = max(12, int(base * 0.04 * 1.1))
        self._pill(left_cx, left_cy + int(base * 0.156) + 18, mini_w, mini_h, 'L3', dev.buttons.get(l3_btn,0)==1)
        self._pill(right_cx, right_cy + int(base * 0.156) + 18, mini_w, mini_h, 'R3', dev.buttons.get(r3_btn,0)==1)
