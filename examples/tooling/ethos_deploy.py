#!/usr/bin/env python3
"""Deploy an Ethos Lua script to a radio over USB, or to a simulator folder.

A small, dependency-light version of the deploy tooling used by large
open-source Ethos Lua projects:

  * finds the radio over USB HID (the same interface Ethos Suite uses)
  * switches it to USB storage mode if it is in serial-debug mode
  * finds the radio's drive by its *.cpuid marker file
  * mirror-copies only changed files (size, then MD5), deleting stale ones
  * optionally switches to serial-debug mode and prints the radio's
    Lua print() output until Ctrl+C, then switches back to storage

Usage:
  python ethos_deploy.py --src src/mywidget --radio
  python ethos_deploy.py --src src/mywidget --radio --debug
  python ethos_deploy.py --src src/mywidget --sim simulators/X20S_FCC/scripts
  python ethos_deploy.py --radio --debug-only          # just tail print() output
  python ethos_deploy.py --radio --debug-only --for 30 # ... for 30 seconds
  python ethos_deploy.py --radio --info                # board id via HID

Requires: Python 3.9+, `pip install hidapi pyserial` (radio only).
Docs: https://frskyrc.github.io/ethos-lua-doc/tools/vscode/
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import string
import sys
import time
from pathlib import Path

VID = 0x0483
PIDS = (0x5750, 0x5740)          # 0x5740 seen on some firmware during re-enumeration
INFO_REQUEST = 0x21              # -> response 0x22, byte[2] = board id
USB_MODE_REQUEST = 0x81
USB_MODE_SERIAL = 0x68           # interface 1 becomes a CDC serial port (print output)
USB_MODE_STORAGE = 0x69          # interface 1 becomes USB mass storage
MARKERS = ("sdcard.cpuid", "radio.cpuid", "flash.cpuid")


# ----------------------------------------------------------------- HID
def hid_open():
    try:
        import hid
    except ImportError:
        sys.exit("radio access needs hidapi: python -m pip install hidapi")
    for pid in PIDS:
        try:
            if hasattr(hid, "device"):           # 'hidapi' package
                dev = hid.device()
                dev.open(VID, pid)
            else:                                # older 'hid' package
                dev = hid.Device(vid=VID, pid=pid)
            return dev
        except Exception:
            continue
    sys.exit("no Ethos radio found over USB HID (is it connected and switched on?)")


def hid_send(payload: bytes) -> None:
    dev = hid_open()
    try:
        dev.write(bytes([0x00]) + payload)       # leading 0x00 = report id
    finally:
        dev.close()


def board_info() -> int | None:
    dev = hid_open()
    try:
        dev.write(bytes([0x00, INFO_REQUEST, 6]))
        r = dev.read(256, 500)
        return r[2] if r and r[0] == INFO_REQUEST + 1 else None
    finally:
        dev.close()


# ----------------------------------------------------------------- drive discovery
def candidate_roots():
    system = platform.system()
    if system == "Windows":
        for letter in string.ascii_uppercase:
            yield Path(f"{letter}:/")
    elif system == "Darwin":
        yield from Path("/Volumes").glob("*")
    else:
        user = os.environ.get("USER", "")
        for base in (Path("/media") / user, Path("/run/media") / user, Path("/mnt")):
            if base.is_dir():
                yield from base.glob("*")


def find_radio_drive() -> Path | None:
    for root in candidate_roots():
        try:
            if any((root / m).exists() for m in MARKERS):
                return root
        except OSError:
            continue
    return None


def serial_port():
    try:
        from serial.tools import list_ports
    except ImportError:
        return None
    for p in list_ports.comports():
        if p.vid == VID and p.pid in PIDS:
            return p.device
    return None


def ensure_storage(timeout=60) -> Path:
    drive = find_radio_drive()
    if drive:
        return drive
    print("[radio] drive not mounted, requesting USB storage mode ...")
    hid_send(bytes([USB_MODE_REQUEST, USB_MODE_STORAGE]))
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        time.sleep(1)
        drive = find_radio_drive()
        if drive:
            print(f"[radio] mounted at {drive} after {time.monotonic() - start:.0f}s")
            return drive
    sys.exit(f"radio drive did not mount within {timeout}s")


# ----------------------------------------------------------------- copy
def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def needs_copy(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    if src.stat().st_size != dst.stat().st_size:
        return True
    return md5(src) != md5(dst)


def mirror(src: Path, dst: Path, dry_run=False) -> tuple[int, int]:
    """rsync-style: copy changed files, delete files that no longer exist in src."""
    copied = removed = 0
    changed: set[Path] = set()
    src_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    for rel in sorted(src_files):
        s, d = src / rel, dst / rel
        if needs_copy(s, d):
            print(f"  + {rel.as_posix()}")
            copied += 1
            changed.add(rel)
            if not dry_run:
                d.parent.mkdir(parents=True, exist_ok=True)
                with open(s, "rb") as fi, open(d, "wb") as fo:
                    fo.write(fi.read())
                    fo.flush()
                    os.fsync(fo.fileno())    # removable storage: make sure it really landed
    if dst.exists():
        for p in sorted(dst.rglob("*"), reverse=True):
            rel = p.relative_to(dst)
            if p.is_file() and rel not in src_files and p.suffix != ".luac":
                print(f"  - {rel.as_posix()}")
                removed += 1
                if not dry_run:
                    p.unlink()
            elif p.is_file() and p.suffix == ".luac" and rel.with_suffix(".lua") in changed:
                # stale bytecode would shadow the new source; Ethos recompiles on load
                print(f"  - {rel.as_posix()} (stale bytecode)")
                removed += 1
                if not dry_run:
                    p.unlink()
    return copied, removed


# ----------------------------------------------------------------- serial debug
def tail_debug(seconds: float | None = None):
    try:
        import serial
    except ImportError:
        sys.exit("serial debug needs pyserial: python -m pip install pyserial")
    print("[radio] switching to serial debug mode (the drive will unmount) ...")
    hid_send(bytes([USB_MODE_REQUEST, USB_MODE_SERIAL]))
    port = None
    for _ in range(30):
        time.sleep(1)
        port = serial_port()
        if port:
            break
    if not port:
        sys.exit("debug serial port did not appear")
    print(f"[radio] {port}: printing Lua output, Ctrl+C to stop")
    end = time.monotonic() + seconds if seconds else None
    try:
        with serial.Serial(port, 115200, timeout=0.5) as s:
            while end is None or time.monotonic() < end:
                line = s.readline()
                if line:
                    print(line.decode("utf-8", errors="replace").rstrip())
    except KeyboardInterrupt:
        pass
    finally:
        print("\n[radio] back to USB storage mode")
        hid_send(bytes([USB_MODE_REQUEST, USB_MODE_STORAGE]))


# ----------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, help="script folder to deploy (its name becomes scripts/<name>)")
    ap.add_argument("--name", help="folder name on the radio (default: name of --src)")
    target = ap.add_mutually_exclusive_group(required=True)
    target.add_argument("--radio", action="store_true", help="deploy to a USB-connected radio")
    target.add_argument("--sim", type=Path, help="deploy into this simulator scripts/ folder")
    ap.add_argument("--debug", action="store_true", help="after deploying, tail the radio's print() output")
    ap.add_argument("--debug-only", action="store_true", help="only tail print() output, no copy")
    ap.add_argument("--for", dest="seconds", type=float, help="stop tailing after this many seconds")
    ap.add_argument("--info", action="store_true", help="print the radio's board id and exit")
    ap.add_argument("--dry-run", action="store_true", help="show what would change, copy nothing")
    args = ap.parse_args()

    if args.info:
        print(f"board id: {board_info()}")
        return 0
    if args.debug_only:
        tail_debug(args.seconds)
        return 0
    if not args.src or not args.src.is_dir():
        ap.error("--src must be an existing folder")

    name = args.name or args.src.name
    if args.radio:
        scripts = ensure_storage() / "scripts"
    else:
        scripts = args.sim
    dest = scripts / name
    print(f"[deploy] {args.src} -> {dest}{' (dry run)' if args.dry_run else ''}")
    t0 = time.monotonic()
    copied, removed = mirror(args.src, dest, args.dry_run)
    print(f"[deploy] {copied} copied, {removed} removed in {time.monotonic() - t0:.1f}s")
    if args.radio and args.debug and not args.dry_run:
        tail_debug(args.seconds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
