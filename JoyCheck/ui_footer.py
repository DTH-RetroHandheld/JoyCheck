import sdl2
from config import PAD
from ui import UIRenderer

class FooterRenderer:
    def __init__(self, ui: UIRenderer):
        self.ui = ui

    def draw(self, width: int, height: int, footer_h: int):
        """Render footer area. Uses UIRenderer primitives and font."""
        self.ui._fill_rect(sdl2.SDL_Rect(0, height - footer_h, width, footer_h), (32, 35, 38, 255))
        self.ui._draw_rect(sdl2.SDL_Rect(0, height - footer_h, width, footer_h), (90, 95, 100, 255))

        ft = "DuongTH - HungDuongWP@gmail.com"
        fw, fh = self.ui.font.text_size(ft)
        self.ui.font.draw_text(ft, PAD, height - footer_h + max(0, (footer_h - fh)//2))
