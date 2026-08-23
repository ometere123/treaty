"""Shared pytest fixtures are provided by genlayer-test's direct-mode plugin.

The current upstream direct loader unlinks its temporary stdin file before
restoring file descriptor 0. Windows refuses that unlink while the descriptor
is still open; Linux does not. Keep the compatibility workaround in the test
harness so it cannot affect deployed contract code.
"""

import atexit
import os
import sys


_WINDOWS_TEMP_FILES: set[str] = set()


def _cleanup_windows_temp_files() -> None:
    for path in list(_WINDOWS_TEMP_FILES):
        try:
            os.unlink(path)
        except (FileNotFoundError, PermissionError, OSError):
            pass


def pytest_sessionstart(session):
    if sys.platform != "win32":
        return

    import gltest.direct.loader as loader

    original = loader._inject_message_to_fd0

    def inject_with_windows_cleanup(vm):
        real_unlink = os.unlink

        def tolerant_unlink(path, *args, **kwargs):
            try:
                return real_unlink(path, *args, **kwargs)
            except PermissionError:
                _WINDOWS_TEMP_FILES.add(str(path))
                return None

        os.unlink = tolerant_unlink
        try:
            original(vm)
        finally:
            os.unlink = real_unlink

    loader._inject_message_to_fd0 = inject_with_windows_cleanup
    atexit.register(_cleanup_windows_temp_files)


def pytest_runtest_teardown(item, nextitem):
    _cleanup_windows_temp_files()
