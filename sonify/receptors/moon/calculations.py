import math
from datetime import datetime
from zoneinfo import ZoneInfo

JULIAN_MONTH_OFFSET = 14
JULIAN_YEAR_OFFSET = 4800
JULIAN_MONTH_MULTIPLIER = 153
JULIAN_DAY_CONSTANT = 32045
HOURS_PER_DAY = 24
MINUTES_PER_DAY = 1440
SECONDS_PER_DAY = 86400
NOON_OFFSET = 12
DEGREES_PER_CYCLE = 360.0
JULIAN_CENTURIES_PER_DAY = 36525.0
J2000 = 2451545.0

# Sun mean longitude and anomaly coefficients (Meeus Ch. 25)
SUN_MEAN_LON_C0 = 280.46646
SUN_MEAN_LON_C1 = 36000.76983
SUN_MEAN_ANOMALY_C0 = 357.52911
SUN_MEAN_ANOMALY_C1 = 35999.05029
SUN_MEAN_ANOMALY_C2 = 0.0001537

# Sun equation of center coefficients
SUN_CENTER_C1_0 = 1.914602
SUN_CENTER_C1_1 = 0.004817
SUN_CENTER_C1_2 = 0.000014
SUN_CENTER_C2_0 = 0.019993
SUN_CENTER_C2_1 = 0.000101
SUN_CENTER_C3 = 0.000289

# Moon mean longitude, anomaly, elongation, argument of latitude (Meeus Ch. 47)
MOON_MEAN_LON_C0 = 218.3164477
MOON_MEAN_LON_C1 = 481267.88123421
MOON_MEAN_ANOMALY_C0 = 134.9633964
MOON_MEAN_ANOMALY_C1 = 477198.8675055
MOON_ELONGATION_C0 = 297.8501921
MOON_ELONGATION_C1 = 445267.1114034
MOON_ARG_LAT_C0 = 93.2720950
MOON_ARG_LAT_C1 = 483202.0175233

# Perturbation term denominator (units: 0.000001 degrees → degrees)
PERTURBATION_SCALE = 1e6


def _julian_date(dt: datetime) -> float:
    a = (JULIAN_MONTH_OFFSET - dt.month) // 12
    y = dt.year + JULIAN_YEAR_OFFSET - a
    m = dt.month + 12 * a - 3
    jd = dt.day + (JULIAN_MONTH_MULTIPLIER * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - JULIAN_DAY_CONSTANT
    jd += (dt.hour - NOON_OFFSET) / HOURS_PER_DAY + dt.minute / MINUTES_PER_DAY + dt.second / SECONDS_PER_DAY
    return jd


def get_phase(timezone: str) -> float:
    dt = datetime.now(ZoneInfo(timezone))
    jd = _julian_date(dt)
    T = (jd - J2000) / JULIAN_CENTURIES_PER_DAY

    # Sun's ecliptic longitude
    L0 = SUN_MEAN_LON_C0 + SUN_MEAN_LON_C1 * T
    M_sun = math.radians(SUN_MEAN_ANOMALY_C0 + SUN_MEAN_ANOMALY_C1 * T - SUN_MEAN_ANOMALY_C2 * T**2)
    C_sun = ((SUN_CENTER_C1_0 - SUN_CENTER_C1_1 * T - SUN_CENTER_C1_2 * T**2) * math.sin(M_sun)
             + (SUN_CENTER_C2_0 - SUN_CENTER_C2_1 * T) * math.sin(2 * M_sun)
             + SUN_CENTER_C3 * math.sin(3 * M_sun))
    sun_lon = (L0 + C_sun) % DEGREES_PER_CYCLE

    # Moon's ecliptic longitude
    L_moon = (MOON_MEAN_LON_C0 + MOON_MEAN_LON_C1 * T) % DEGREES_PER_CYCLE
    M_moon = math.radians((MOON_MEAN_ANOMALY_C0 + MOON_MEAN_ANOMALY_C1 * T) % DEGREES_PER_CYCLE)
    D = math.radians((MOON_ELONGATION_C0 + MOON_ELONGATION_C1 * T) % DEGREES_PER_CYCLE)
    F = math.radians((MOON_ARG_LAT_C0 + MOON_ARG_LAT_C1 * T) % DEGREES_PER_CYCLE)

    # Main perturbation terms from Meeus Table 47.A
    dL = (6288774 * math.sin(M_moon)
          + 1274027 * math.sin(2*D - M_moon)
          + 658314  * math.sin(2*D)
          + 213618  * math.sin(2*M_moon)
          - 185116  * math.sin(M_sun)
          - 114332  * math.sin(2*F)
          + 58793   * math.sin(2*D - 2*M_moon)
          + 57066   * math.sin(2*D - M_sun - M_moon)
          + 53322   * math.sin(2*D + M_moon)
          + 45758   * math.sin(2*D - M_sun)
          - 40923   * math.sin(M_sun - M_moon)
          - 34720   * math.sin(D)
          - 30383   * math.sin(M_sun + M_moon)
          + 15327   * math.sin(2*D - 2*F)
          - 12528   * math.sin(M_moon + 2*F)
          + 10980   * math.sin(M_moon - 2*F)
          + 10675   * math.sin(4*D - M_moon)
          + 10034   * math.sin(3*M_moon)
          + 8548    * math.sin(4*D - 2*M_moon)
          - 7888    * math.sin(2*D + M_sun - M_moon)
          - 6766    * math.sin(2*D + M_sun)
          - 5163    * math.sin(D - M_moon)) / PERTURBATION_SCALE

    moon_lon = (L_moon + dL) % DEGREES_PER_CYCLE

    return (moon_lon - sun_lon) % DEGREES_PER_CYCLE


def get_illumination(phase_deg: float) -> float:
    phase_rad = math.radians(phase_deg)
    return (1 - math.cos(phase_rad)) / 2 * 100
