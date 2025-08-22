import sdl2
from config import PAD
from ui import UIRenderer

class HeaderRenderer:
    def __init__(self, ui: UIRenderer):
        self.ui = ui

    def draw(self, width: int, header_h: int, stats: dict):
        """Render header area. Uses UIRenderer primitives and font."""
        self.ui._fill_rect(sdl2.SDL_Rect(0, 0, width, header_h), (32, 35, 38, 255))
        self.ui._draw_rect(sdl2.SDL_Rect(0, 0, width, header_h), (90, 95, 100, 255))

        devices = int((stats or {}).get('devices', 0) or 0)
        fps = (stats or {}).get('fps', 0)
        stick_dz = float((stats or {}).get('stick_dz', 0.0) or 0.0)
        trig_dz = float((stats or {}).get('trig_dz', 0.0) or 0.0)

        hdr = f"JoyCheck  DEVS:{devices}  FPS:{fps}  DZ STICK:{stick_dz:.2f}  DZ TRIG:{trig_dz:.2f}"
        _w, th = self.ui.font.text_size(hdr)
        self.ui.font.draw_text(hdr, PAD, max(0, (header_h - th)//2))
