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
Calling Main Function
'''
if __name__ == "__main__":
    uvicorn.run("f1_api:app",host="0.0.0.0",port=8000,reload=True)
