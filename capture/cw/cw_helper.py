import os
import subprocess
import sys
import time
import warnings

import chipwhisperer as cw

cwpath = None
firmwarepath = None

scope = None
target = None
platform = None


def search_common_paths_for_cw():
    project_root = os.path.join(os.path.dirname(__file__), "../..")
    global cwpath
    global firmwarepath
    cwpath = None
    firmwarepath = None
    for cwpath in list(
        os.path.join(project_root, p)
        for p in (
            "..",
            "../..",
            "../chipwhisperer",
            "../../chipwhisperer",
            "../../../chipwhisperer",
        )
    ) + [r"C:\cw\cw\home\portable\chipwhisperer"]:
        firmwarepath = os.path.abspath(os.path.join(cwpath, "hardware/victims/firmware"))
        if os.path.exists(firmwarepath):
            break

    if not os.path.exists(firmwarepath):
        raise ValueError("FIRMWAREPATH not found")

    if "win" in sys.platform:
        os.environ["PATH"] += ";" + ";".join(
            (
                r"C:\cw\cw\usr\bin",
                r"C:\cw\cw\home\portable\armgcc\gcc-arm-none-eabi-10-2020-q4-major\bin",
                r"C:\cw\cw\home\portable\avrgcc\avr-gcc-10.1.0-x64-windows\bin",
            )
        )


search_common_paths_for_cw()


def init_scope_and_target(platform_="CWLITEXMEGA"):
    global scope
    global target
    global platform
    if scope is None:
        platform = platform_
        scope = cw.scope()
        target = cw.target(scope, target_type=cw.targets.SimpleSerial2)
    scope.default_setup()
    return scope, target


def exit_scope_and_target():
    global scope
    global target
    if scope is not None:
        target.dis()
        scope.dis()
        cw.util.DisableNewAttr._read_only_attrs.clear()
        target = None
        scope = None


def compile(path, cryptooptions=None):
    cryptooptions = cryptooptions or ["CRYPTO_TARGET=NONE"]
    try:
        proc = subprocess.run(
            [
                "make",
                "-f",
                f'{os.path.join(os.path.dirname(__file__), "cw_helper_makefile")}',
                f"PLATFORM={platform}",
                f"FIRMWAREPATH={firmwarepath}",
                f"TARGET={os.path.splitext(os.path.basename(path))[0]}",
                "clean",
                "allquick",
            ]
            + cryptooptions,
            cwd=os.path.dirname(path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        # print("\x1b[32m✓\x1b[0m " + proc.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f'\x1b[31m✗ "{" ".join(e.args[1])}" returned:\x1b[0m\n' + e.stderr.decode())
        raise


def flash(path):
    if platform == "CWLITEXMEGA":
        prog = cw.programmers.XMEGAProgrammer
    elif platform == "CWLITEARM" or "STM" in platform:
        prog = cw.programmers.STM32FProgrammer
    cw.program_target(
        scope=scope,
        prog_type=prog,
        fw_path=os.path.join(
            os.path.dirname(path),
            f"{os.path.splitext(os.path.basename(path))[0]}-{platform}.hex",
        ),
    )


def compile_and_flash(path, cryptooptions=None):
    compile(path, cryptooptions)
    flash(path)
    print("\x1b[32m✓\x1b[0m")


def reset_target():
    scope.io.nrst = "low"
    time.sleep(0.05)
    target.flush()
    scope.io.nrst = "high_z"
    time.sleep(0.05)


def capture():
    ret = scope.capture()

    for i in range(101):
        if target.is_done():
            break
        time.sleep(0.05)
        if i == 100:
            warnings.warn("Target did not finish operation")
            return None
    if ret:
        warnings.warn("Timeout happened during capture")
        return None

    return scope.get_last_trace()
