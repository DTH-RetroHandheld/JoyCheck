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


def sdl_init():
    flags = (sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER |
             sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC | sdl2.SDL_INIT_EVENTS)
    if sdl2.SDL_Init(flags) != 0:
        raise RuntimeError(sdl2.SDL_GetError().decode())


def main():
    sdl_init()
    try:
        # Get current resolution (display 0)
        dm = sdl2.SDL_DisplayMode()
        sdl2.SDL_GetCurrentDisplayMode(0, dm)
        win_w = dm.w if FULLSCREEN else WIDTH
        win_h = dm.h if FULLSCREEN else HEIGHT

        flags = sdl2.SDL_WINDOW_SHOWN
        if FULLSCREEN:
            flags |= sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP

        window = sdl2.SDL_CreateWindow(
            b"JoyCheck",
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            win_w, win_h,
            flags
        )
        if not window:
            raise RuntimeError(sdl2.SDL_GetError().decode())

        renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
        if not renderer:
            raise RuntimeError(sdl2.SDL_GetError().decode())

        devmgr = DeviceManager()
        devmgr.initial_scan()

        log = EventLog(max_lines=200)
        ui = UIRenderer(renderer, devmgr, log)

        # Deadzone runtime
        stick_dz = float(STICK_DEADZONE)
        trig_dz = float(TRIGGER_DEADZONE)
        # FPS moving average
        fps_avg = 0.0
        last_frame = time.time()

        # FN via keyboard (fallback), e.g., device maps FN -> F1
        fn_key = False
        show_log = False

        running = True
        clock_per_frame_ms = int(1000 / FPS)

        event = sdl2.SDL_Event()
        last_title_update = 0.0

        while running:
            # Event pump
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
                    elif key == sdl2.SDLK_c:  # clear log
                        log.clear()
                    elif key == sdl2.SDLK_l:  # toggle log panel
                        show_log = not show_log
                    elif key == sdl2.SDLK_LEFTBRACKET:    # [ decrease stick deadzone
                        stick_dz = max(0.0, round(stick_dz - 0.01, 3))
                    elif key == sdl2.SDLK_RIGHTBRACKET:   # ] increase stick deadzone
                        stick_dz = min(1.0, round(stick_dz + 0.01, 3))
                    elif key == sdl2.SDLK_SEMICOLON:      # ; decrease trigger deadzone
                        trig_dz = max(0.0, round(trig_dz - 0.01, 3))
                    elif key == sdl2.SDLK_QUOTE:          # ' increase trigger deadzone
                        trig_dz = min(1.0, round(trig_dz + 0.01, 3))
                    elif key == sdl2.SDLK_F1:             # FN fallback
                        fn_key = True
                elif etype == sdl2.SDL_KEYUP:
                    if event.key.keysym.sym == sdl2.SDLK_F1:
                        fn_key = False
                        show_log = False
                elif etype == sdl2.SDL_CONTROLLERDEVICEADDED:
                    dev_index = event.cdevice.which
                    devmgr.add_by_index(dev_index)
                elif etype == sdl2.SDL_CONTROLLERDEVICEREMOVED:
                    instance_id = event.cdevice.which
                    devmgr.remove_by_instance_id(instance_id)

            # Update device states
            devmgr.update_states()

            # Exit combo: SELECT+START within 200 ms
            if devmgr.check_combo_exit(window_ms=200):
                running = False

            # Log input diffs
            for msg in devmgr.diff_events(axis_step=AXIS_EVENT_STEP):
                log.add(msg)

            # Viewport size
            from ctypes import c_int
            cur_w, cur_h = c_int(), c_int()
            sdl2.SDL_GetWindowSize(window, cur_w, cur_h)
            vw, vh = cur_w.value, cur_h.value

            # Render
            sdl2.SDL_SetRenderDrawBlendMode(renderer, sdl2.SDL_BLENDMODE_BLEND)
            sdl2.SDL_SetRenderDrawColor(renderer, *BG_COLOR)
            sdl2.SDL_RenderClear(renderer)

            # FPS
            now = time.time()
            dt = max(1e-6, now - last_frame)
            inst_fps = 1.0 / dt
            fps_avg = inst_fps if fps_avg == 0.0 else fps_avg * 0.9 + inst_fps * 0.1
            last_frame = now

            stats = {
                'fps': round(fps_avg, 1),
                'stick_dz': stick_dz,
                'trig_dz': trig_dz,
                'devices': len(devmgr.devices),
                'hint': "SELECT+START = Exit",
            }
            ui.draw(vw, vh, stick_deadzone=stick_dz, trigger_deadzone=trig_dz, stats=stats, fn_key=fn_key, show_log=show_log)

            sdl2.SDL_RenderPresent(renderer)

            # Update window title 1Hz
            now = time.time()
            if now - last_title_update > 1.0:
                title = f"JoyCheck • devices={len(devmgr.devices)}"
                sdl2.SDL_SetWindowTitle(window, title.encode())
                last_title_update = now

            sdl2.SDL_Delay(clock_per_frame_ms)

    finally:
        sdl2.SDL_Quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal: {e}")
        sys.exit(1)
