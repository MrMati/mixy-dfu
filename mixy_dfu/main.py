import time
import argparse
import shutil
import sys
import os
import struct

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("pyserial is required. Install with: pip install pyserial")
    sys.exit(1)


ERR = "\033[91m"  # Bright Red
SCS = "\033[92m"  # Bright Green
WRN = "\033[93m"  # Bright Yellow
# INFO = "\033[94m" # Bright Blue
INFO = "\033[0m"  # No color
RESET = "\033[0m"


def is_uf2(buf):
    UF2_MAGIC_START0 = 0x0A324655
    UF2_MAGIC_START1 = 0x9E5D5157
    w = struct.unpack("<II", buf[0:8])
    return w[0] == UF2_MAGIC_START0 and w[1] == UF2_MAGIC_START1


def find_device(vid: int, pid: int) -> str | None:
    for port in serial.tools.list_ports.comports():
        if port.vid == vid and port.pid == pid:
            return port.device
    return None


def dfu_reset(device) -> bool:
    try:
        serial.Serial(device, baudrate=1200).open()
    except serial.SerialException:
        # funny I know
        print(f"{SCS}✅ Device reset successfully{RESET}")
        return True

    print(f"{WRN}⚠️  Device might not have been reset{RESET}")
    return False


def flash_uf2_windows(uf2_path: str, verbose: bool) -> bool:
    import win32api
    import win32file

    end_time = time.time() + 5

    while time.time() < end_time:
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split("\000")[:-1]

        for d in drives:
            try:
                type_ = win32file.GetDriveType(d)
                if type_ == win32file.DRIVE_REMOVABLE:
                    if not os.path.exists(
                        os.path.join(d, "INFO_UF2.TXT")
                    ):  # TODO: check Board-ID
                        continue

                    print(
                        f"{SCS}⚙️ UF2 bootloader found ({d}). Flashing... {RESET}")
                    try:
                        shutil.copyfile(uf2_path, os.path.join(d, uf2_path))
                    except Exception as e:
                        print(f"{ERR}❓ UF2 flashing failed{RESET}")
                        if verbose:
                            print("Error:", e)
                        return False
                    print(f"{SCS}✅ Firmware flashed successfully{RESET}")
                    return True
            except Exception:
                continue
        time.sleep(0.5)

    print(f"{WRN}❌ UF2 bootloader not found on Windows{RESET}")
    return False


def flash_uf2_linux(uf2_path: str, verbose: bool) -> bool:
    end_time = time.time() + 5

    while time.time() < end_time:
        with open("/proc/mounts", "r") as f:
            mounts = [line.split()[1] for line in f.readlines()]

        for mount_point in mounts:
            # TODO: check Board-ID
            info_file = os.path.join(mount_point, "INFO_UF2.TXT")
            if os.path.exists(info_file):
                print(
                    f"{SCS}⚙️ UF2 bootloader found ({mount_point}). Flashing... {RESET}")
                try:
                    shutil.copyfile(uf2_path, os.path.join(
                        mount_point, uf2_path))
                    print(f"{SCS}✅ Firmware flashed successfully{RESET}")
                    return True
                except Exception as e:
                    print(f"{ERR}❓ UF2 flashing failed{RESET}")
                    if verbose:
                        print("Error:", e)
                    return False

        time.sleep(0.5)

    print(f"{WRN}⚠️ UF2 bootloader not found among mounted drives{RESET}")
    print("💡 If you have auto-mounting disabled, don't mount manually.")
    print(
        f"💡 Just write directly with:  sudo dd if={uf2_path} of=/dev/sdX bs=1M conv=fsync")
    return False


def flash_uf2(uf2_path: str, verbose=False) -> bool:
    funcs = {
        "linux": flash_uf2_linux,
        "win32": flash_uf2_windows,
    }

    if sys.platform in funcs:
        print(f"{INFO}⌛ Waiting for UF2 bootloader...{RESET}")
        return funcs[sys.platform](uf2_path, verbose)

    print(f"{ERR}❌ UF2 flashing is not supported on this platform{RESET}")
    return False


def main():
    parser = argparse.ArgumentParser(description="DFU reset tool")
    parser.add_argument("--vid", type=lambda x: int(x, 0),
                        default=0x2FE3, help="USB VID (hex or int)")
    parser.add_argument("--pid", type=lambda x: int(x, 0),
                        default=0x1337, help="USB PID (hex or int)")
    parser.add_argument("--firmware", type=str,
                        help="Path to UF2 file to flash after reset")
    parser.add_argument("--nowait", action="store_true",
                        help="Do not wait for device if not found")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    try:
        if args.firmware:
            try:
                with open(args.firmware, "rb") as f:
                    if not is_uf2(f.read(8)):
                        print(f"{ERR}❌ Invalid UF2 file{RESET}")
                        return
            except OSError:
                print(f"{ERR}❌ Cannot access UF2 file{RESET}")
                return

        if dev := find_device(args.vid, args.pid):
            print(f"{INFO}🔍 Found Mixy reset interface: {dev}{RESET}")
            dfu_reset(dev)  # ignore reset error
            if args.firmware:
                flash_uf2(args.firmware, args.verbose)
            return
        elif args.nowait:
            print(f"{WRN}❌ No compatible device found{RESET}")
            return

        print(f"{INFO}⌛ Waiting for device...{RESET}")
        while True:
            if dev := find_device(args.vid, args.pid):
                print(f"{INFO}🔍 Mixy reset interface connected: {dev}{RESET}")
                dfu_reset(dev)  # ignore reset error
                if args.firmware:
                    flash_uf2(args.firmware, args.verbose)
                return
            time.sleep(0.5)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
