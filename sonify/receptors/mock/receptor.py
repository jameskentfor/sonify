import json
import random
import time


class MockGenerator:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            config = json.load(f)

        self.signals = config["signals"]
        self._state = {
            sid: random.uniform(cfg["min"], cfg["max"])
            for sid, cfg in self.signals.items()
        }

    def read(self) -> list[dict]:
        ts = time.time()
        result = []

        for sid, cfg in self.signals.items():
            lo, hi = cfg["min"], cfg["max"]
            step = (hi - lo) * 0.05
            self._state[sid] = max(lo, min(hi, self._state[sid] + random.uniform(-step, step)))
            result.append({"id": sid, "value": self._state[sid], "ts": ts})

        return result
