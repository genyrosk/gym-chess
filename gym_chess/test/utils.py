import inspect
import sys


def run_test_funcs(namespace):
    test_funcs = [
        obj
        for name, obj in inspect.getmembers(sys.modules[namespace])
        if (inspect.isfunction(obj) and name.startswith("test_"))
    ]
    for func in test_funcs:
        func()
