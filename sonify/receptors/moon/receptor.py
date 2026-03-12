import time

from receptors.moon.calculations import get_illumination, get_phase


class MoonReceptor:
    def __init__(self, timezone: str = "UTC"):
        self.timezone = timezone

    def read(self) -> list[dict]:
        ts = time.time()
        phase = get_phase(self.timezone)
        illumination = get_illumination(phase)
        return [
            {"id": "moon_phase", "value": phase, "ts": ts},
            {"id": "moon_illumination", "value": illumination, "ts": ts},
        ]
