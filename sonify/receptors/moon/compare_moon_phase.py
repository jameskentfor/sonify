from datetime import datetime, timezone
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
from moon_phase import get_phase

now = datetime.now(timezone.utc)

# Skyfield (authoritative)
ts = load.timescale()
t = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
eph = load('de421.bsp')
sun, moon, earth = eph['sun'], eph['moon'], eph['earth']
e = earth.at(t)
_, slon, _ = e.observe(sun).apparent().frame_latlon(ecliptic_frame)
_, mlon, _ = e.observe(moon).apparent().frame_latlon(ecliptic_frame)
skyfield_phase = (mlon.degrees - slon.degrees) % 360.0

# Fast approximation
fast_phase = get_phase("UTC")

diff = abs(skyfield_phase - fast_phase)
diff = min(diff, 360.0 - diff)

print(f"Skyfield:    {skyfield_phase:.4f}°")
print(f"Fast approx: {fast_phase:.4f}°")
print(f"Difference:  {diff:.4f}°")
