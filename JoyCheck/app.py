#!/usr/bin/env python3
import sys
from pathlib import Path

EXLIBS = Path(__file__).parent / "exlibs"
if EXLIBS.exists():
    sys.path.insert(0, str(EXLIBS))

import time
import sdl2
import sdl2.ext

from config import WIDTH, HEIGHT, BG_COLOR, FPS, FULLSCREEN, STICK_DEADZONE, TRIGGER_DEADZONE, AXIS_EVENT_STEP
from input_device import DeviceManager
from ui import UIRenderer, EventLog
from ui_header import HeaderRenderer
from ui_footer import FooterRenderer
from ui_body import BodyRenderer


def sdl_init():
    flags = (sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER |
             sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC | sdl2.SDL_INIT_EVENTS)
    if sdl2.SDL_Init(flags) != 0:
        raise RuntimeError(sdl2.SDL_GetError().decode())


def main():
    sdl_init()
    try:
        dm = sdl2.SDL_DisplayMode()
        sdl2.SDL_GetCurrentDisplayMode(0, dm)
        win_w = dm.w if FULLSCREEN else WIDTH
        win_h = dm.h if FULLSCREEN else HEIGHT

        flags = sdl2.SDL_WINDOW_SHOWN
        if FULLSCREEN:
            flags |= sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP

        window = sdl2.SDL_CreateWindow(b"JoyCheck",
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            win_w, win_h, flags)
        if not window:
            raise RuntimeError(sdl2.SDL_GetError().decode())

        renderer = sdl2.SDL_CreateRenderer(window, -1,
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
        if not renderer:
            raise RuntimeError(sdl2.SDL_GetError().decode())

        devmgr = DeviceManager()
        devmgr.initial_scan()

        log = EventLog(max_lines=200)
        ui = UIRenderer(renderer, devmgr, log)
        header = HeaderRenderer(ui)
        footer = FooterRenderer(ui)
        body = BodyRenderer(ui)

        stick_dz = float(STICK_DEADZONE)
        trig_dz = float(TRIGGER_DEADZONE)
        fps_avg = 0.0
        last_frame = time.time()
        fn_key = False
        show_log = False
        running = True
        clock_per_frame_ms = int(1000 / FPS)
        event = sdl2.SDL_Event()
        last_title_update = 0.0

        while running:
            while sdl2.SDL_PollEvent(event):
                etype = event.type
                if etype == sdl2.SDL_QUIT:
                    running = False
                    break
                elif etype == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key in (sdl2.SDLK_ESCAPE, sdl2.SDLK_q):
                        running = False
                        break
                    elif key == sdl2.SDLK_c:
                        log.clear()
                    elif key == sdl2.SDLK_l:
                        show_log = not show_log
                    elif key == sdl2.SDLK_LEFTBRACKET:   # [ decrease stick deadzone
                        stick_dz = max(0.0, round(stick_dz - 0.01, 3))
                    elif key == sdl2.SDLK_RIGHTBRACKET:  # ] increase stick deadzone
                        stick_dz = min(1.0, round(stick_dz + 0.01, 3))
                    elif key == sdl2.SDLK_SEMICOLON:     # ; decrease trigger deadzone
                        trig_dz = max(0.0, round(trig_dz - 0.01, 3))
                    elif key == sdl2.SDLK_QUOTE:         # ' increase trigger deadzone
                        trig_dz = min(1.0, round(trig_dz + 0.01, 3))
                    elif key == sdl2.SDLK_F1:            # FN fallback
                        fn_key = True
                elif etype == sdl2.SDL_KEYUP:
                    if event.key.keysym.sym == sdl2.SDLK_F1:
                        fn_key = False
                        show_log = False
                elif etype == sdl2.SDL_CONTROLLERDEVICEADDED:
                    devmgr.add_by_index(event.cdevice.which)
                elif etype == sdl2.SDL_CONTROLLERDEVICEREMOVED:
                    devmgr.remove_by_instance_id(event.cdevice.which)

            # Update devices state
            devmgr.update_states()

            # Mandatory exit: BACK + START within ~200 ms
            if devmgr.check_combo_exit(window_ms=200):
                running = False

            # Collect axis diff events for logging
            try:
                diffs = list(devmgr.diff_events(axis_step=AXIS_EVENT_STEP))
            except TypeError:
                # Backward compatibility if diff_events() had no parameter
                diffs = list(devmgr.diff_events())
            for msg in diffs:
                log.add(msg)

            # Render
            cur_w = sdl2.Sint32()
            cur_h = sdl2.Sint32()
            sdl2.SDL_GetWindowSize(window, cur_w, cur_h)
            vw, vh = int(cur_w.value), int(cur_h.value)

            sdl2.SDL_SetRenderDrawBlendMode(renderer, sdl2.SDL_BLENDMODE_BLEND)
            sdl2.SDL_SetRenderDrawColor(renderer, *BG_COLOR)
            sdl2.SDL_RenderClear(renderer)

            now = time.time()
            dt = max(1e-6, now - last_frame)
            inst_fps = 1.0 / dt
            fps_avg = inst_fps if fps_avg == 0.0 else fps_avg * 0.9 + inst_fps * 0.1
            last_frame = now

            stats = {'fps': round(fps_avg, 1),
                     'stick_dz': stick_dz,
                     'trig_dz': trig_dz,
                     'devices': len(devmgr.devices)}

            header_h = int(vh * 0.10)
            footer_h = int(vh * 0.10)

            header.draw(vw, header_h, stats)
            body.draw(vw, vh, header_h, footer_h,
                      stick_deadzone=stick_dz,
                      trigger_deadzone=trig_dz,
                      show_log=show_log)
            footer.draw(vw, vh, footer_h)

            sdl2.SDL_RenderPresent(renderer)

            if time.time() - last_title_update > 1.0:
                sdl2.SDL_SetWindowTitle(window, f"JoyCheck • devices={len(devmgr.devices)}".encode())
                last_title_update = time.time()

            sdl2.SDL_Delay(clock_per_frame_ms)

    finally:
        sdl2.SDL_Quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal: {e}")
        sys.exit(1)
