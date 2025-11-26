import os
import shutil
from typing import List, Tuple


class TapisClientStub:
    """
    Stub implementation of the Tapis API client.
    Simulates network upload by copying files to a local folder.
    """

    def __init__(self, base_dir: str = "./hpc_storage"):
        self.base_dir = base_dir
        self._failed_once_sessions = set()

    def ensure_base_dir(self) -> None:
        os.makedirs(self.base_dir, exist_ok=True)

    def upload_batch(self, session_key: str, files: List[Tuple[str, int]]) -> str:
        """
        Simulate a resumable batch upload.
        The first call for a session may fail if TAPIS_FAIL_FIRST is set.
        """
        always_fail = os.getenv("TAPIS_ALWAYS_FAIL", "").lower() == "true"
        fail_first = os.getenv("TAPIS_FAIL_FIRST", "").lower() == "true"

        if always_fail:
            raise RuntimeError("Simulated persistent network failure")

        if fail_first and session_key not in self._failed_once_sessions:
            self._failed_once_sessions.add(session_key)
            raise RuntimeError("Simulated transient network failure")

        session_dir = os.path.join(self.base_dir, session_key)
        os.makedirs(session_dir, exist_ok=True)

        for path, _size in files:
            if not os.path.isfile(path):
                continue
            dest = os.path.join(session_dir, os.path.basename(path))
            shutil.copy2(path, dest)

        # Return a fake remote path
        return f"{session_key}/"
