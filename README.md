#  Formula 1 Data Analysis

A Python project for exploring and visualizing Formula 1 race data using [FastF1](https://docs.fastf1.dev/) and [Rich](https://rich.readthedocs.io/). Includes a beautiful terminal dashboard with live race results, lap analysis, telemetry, tyre strategy, and weather data.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastF1](https://img.shields.io/badge/FastF1-3.8.1-red)
![Rich](https://img.shields.io/badge/Rich-Terminal%20UI-green)
![License](https://img.shields.io/badge/License-MIT-yellow)


---

##  Features

- **Race Dashboard** — Full race classification with positions, gaps, status, and points
- **Terminal Bar Charts** — Points and fastest lap visualizations, no matplotlib needed
- **Lap Analysis** — Sector times, lap progression, and personal best laps per driver
- **Telemetry** — Speed, throttle, brake, DRS, RPM, and gear data per lap
- **Tyre Strategy** — Compound usage, tyre life, and stint breakdowns
- **Weather Summary** — Air/track temperature, humidity, rainfall panels
- **Race Control** — Safety car periods, flags, and penalty messages
- **Pure Terminal UI** — Powered by `rich`, works in any terminal

---

##  Installation

```bash
git clone https://github.com/your-username/formula1-2026.git
cd formula1-2026

pip install fastf1 rich pandas
```

---

##  Usage

### Race Dashboard
```bash
python f1_australia_2026.py
```

### Load Any Session
```python
import fastf1

# Format: get_session(year, round_number, session_type)
# Session types: 'R' = Race, 'Q' = Qualifying, 'FP1'/'FP2'/'FP3' = Practice

session = fastf1.get_session(2026, 1, 'R')   # Australian GP Race
session = fastf1.get_session(2026, 1, 'Q')   # Australian GP Qualifying
session.load()
```

---

##  Data Available

| Source | What You Get |
|---|---|
| `session.results` | Final standings, grid positions, points, Q1/Q2/Q3 times |
| `session.laps` | Lap times, sector times, speed traps, position per lap |
| `session.laps.pick_fastest().get_telemetry()` | Speed, RPM, throttle, brake, DRS, gear (~50ms intervals) |
| `session.weather_data` | Air/track temp, humidity, wind speed, rainfall |
| `session.car_data['driver_no']` | Raw car sensor data per driver |
| `session.pos_data['driver_no']` | GPS X/Y/Z coordinates per driver |
| `session.race_control_messages` | Safety car, VSC, flags, penalties |

### Key Lap Filters
```python
laps = session.laps

laps.pick_drivers('HAM')                        # Single driver
laps.pick_drivers(['HAM', 'VER', 'LEC'])        # Multiple drivers
laps.pick_fastest()                             # Overall fastest lap
laps.pick_quicklaps()                           # Clean laps only
laps[laps['Compound'] == 'SOFT']                # Filter by tyre compound
laps[laps['IsPersonalBest'] == True]            # Personal best laps only
```

### Key Telemetry Columns
```python
tel = lap.get_telemetry()
# Distance, Speed, RPM, nGear, Throttle, Brake, DRS, X, Y, Z
```

---

##  Project Structure

```
formula1-2026/
├── f1_australia_2026.py   # Rich terminal dashboard for AUS GP
├── session_data.py        # Session data exploration & basics
└── README.md
```

---

## Roadmap

- [ ] Per-driver full analysis dashboard
- [ ] Lap time progression chart (terminal sparklines)
- [ ] Head-to-head driver comparison
- [ ] Tyre strategy timeline visualization
- [ ] Track map using GPS position data (X/Y)
- [ ] Season standings tracker across all rounds
- [ ] Export results to CSV / HTML report

---

##  Resources

- [FastF1 Documentation](https://docs.fastf1.dev/)
- [FastF1 GitHub](https://github.com/theOehrly/Fast-F1)
- [Rich Documentation](https://rich.readthedocs.io/)
- [F1 Official Timing](https://www.formula1.com/en/timing/f1-live)

---

## Data Availability

FastF1 pulls data from the official F1 timing API. Session data is typically available **1–3 days** after the event. Use FastF1's built-in caching to avoid repeated API calls:

```python
import fastf1
fastf1.Cache.enable_cache('./cache')   # Optional: specify custom cache directory
```

---

##  License

MIT License — feel free to use, modify, and share.

---

> Built with FastF1 + Rich — because F1 data deserves a podium finish in your terminal.
