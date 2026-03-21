import fastf1
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.layout import Layout
from rich.rule import Rule
import time

console = Console()

# ─── Load Session ────────────────────────────────────────────────────────────
race = fastf1.get_session(2026,2,'R')
with Progress(
    SpinnerColumn(),
    TextColumn(f"[bold red]Loading F1 Data for {race.event['EventName']} {race.event['Country']} {race.event['Location']}"),
    transient=True,
) as progress:
    progress.add_task("load", total=None)
    race = fastf1.get_session(2026, 2, 'R')
    race.load(telemetry=True, laps=True, weather=True)

console.print(Rule("[bold red]FORMULA 1 — 2026 CHINESE GRAND PRIX[/]"))
console.print()

# ─── Winner Banner ───────────────────────────────────────────────────────────
winner = race.results.iloc[0]
winner_text = Text(justify="center")
winner_text.append("  RACE WINNER\n", style="bold yellow")
winner_text.append(f"  {winner['BroadcastName']}  ", style="bold white on red")
winner_text.append(f"\n  {winner['Time']}", style="dim")
console.print(Panel(winner_text, border_style="yellow", padding=(1, 4)))
console.print()

# ─── Results Table ───────────────────────────────────────────────────────────
results_table = Table(
    title="[bold white] Race Classification[/]",
    box=box.ROUNDED,
    border_style="red",
    header_style="bold yellow",
    show_lines=False,
)

results_table.add_column("Pos", justify="center", style="bold white", width=4)
results_table.add_column("Driver", style="bold cyan", width=18)
results_table.add_column("Team", style="dim white", width=20)
results_table.add_column("Laps", justify="center", width=6)
results_table.add_column("Time / Gap", justify="right", width=20)
results_table.add_column("Status", justify="center", width=14)
results_table.add_column("Pts", justify="center", style="bold yellow", width=5)

STATUS_STYLE = {
    "Finished": "green",
    "Lapped": "yellow",
    "Retired": "red",
    "Did not start": "dim red",
}

MEDAL = {1: "1", 2: "2", 3: "3"}

for _, row in race.results.iterrows():
    pos = int(row['Position']) if not pd.isna(row['Position']) else "-"
    medal = MEDAL.get(pos, str(pos))
    status = row['Status']
    status_style = STATUS_STYLE.get(status, "white")

    if pos == 1:
        time_str = str(row['Time']).split("days ")[-1] if pd.notna(row['Time']) else "-"
    elif pd.notna(row['Time']):
        time_str = "+" + str(row['Time']).split("days ")[-1]
    else:
        time_str = "-"

    results_table.add_row(
        str(medal),
        row['BroadcastName'],
        row.get('TeamName', '-'),
        str(int(row['Laps'])) if not pd.isna(row['Laps']) else "-",
        time_str,
        f"[{status_style}]{status}[/]",
        str(int(row['Points'])) if row['Points'] > 0 else "-",
    )

console.print(results_table)
console.print()

# ─── Points Bar Chart (Terminal) ─────────────────────────────────────────────
console.print(Rule("[bold yellow] Points Scored — Top Drivers[/]"))
console.print()

scorers = race.results[race.results['Points'] > 0].copy()
max_pts = scorers['Points'].max()
BAR_WIDTH = 40

TEAM_COLORS = {
    "Mercedes": "cyan",
    "Ferrari": "red",
    "Red Bull Racing": "blue",
    "McLaren": "yellow",
    "Haas F1 Team": "white",
    "Alpine": "bright_blue",
    "Williams": "bright_cyan",
    "Aston Martin": "green",
    "Sauber": "green",
    "Racing Bulls": "bright_white",
}

for _, row in scorers.iterrows():
    pts = int(row['Points'])
    bar_len = int((pts / max_pts) * BAR_WIDTH)
    team = row.get('TeamName', '')
    color = TEAM_COLORS.get(team, "white")
    bar = "█" * bar_len
    label = f"{row['Abbreviation']:<4} {pts:>2}pts"
    console.print(f"  {label}  [bold {color}]{bar}[/]")

console.print()

# ─── Fastest Laps per Driver (Spark-style) ───────────────────────────────────
console.print(Rule("[bold yellow] Fastest Lap per Driver[/]"))
console.print()

fl_table = Table(box=box.SIMPLE, header_style="bold yellow", show_edge=False)
fl_table.add_column("Driver", style="cyan", width=6)
fl_table.add_column("Fastest Lap", width=16)
fl_table.add_column("Lap #", justify="center", width=6)
fl_table.add_column("Visual", width=45)

driver_best = []
for drv in race.results['Abbreviation']:
    try:
        laps = race.laps.pick_drivers(drv).pick_quicklaps()
        if laps.empty:
            continue
        best = laps.pick_fastest()
        lt = best['LapTime'].total_seconds()
        driver_best.append((drv, lt, int(best['LapNumber'])))
    except Exception:
        continue

if driver_best:
    min_t = min(x[1] for x in driver_best)
    max_t = max(x[1] for x in driver_best)
    driver_best.sort(key=lambda x: x[1])

    for drv, lt, lap_no in driver_best:
        mins = int(lt // 60)
        secs = lt % 60
        time_str = f"{mins}:{secs:06.3f}"
        norm = (lt - min_t) / (max_t - min_t) if max_t != min_t else 0
        bar_len = int((1 - norm) * 38) + 2
        color = "green" if norm < 0.15 else ("yellow" if norm < 0.5 else "red")
        bar = f"[{color}]{'||' * bar_len}[/]"
        fl_table.add_row(drv, time_str, str(lap_no), bar)

console.print(fl_table)
console.print()

# ─── Weather Summary ─────────────────────────────────────────────────────────
try:
    weather = race.weather_data
    avg_air = weather['AirTemp'].mean()
    avg_track = weather['TrackTemp'].mean()
    avg_humidity = weather['Humidity'].mean()
    rainfall = weather['Rainfall'].any()

    weather_items = [
        Panel(f"[bold yellow]{avg_air:.1f}°C[/]\n[dim]Avg Air Temp[/]", border_style="blue"),
        Panel(f"[bold red]{avg_track:.1f}°C[/]\n[dim]Avg Track Temp[/]", border_style="red"),
        Panel(f"[bold cyan]{avg_humidity:.1f}%[/]\n[dim]Avg Humidity[/]", border_style="cyan"),
        Panel(f"[bold {'red' if rainfall else 'green'}]{' Yes' if rainfall else ' No'}[/]\n[dim]Rainfall[/]", border_style="white"),
    ]
    console.print(Rule("[bold yellow] Weather Summary[/]"))
    console.print(Columns(weather_items, equal=True, expand=True))
    console.print()
except Exception:
    pass

# ─── Retirements ─────────────────────────────────────────────────────────────
dnf = race.results[race.results['Status'].isin(['Retired', 'Did not start'])]
if not dnf.empty:
    console.print(Rule("[bold red]  Retirements & DNS[/]"))
    console.print()
    dnf_table = Table(box=box.SIMPLE, show_edge=False, header_style="bold red")
    dnf_table.add_column("Driver", style="cyan")
    dnf_table.add_column("Team", style="dim")
    dnf_table.add_column("Status", style="red")
    dnf_table.add_column("Laps Completed", justify="center")
    for _, row in dnf.iterrows():
        dnf_table.add_row(
            row['BroadcastName'],
            row.get('TeamName', '-'),
            row['Status'],
            str(int(row['Laps'])) if not pd.isna(row['Laps']) else "0"
        )
    console.print(dnf_table)
    console.print()

console.print(Rule("[dim]Data via FastF1 v3.8.1 — 2026 Australian Grand Prix[/]"))
