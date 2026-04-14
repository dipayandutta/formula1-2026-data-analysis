import fastf1
import pandas as pd
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

app = FastAPI(
        title = "F1 2026 Rece Data API",
        description="RestAPI Implementation for the F1",
        version="1.0.0"
        )

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        )

_sessions: dict = {}

def _get_race_session(year: int, round_number: int):
    key = (year,round_number)
    if key not in _sessions:
        try:
            session = fastf1.get_session(year,round_number,"R")
            session.load(telemetry=False,laps=True,weather=True)
            _sessions[key] = session 
        except Excetion as e:
            raise HTTPException(status_code=500, detail=f"Failed to load session: {e}")
    return _sessions[key]



'''
Get All Details without clustering
'''
@app.get("/race/details")
def get_details(year: int=2026, round: int=1):
    race = _get_race_session(year,round)

    return race.results 


'''
Get the Race Information 
'''

@app.get("/race/info")
def get_race_info(year: int=2026, round: int=1):
    race = _get_race_session(year,round)
    
    return {

            "event_name": race.event["EventName"],
            "country": race.event["Country"],
            "location": race.event["Location"],
            "year": year,
            "round": round,
            }

'''
race winner
'''
@app.get("/race/winner")
def get_winner(year: int=2026, round: int=1):
    race = _get_race_session(year,round)
    winner = race.results.iloc[0]
    return{
        "driver": winner['BroadcastName'],
        "abbreviation": winner['Abbreviation'],
        "team" : winner.get("TeamName","-"),
        "points": int(winner['Points']),
        "status": winner['Status']

            }

'''
race result 
'''

@app.get("/race/results")
def get_results(year: int=2026, round: int=1):
    race = _get_race_session(year,round)
    results = []

    for _,row in race.results.iterrows():
        pos = int(row["Position"]) if pd.notna(row["Position"]) else None 

        if pos == 1:
            time_str = str(row["Time"]).split("days")[-1] if pd.notna(row["Time"]) else "-"
        elif pd.notna(row["Time"]):
            time_str = "+" + str(row["Time"]).split("days")[-1]
        else:
            time_str = "-"

        results.append({
            "position" : pos,
            "driver": row["BroadcastName"],
            "abbreviation": row["Abbreviation"],
            "team": row.get("TeamName", "-"),
            "laps": int(row["Laps"]) if pd.notna(row["Laps"]) else None,
            "time_gap": time_str,
            "status": row["Status"],
            "points": int(row["Points"]) if row["Points"] > 0 else 0,
            })
    return {"year": year, "round": round, "event": race.event["EventName"], "resutls": results}

'''
Race Points 
'''
@app.get("/race/points")
def get_points(year: int=2026, round: int=1):
    race = _get_race_session(year,round)
    scores = race.results[race.results["Points"] > 0].copy()
    max_pts = int(scores["Points"].max())

    data = []

    for _,row in scores.iterrows():
        data.append({

            "driver": row["BroadcastName"],
            "abbreviation" : row["Abbreviation"],
            "team": row.get("TeamName", "-"),
            "points" : int(row["Points"]),
            })
    return {max_pts: "max_pts", "scores": data}


'''
Fastest Lap 
'''
@app.get("/race/fastestlap")
def get_fastest_lap(year: int=2026 , rounds: int=1):
    race = _get_race_session(year,rounds)
    driver_best = []

    for drv in race.results["Abbreviation"]:
        try:
            laps = race.laps.pick_drivers(drv).pick_quicklaps()
            if laps.empty:
                continue
            best = laps.pick_fastest()
            lap_time = best["LapTime"].total_seconds()
            mins = int(lap_time//60)
            secs = lap_time % 60

            driver_best.append({
                "driver": drv,
                "lap_time": f"{mins}:{secs:06.3f}",
                "lap_time_second": round(lap_time,3),
                "lap_number": int(best["LapNumber"])
                })
        except Exception as e :
            raise e 

    driver_best.sort(key=lambda x:x["lap_time_second"])
    return {"fastest_laps": driver_best}


'''
Get the Weather information during the race 
'''
@app.get("/race/weather")
def get_weather(year: int=2026, round: int=1):
    race = _get_race_session(year,round)

    try:
        weather = race.weather_data
        return{
                "rainfall": bool(weather["Rainfall"].any())
#                "avg_air_temp_c": round(float(weather["AirTemp"].mean()),1),
#                 "avg_track_temp_c": round(float(weather["TrackTemp"].mean()),1),
#                "avg_humidity_pct": round(float(weather["Humidity"].mean()),1),
#                 "rainfall": bool(weather["Rainfall"].any()),
                }
    except Exception as e :
        raise HTTPException(status_code=500, detail=f"Weather Data unavailable {e}")

'''
Drivers that not able start the race or retired 
'''

@app.get("/race/retirements")
def get_retirements(year: int=2026, round: int=1):
    race = _get_race_session(year,round)
    drivers = race.results[race.results["status"].isin(["Retired", "Did not start"])]

    data = []

    for _, row in drivers.iterrows():
        data.append({
            "driver": row["BroadcastName"],
            "abbreviation": row["Abbreviation"],
            "team": row.get("TeamName", "-"),
            "status": row["status"],
            "laps_completed": int(row["Laps"]) if pd.notna(row["Laps"]) else 0,
            })
    return {"retirements": data}

'''
Calling Main Function
'''
if __name__ == "__main__":
    uvicorn.run("f1_api:app",host="0.0.0.0",port=8000,reload=True)
