"""
APK Compiler - Native Windows Drag and Drop Handler.
Provides 64-bit safe, crash-proof OLE/Win32 WM_DROPFILES integration for Tkinter/CustomTkinter.
Safely extracts dropped file/folder paths and schedules callbacks on the Tkinter mainloop.
"""

import os
import sys
import ctypes
from ctypes import wintypes
from typing import Callable, List, Optional


class WinDropHandler:
    """
    Subclasses the Windows Win32 window procedure to capture WM_DROPFILES messages.
    Fully 64-bit safe with proper pointer types and asynchronous mainloop dispatch.
    """

    def __init__(self, tk_window, on_drop_callback: Callable[[List[str]], None]):
        self.tk_window = tk_window
        self.on_drop_callback = on_drop_callback
        self.hwnd = None
        self.old_proc = None
        self._c_proc_ref = None
        self._is_hooked = False

        if sys.platform == "win32":
            # Wait until window HWND is realized
            self.tk_window.after(150, self._setup_hook)

    def _setup_hook(self):
        if self._is_hooked:
            return

        try:
            user32 = ctypes.windll.user32
            shell32 = ctypes.windll.shell32

            LONG_PTR = ctypes.c_ssize_t
            LRESULT = ctypes.c_ssize_t
            HWND = wintypes.HWND
            UINT = wintypes.UINT
            WPARAM = wintypes.WPARAM
            LPARAM = wintypes.LPARAM

            self.WNDPROC = ctypes.WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)

            if ctypes.sizeof(ctypes.c_void_p) == 8:
                GetWindowLongPtr = user32.GetWindowLongPtrW
                GetWindowLongPtr.argtypes = [HWND, ctypes.c_int]
                GetWindowLongPtr.restype = LONG_PTR

                SetWindowLongPtr = user32.SetWindowLongPtrW
                SetWindowLongPtr.argtypes = [HWND, ctypes.c_int, LONG_PTR]
                SetWindowLongPtr.restype = LONG_PTR
            else:
                GetWindowLongPtr = user32.GetWindowLongW
                GetWindowLongPtr.argtypes = [HWND, ctypes.c_int]
                GetWindowLongPtr.restype = LONG_PTR

                SetWindowLongPtr = user32.SetWindowLongW
                SetWindowLongPtr.argtypes = [HWND, ctypes.c_int, LONG_PTR]
                SetWindowLongPtr.restype = LONG_PTR

            CallWindowProc = user32.CallWindowProcW
            CallWindowProc.argtypes = [LONG_PTR, HWND, UINT, WPARAM, LPARAM]
            CallWindowProc.restype = LRESULT

            shell32.DragAcceptFiles.argtypes = [HWND, wintypes.BOOL]
            shell32.DragAcceptFiles.restype = None

            shell32.DragQueryFileW.argtypes = [WPARAM, UINT, wintypes.LPWSTR, UINT]
            shell32.DragQueryFileW.restype = UINT

            shell32.DragFinish.argtypes = [WPARAM]
            shell32.DragFinish.restype = None

            self.hwnd = self.tk_window.winfo_id()
            if not self.hwnd:
                return

            self.old_proc = GetWindowLongPtr(self.hwnd, -4)  # GWL_WNDPROC = -4
            if not self.old_proc:
                return

            WM_DROPFILES = 0x0233
            WM_DESTROY = 0x0002

            def _wndproc_handler(hwnd, msg, wp, lp):
                if msg == WM_DROPFILES:
                    try:
                        hdrop = wp
                        file_count = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
                        dropped_paths = []
                        buf = ctypes.create_unicode_buffer(1024)

                        for idx in range(file_count):
                            length = shell32.DragQueryFileW(hdrop, idx, buf, 1024)
                            if length > 0 and buf.value:
                                dropped_paths.append(os.path.normpath(buf.value.strip()))

                        shell32.DragFinish(hdrop)

                        # Safely dispatch onto Tkinter main thread
                        if dropped_paths and self.on_drop_callback:
                            self.tk_window.after(20, lambda paths=dropped_paths: self._safe_dispatch(paths))
                    except Exception as err:
                        sys.stderr.write(f"Drop handling error: {err}\n")
                    return 0

                elif msg == WM_DESTROY and self.old_proc:
                    SetWindowLongPtr(self.hwnd, -4, self.old_proc)

                return CallWindowProc(self.old_proc, hwnd, msg, wp, lp)

            # Store persistent reference to prevent garbage collection
            self._c_proc_ref = self.WNDPROC(_wndproc_handler)
            proc_address = ctypes.cast(self._c_proc_ref, ctypes.c_void_p).value
            SetWindowLongPtr(self.hwnd, -4, proc_address)

            shell32.DragAcceptFiles(self.hwnd, True)
            self._is_hooked = True
        except Exception as e:
            sys.stderr.write(f"Failed to hook drag and drop: {e}\n")

    def _safe_dispatch(self, paths: List[str]):
        """Run callback safely inside Tkinter event loop."""
        try:
            if self.on_drop_callback:
                self.on_drop_callback(paths)
        except Exception as e:
            sys.stderr.write(f"Exception during drop callback dispatch: {e}\n")

    def unhook(self):
        """Restore original window procedure."""
        if self._is_hooked and self.hwnd and self.old_proc:
            try:
                user32 = ctypes.windll.user32
                if ctypes.sizeof(ctypes.c_void_p) == 8:
                    user32.SetWindowLongPtrW(self.hwnd, -4, self.old_proc)
                else:
                    user32.SetWindowLongW(self.hwnd, -4, self.old_proc)
                self._is_hooked = False
            except Exception:
                pass

