# Sonify

Modular sonification middleware that translates real-world data into musical control signals. Connects sensors, cameras, astronomical data, and other sources to synthesizers and music software via OSC.

## How it works

Data flows through a four-stage pipeline:

```
Receptor → Normalizer → Mapper → Controller
```

1. **Receptor** — reads raw data from a source (sensor, moon phase, mock generator, etc.) and emits `{id, value, ts}` signals
2. **Normalizer** — scales raw values to a 0–1 range using configured min/max bounds; clamps and warns if a value falls outside the configured range
3. **Mapper** — translates source signal IDs to musical target IDs (e.g. `brightness` → `filter_cutoff`)
4. **Controller** — sends the mapped values as OSC messages to a synthesizer or DAW

## Setup

Requires Python 3 and the packages in `sonify/requirements.txt`:

```bash
pip3 install -r sonify/requirements.txt
```

If using the dev container, this is handled automatically by `.devcontainer/postCreate.sh`.

`liblo-tools` is also installed system-wide via the dev container for OSC debugging.

## Running

From the `sonify/` directory:

```bash
python3 pipeline.py
```

Pass `--verbose` (or `-v`) to print each signal as it is sent:

```bash
python3 pipeline.py -v
```

The pipeline reads `pipeline_config.json` to determine the tick rate, receptor, and config paths for each stage.

**Mock generator** (for testing):
```json
{
  "tick_rate": 30,
  "receptor": {
    "type": "mock",
    "args": { "config_path": "receptors/mock/config.json" }
  },
  "normalizer": { "config_path": "normalizer/normalizer_config.json" },
  "mapper": { "config_path": "mapper/mapper_config.json" },
  "controller": { "config_path": "controller/osc/osc_config.json" }
}
```

**Moon receptor**:
```json
{
  "tick_rate": 30,
  "receptor": {
    "type": "moon",
    "args": { "timezone": "UTC" }
  },
  "normalizer": { "config_path": "normalizer/normalizer_config.json" },
  "mapper": { "config_path": "mapper/mapper_config.json" },
  "controller": { "config_path": "controller/osc/osc_config.json" }
}
```

## Configuration

| File | Purpose |
|------|---------|
| `sonify/pipeline_config.json` | Tick rate, receptor selection, and config paths for each stage |
| `sonify/normalizer/normalizer_config.json` | Min/max bounds per signal ID |
| `sonify/mapper/mapper_config.json` | Source → target ID mappings |
| `sonify/controller/osc/osc_config.json` | OSC host, port, and address prefix |
| `sonify/receptors/mock/config.json` | Mock signal ranges |

## Receptors

| Receptor | Description |
|----------|-------------|
| `mock` | Generates random-walking test signals |
| `moon` | Calculates moon phase and illumination using Meeus astronomical algorithms (Chapters 25 & 47) |

### Moon receptor signals

| Signal ID | Range | Description |
|-----------|-------|-------------|
| `moon_phase` | 0–360° | Ecliptic longitude difference between Moon and Sun |
| `moon_illumination` | 0–100% | Percentage of lunar disk illuminated |

To add a new receptor, implement a class with a `read()` method that returns a list of `{id, value, ts}` dicts, then register it in `pipeline.py`.

## SuperCollider integration

`controller/osc/sonify.scd` is a headless SuperCollider script that listens for OSC messages from the pipeline and drives a simple synth (filtered saw wave with controllable cutoff and pan).

Start SuperCollider before the pipeline. On Linux with PipeWire:

```bash
pw-jack sclang controller/osc/sonify.scd
```

Wait for:
```
Sonify synth running.
OSC responders registered. Listening on port 57120.
```

Then start the pipeline in a second terminal:

```bash
python3 pipeline.py
```

### OSC messages handled by sonify.scd

| Address | Range | Controls |
|---------|-------|----------|
| `/synth/filter_cutoff` | 0.0–1.0 → 200–8000 Hz | Filter cutoff frequency |
| `/synth/pan` | 0.0–1.0 → −1.0 to 1.0 | Stereo pan position |

### Dev container audio (Linux with PipeWire)

The dev container mounts the host's PipeWire and PulseAudio sockets. `pw-jack` routes audio through PipeWire to your host's audio device, so no additional setup is needed beyond rebuilding the container after cloning.

## Debugging OSC output

To inspect raw OSC messages without SuperCollider running:

```bash
oscdump 57120
```

Note: `oscdump` and `sclang` both bind to port 57120, so only run one at a time.

## OSC output

Messages are sent to `localhost:57120` with the prefix `/synth/` by default. For example, a signal mapped to `filter_cutoff` is sent as `/synth/filter_cutoff <value>`.
