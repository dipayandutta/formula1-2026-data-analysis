from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ── Your FastAPI base URL ──────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"


def fetch(endpoint, year=2026, round_number=1):
    """Helper — calls the FastAPI and returns JSON, or None on error."""
    try:
        r = requests.get(f"{API_BASE}{endpoint}", params={"year": year, "round_number": round_number}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"API error [{endpoint}]: {e}")
        return None


@app.route("/")
def index():
    year        = int(request.args.get("year", 2026))
    round_num   = int(request.args.get("round_number", 1))

    info        = fetch("/race/info",        year, round_num)
    winner      = fetch("/race/winner",      year, round_num)
    results     = fetch("/race/results",     year, round_num)
    points      = fetch("/race/points",      year, round_num)
    fastest     = fetch("/race/fastest-laps",year, round_num)
    weather     = fetch("/race/weather",     year, round_num)
    #retirements = fetch("/race/retirements", year, round_num)

    return render_template(
        "index.html",
        info=info,
        winner=winner,
        results=results,
        points=points,
        fastest=fastest,
        weather=weather,
      #  retirements=retirements,
        year=year,
        round_num=round_num,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)

