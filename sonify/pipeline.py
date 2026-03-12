import argparse
import json
import time

from receptors.mock.receptor import MockGenerator
from receptors.moon.receptor import MoonReceptor
from normalizer.normalizer import Normalizer
from mapper.mapper import Mapper
from controller.osc.controller import OscController

RECEPTORS = {
    "mock": MockGenerator,
    "moon": MoonReceptor,
}


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Print signals as they are sent")
    args = parser.parse_args()

    with open("pipeline_config.json") as f:
        config = json.load(f)

    tick_interval = 1 / config["tick_rate"]

    receptor_config = config["receptor"]
    receptor = RECEPTORS[receptor_config["type"]](**receptor_config.get("args", {}))
    normalizer = Normalizer(config["normalizer"]["config_path"])
    mapper = Mapper(config["mapper"]["config_path"])
    controller = OscController(config["controller"]["config_path"])

    print("[Pipeline] Starting...")

    try:
        while True:
            for signal in receptor.read():
                normalized = normalizer.process(signal)
                if normalized is None:
                    continue

                mapped = mapper.process(normalized)
                if mapped is None:
                    continue

                controller.send(mapped)
                if args.verbose:
                    print(f"[{mapped['id']}] {mapped['value']}")

            time.sleep(tick_interval)

    except KeyboardInterrupt:
        print("[Pipeline] Stopped.")


if __name__ == "__main__":
    run()
