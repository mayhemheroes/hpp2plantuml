#!/usr/bin/env python3
from re import error

import atheris
import sys
import io
from contextlib import contextmanager

from CppHeaderParser import CppParseError

import fuzz_helpers

with atheris.instrument_imports():
    import hpp2plantuml

ctr = 0
@contextmanager
def nostdout():
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stdout = io.BytesIO()
    sys.stderr = io.BytesIO()
    yield
    sys.stdout = save_stdout
    sys.stderr = save_stderr
def TestOneInput(data):
    global ctr
    ctr += 1
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        if fdp.ConsumeBool():
            with nostdout():
                with fdp.ConsumeTemporaryFile(suffix='.hpp', all_data=True, as_bytes=True) as f:
                    hpp2plantuml.CreatePlantUMLFile(file_list=[f], output_file='/dev/null')
        else:
            with nostdout():
                obj_d = hpp2plantuml.Diagram(flag_dep=fdp.ConsumeBool())
                obj_d.create_from_string(fdp.ConsumeRemainingString())
    except (CppParseError, UnicodeDecodeError, error):
        return -1
    except (TypeError, AssertionError):
        if ctr > 1000:
            raise
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
