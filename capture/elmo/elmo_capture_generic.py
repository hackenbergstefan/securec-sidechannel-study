#!/usr/bin/env python
import os
import random
import struct
import subprocess
import shutil
import tempfile

import numpy as np
import jinja2

filedir = os.path.abspath(os.path.dirname(__file__))

TEMPLATE = open(os.path.join(filedir, "elmoprogram.j2")).read()

STDERR_TO_NULL = False


def run_elmo(binary="elmo", cwd=None):
    if cwd is not None and cwd != filedir:
        shutil.copy(os.path.join(filedir, binary), cwd)
        shutil.copy(os.path.join(filedir, "coeffs.txt"), cwd)
        shutil.copy(os.path.join(filedir, "_elmoprogram.bin"), cwd)

    subprocess.check_call(
        ["rm", "-rf", "output"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd or filedir,
    )
    subprocess.check_call(
        [f"./{binary}", "_elmoprogram.bin"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd or filedir,
    )


def compile(number_of_traces, input_length, code=None, fromfile=None):
    """Render template with given code and compile using make."""
    template = jinja2.Environment().from_string(TEMPLATE)
    rendered = template.render(
        dict(number_of_traces=number_of_traces, input_length=input_length, code=code, fromfile=fromfile)
    )
    with open(os.path.join(filedir, "_elmoprogram.c"), "w") as fp:
        fp.write(rendered)

    additional_args = dict(stderr=subprocess.DEVNULL) if STDERR_TO_NULL is True else {}
    subprocess.check_call(
        ["make", "clean", "all", "BINARY=_elmoprogram"],
        stdout=subprocess.DEVNULL,
        **additional_args,
        cwd=filedir,
    )


def trace_length(input_length, code=None, fromfile=None, cwd=None):
    """Estimate number of traces generated by elmo by capturing one shot."""
    compile(number_of_traces=16, input_length=input_length, code=code, fromfile=fromfile)

    with open(os.path.join(cwd or filedir, "plaintexts.txt"), "w") as fp:
        fp.write(16 * input_length * "00\n")

    run_elmo(cwd=cwd)

    with open(os.path.join(cwd, f"output/traces/trace00001.trc"), "rb") as fp:
        content = fp.read()
    return len(content) // 8


def capture(
    name,
    number_of_traces,
    inputfunction,
    code=None,
    fromfile=None,
    cleanup=True,
    save=False,
    checkoutput=None,
    tmpdir=True,
    **kwargs,
):
    """Capture traces with elmo."""
    try:
        if tmpdir:
            tempdir = tempfile.TemporaryDirectory()
            cwd = tempdir.__enter__()
        else:
            cwd = filedir

        input_length = len(inputfunction())
        number_of_samples = trace_length(input_length, code, fromfile, cwd=cwd)

        data = np.zeros(
            number_of_traces,
            dtype=[
                ("trace", "f8", number_of_samples),
                ("input", "u1", input_length),
            ],
        )

        compile(number_of_traces=number_of_traces, input_length=input_length, code=code, fromfile=fromfile)
        with open(os.path.join(cwd, "plaintexts.txt"), "w") as fp:
            for i in range(number_of_traces):
                data["input"][i, :] = inputfunction()
                fp.write("".join(f"{x:02x}\n" for x in data["input"][i, :]))

        run_elmo(binary=name.split("_")[0], cwd=cwd)

        for i in range(number_of_traces):
            with open(os.path.join(cwd, f"output/traces/trace{i + 1:05d}.trc"), "rb") as fp:
                content = fp.read()
            data["trace"][i, :] = struct.unpack(f"{len(content) // 8}d", content)

        if checkoutput:
            with open(os.path.join(cwd, "output/printdata.txt")) as fp:
                prints = [int(l, base=16) for l in fp.readlines()]
            output_first = checkoutput(data["input"][0])
            output_last = checkoutput(data["input"][-1])

            if list(output_first) != prints[: len(output_first)]:
                raise Exception(f"{output_first} != {prints[:len(output_first)]}")
            if list(output_last) != prints[-len(output_last) :]:
                raise Exception(f"{output_last} != {prints[-len(output_last):]}")

        shutil.copy(os.path.join(cwd, "output/asmoutput/asmtrace00001.txt"), filedir)

        if cleanup:
            subprocess.check_call(
                ["rm", "-rf", "output"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=cwd,
            )
        if save:
            np.save(os.path.join(filedir, f"../../data/{name}.npy"), data)
    finally:
        if tmpdir is True:
            tempdir.__exit__(None, None, None)

    return data


def main():
    capture(
        "elmo",
        number_of_traces=1_000,
        inputfunction=lambda: [random.randint(0, 255) for _ in range(2)],
        code="""print_buffer(input, 2);""",
        checkoutput=lambda input: input,
        tmpdir=True,
    )
    capture(
        "elmo",
        number_of_traces=1_000,
        inputfunction=lambda: [random.randint(0, 255) for _ in range(32 + 4 + 3 * 32)],
        fromfile="../../examples/sbox/sbox.c",
    )


if __name__ == "__main__":
    main()
