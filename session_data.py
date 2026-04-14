import fastf1

# Load the session
session = fastf1.get_session(2026, 1, 'R')
session.load()  # This fetches all the data

# --- Session Info ---
print(f"Session Name -> {session.name}")          # 'Qualifying'
print(session.date)          # Session date
print(session.event)         # Event/race weekend info

# --- Laps Data ---
laps = session.laps           # All laps as a DataFrame
print(laps.head())

# --- Driver Results ---
results = session.results     # Final classification/results
print(results[['DriverNumber', 'Abbreviation', 'TeamName', 'Q1', 'Q2', 'Q3']])

# --- Specific Driver Laps ---
hamilton_laps = session.laps.pick_driver('HAM')
fastest_lap = hamilton_laps.pick_fastest()
print(fastest_lap['LapTime'])

# --- Telemetry for a lap ---
telemetry = fastest_lap.get_telemetry()
#print(telemetry[['Time', 'Speed', 'Throttle', 'Brake', 'RPM', 'Gear']])

# --- Weather Data ---
weather = session.weather_data
print(weather.head())
