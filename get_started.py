import fastf1
import pandas as pd

race = fastf1.get_session(2026,1,'R')
race.load()

####----SESSION INFORMATION----####
print("SESSION INFORMATION")
print(f"Event       : {race.event['EventName']}")
print(f"Country     : {race.event['Country']}")
print(f"Location    : {race.event['Location']}")
print(f"Session     : {race.name}")
print(f"Date        : {race.date}")
print(f"Round       : {race.event.RoundNumber}")


#####----RESULT----####
print("\n RESULT COLUMS ")
print(race.results.columns.tolist())

####---- RESULT FOR TODAYS WINNER G.RUSSEL ----####
print(race.results[race.results['Abbreviation'] == 'RUS'])

####----LAP DATA----####
print("\n LAP DATA")
print(race.laps.columns.tolist())

####----G.RUSSEL LAP DATA----####
rus_laps = race.laps.pick_drivers('RUS')
print(rus_laps[['LapNumber', 'LapTime', 'Compound', 'TyreLife', 'Position']].head(10))


####---GET TELEMETRY DATA----#
fastest_lap = race.laps.pick_drivers('RUS').pick_fastest()
tel = fastest_lap.get_telemetry()
print("TELEMETRY COLUMNS")
print("------------------------")
# ['Date', 'Time', 'SessionTime',
#  'Speed',      ← km/h
#  'RPM',
#  'nGear',      ← gear number
#  'Throttle',   ← 0 to 100
#  'Brake',      ← True/False
#  'DRS',        ← 0/8/10/12/14 (inactive/active)
#  'Source',
#  'Distance',         ← meters from lap start
#  'RelativeDistance', ← 0.0 to 1.0
#  'Status', 'X', 'Y', 'Z']  ← GPS coordinates

print(tel.columns.tolist())

print(tel[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear', 'DRS']].head(10))


####----GET TYRE DATA----#
print("\n TYRE DATA")
print(rus_laps[['LapNumber', 'Compound', 'TyreLife', 'FreshTyre', 'Stint']].to_string())


####---GET WEATHER DATA----#
print("\n=== WEATHER COLUMNS ===")
print(race.weather_data.columns.tolist())
# ['Time', 'AirTemp', 'Humidity', 'Pressure',
#  'Rainfall', 'TrackTemp', 'WindDirection', 'WindSpeed']
print(race.weather_data.head(5))


####---- CAR DATA ----#####
print("\n=== CAR DATA ===")
car = race.car_data['63']   # by driver number
print(car.columns.tolist())
# ['Date', 'Time', 'Speed', 'RPM', 'nGear', 'Throttle', 'Brake', 'DRS', 'Source']
print(car.head(5))


##### ----- GET GPS DATA ---- #####
print("\n=== POSITION DATA ===")
pos = race.pos_data['63']   # by driver number
print(pos.columns.tolist())
# ['Date', 'Time', 'X', 'Y', 'Z', 'Status', 'Source']
print(pos.head(5))

####----- RACE CONTROLLER MESSAGE ---- ####
print("\n=== RACE CONTROL MESSAGES ===")
print(race.race_control_messages.columns.tolist())
# ['Time', 'Utc', 'Lap', 'Category', 'Message',
#  'Flag', 'Scope', 'Sector', 'RacingNumber']
print(race.race_control_messages[['Lap', 'Category', 'Message']].head(10))
# Safety car, VSC, flags, penalties etc.



###### ----- ALL DRIVER LIST ---- ####

print("####----------ALL DRIVER LIST--------#####")
drivers = race.results['Abbreviation'].tolist()
print("Drivers :",drivers)
