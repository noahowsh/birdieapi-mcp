---
name: data-pipeline
description: "Use when the user wants to automate a sports model: run predictions every morning, set up a cron job or GitHub Action, store predictions in a database, version models, retrain on a schedule or get alerted when accuracy drifts. Covers pulls through any sport's SportsDataHQ MCP server. Not for one-off lookups (use your sport's lookup skill or nl-to-query), not for building the model (use model-building), not for historical testing (use backtesting), not for grading logged predictions (use prediction-tracker)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Data Pipeline

You are an expert in sports analytics automation. The goal is to move from "I built a model" to "my model runs every morning and its results are logged." Odds are information only: the pipeline stores market probabilities next to model probabilities for comparison and does not produce wagering instructions.

## Rules for numbers

- Call the SportsDataHQ MCP tools for every figure; never fill a gap from memory.
- Store the tool name and arguments with each pull so any stored number can be traced to the call that produced it.
- Record sample size and the season convention (calendar year, year the season starts, or year it ends) in every report the pipeline writes.
- If a pull fails or a window has too few games, the report says "not enough data". It does not impute silently.
- Check the cost of a large backfill with the user before running it.

## Data

Call your sport's SportsDataHQ MCP tools. Examples: hockey get_schedule and get_games, football get_games and get_plays, basketball list_games and get_shot_chart, baseball get_games and get_pitches, soccer list_games and get_events, tennis get_matches and get_match, golf get_leaderboard, UFC get_event and get_fight, cricket get_deliveries. Market inputs come from get_odds, get_game_probabilities or get_line_movement where the server offers them.

The MCP server is pull-only (no streaming) and has no scheduler. Automate by running Claude headlessly on a schedule:

```
claude -p "Pull today's games with the SportsDataHQ tools and save JSON to data/games/"
```

Own data: skip the tools and read files directly.

## Initial assessment

1. Output: predictions only, or predictions plus a report?
2. Cadence: daily, before each game window, or event-driven?
3. Storage: SQLite (local), Postgres, Sheets or Notion?
4. Does the model exist? If not, start with model-building.

## Step 1: pipeline shape

```
[Schedule] -> [Data pull] -> [Prediction] -> [Storage + alert]
   cron        MCP tools     model.predict()   SQLite / Sheets
```

## Step 2: GitHub Actions cron

```yaml
name: Daily pipeline
on:
  schedule:
    - cron: '0 11 * * *'   # 6 AM ET = 11:00 UTC
  workflow_dispatch:
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - name: Pull games and market probabilities
        run: python scripts/pull_data.py --date today
      - name: Generate predictions
        run: python scripts/generate_predictions.py --date today
      - name: Log predictions
        run: python scripts/log_predictions.py --date today
      - name: Drift check
        run: python scripts/drift_check.py --window 14
      - name: Commit results
        run: |
          git config user.email "pipeline@example.com"
          git config user.name "Pipeline Bot"
          git add data/ predictions/
          git commit -m "Daily pipeline $(date +%F)" || echo "Nothing to commit"
          git push
```

Schedules vary by sport: pick a run time after lineups or starters are usually known (starting goalies, starting pitchers, injury reports, confirmed XIs), and a second refresh closer to game time if the market inputs matter.

## Step 3: save pulls

```python
# scripts/pull_data.py
import json, os
from datetime import date

def save_pull(payload: dict, kind: str, target_date: str, source_call: str):
    """payload is the result Claude got from an MCP tool; source_call records which tool produced it."""
    path = f"data/{kind}/{target_date}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"date": target_date, "pulled_at": date.today().isoformat(),
                   "source_call": source_call, "data": payload}, f, indent=2)
```

## Step 4: generate predictions

```python
# scripts/generate_predictions.py
import json, pickle

def active_version() -> str:
    return json.load(open("models/registry.json"))["active"]

def generate(target_date: str):
    version = active_version()
    model = pickle.load(open(f"models/{version}/model.pkl", "rb"))
    games = json.load(open(f"data/games/{target_date}.json"))["data"]
    out = []
    for g in games:
        x = build_features(g)          # your feature code, shift(1) applied
        p = float(model.predict_proba([x])[0][1])
        out.append({"game_id": g["id"], "date": target_date,
                    "home_win_prob": round(p, 4), "model_version": version})
    json.dump(out, open(f"predictions/{target_date}.json", "w"), indent=2)

def build_features(game):
    raise NotImplementedError("Use feature-engineering output here")
```

## Step 5: tracking schema (SQLite)

```sql
CREATE TABLE IF NOT EXISTS predictions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  game_id TEXT NOT NULL,
  game_date DATE NOT NULL,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  home_win_prob REAL NOT NULL,          /* model probability */
  market_open_prob REAL,                /* market no-margin probability at prediction time */
  market_close_prob REAL,               /* fill later */
  model_version TEXT NOT NULL,
  generated_at TIMESTAMP NOT NULL,
  actual_result INTEGER,                /* 1 home win, 0 away win; fill after game */
  source_call TEXT                      /* tool call that supplied inputs */
);

CREATE TABLE IF NOT EXISTS model_versions (
  version TEXT PRIMARY KEY,
  trained_at DATE NOT NULL,
  training_games INTEGER NOT NULL,
  val_log_loss REAL NOT NULL,
  val_accuracy REAL NOT NULL,
  feature_set TEXT NOT NULL,
  is_active INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS drift_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  check_date DATE NOT NULL,
  window_days INTEGER NOT NULL,
  games_in_window INTEGER NOT NULL,
  accuracy REAL,
  expected_acc REAL NOT NULL,
  drift_flag INTEGER DEFAULT 0
);
```

Rolling accuracy query:

```sql
SELECT game_date,
  AVG(CASE WHEN actual_result = ROUND(home_win_prob) THEN 1.0 ELSE 0.0 END)
    OVER (ORDER BY game_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS rolling_14
FROM predictions WHERE actual_result IS NOT NULL ORDER BY game_date;
```

## Step 6: model versioning

Never overwrite a model file. Each training run writes a new directory (`models/v2.2.0/model.pkl`) and `models/registry.json` points at the active version with its training date, validation scores and feature list. Roll back by changing the pointer.

## Step 7: retrain triggers

| Condition | Trigger | Action |
|-----------|---------|--------|
| Calendar | Start of each month or season | Retrain on the latest completed seasons |
| Game count | Every 50 new games | Rolling-window retrain |
| Accuracy drop | Window accuracy more than 3 points below validation | Review features first, then retrain |
| New season | Season opens | Full retrain with a carryover check |
| Closing-line check | Model probability stops moving toward the closing probability for 30 days | Model is lagging the market; review features |

Do not retrain on one bad week. Require the trigger to hold on two or three consecutive checks.

## Step 8: drift check

```python
# scripts/drift_check.py
import sqlite3, json, argparse
THRESH = 0.03

def check(window: int = 14):
    conn = sqlite3.connect("predictions.db")
    games, acc = conn.execute("""
      SELECT COUNT(*), AVG(CASE WHEN actual_result = ROUND(home_win_prob) THEN 1.0 ELSE 0.0 END)
      FROM predictions WHERE actual_result IS NOT NULL
        AND game_date >= DATE('now', ?)""", (f"-{window} days",)).fetchone()
    if games < 30:
        print(f"Not enough data: {games} games in {window} days")
        return
    reg = json.load(open("models/registry.json"))
    expected = next(v["val_accuracy"] for v in reg["versions"] if v["version"] == reg["active"])
    flag = acc < expected - THRESH
    conn.execute("INSERT INTO drift_log (check_date, window_days, games_in_window, accuracy, expected_acc, drift_flag) VALUES (DATE('now'),?,?,?,?,?)",
                 (window, games, acc, expected, int(flag)))
    conn.commit()
    print(("DRIFT: " if flag else "OK: ") + f"{acc:.1%} over {games} games (expected {expected:.1%})")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--window", type=int, default=14)
    check(p.parse_args().window)
```

A small window is noisy: the check refuses to flag below 30 games.

## Step 9: multiple sources in one run

Pull results, market probabilities and team or player stats in parallel; if one source fails, continue and mark the missing input in the log rather than hiding it.

```python
results = await asyncio.gather(pull_games(d), pull_market(d), pull_team_stats(d), return_exceptions=True)
games, market, stats = results
if isinstance(market, Exception):
    log_warning("market pull failed; storing model probability only")
    market = {}
```

Cache slow-moving inputs (season stats, ratings) and refresh weekly rather than daily. Backfill history once, store it locally, then pull only new games.

## Anti-patterns

| Claim | Why it fails | Do instead |
|-------|--------------|------------|
| "I will run it by hand each morning" | You will miss days | Schedule it now, even if imperfect |
| "Overwrite the model on retrain" | Cannot audit which model made which prediction | Version every model |
| "One bad week means drift" | Variance | Window of 30+ games and a 3 point drop on repeat checks |
| "Spreadsheet is fine" | Manual entry breaks | SQLite takes minutes to set up |
| "Pull full history daily" | Wasteful | Backfill once, pull new games only |

## What to do next

| Finding | Next | Skill |
|---------|------|-------|
| Pipeline running | Grade the logged predictions over time | `prediction-tracker` |
| Accuracy drifting | Test on recent history | `backtesting` |
| Need better inputs | Rebuild features | `feature-engineering` |
| Need a new model | Retrain | `model-building` |
| Want today's gap to the market | Compare probabilities | `market-vs-model` |
