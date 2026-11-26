---
name: prediction-tracker
description: "Use when the user wants to log model predictions and grade them as games finish, for any sport, in plain wording: 'track my predictions', 'log tonight's probabilities', 'how's the model doing so far', 'is it still any good', 'is accuracy slipping', 'am I beating the close', 'grade last week's picks', 'keep a record of what the model said'. Use this whenever predictions are saved before games and scored after. Load it for short fragments and follow-ups too, instead of answering from memory or going straight to the raw tools. Logs probability, outcome, Brier score, log loss, calibration and closing-line comparison with sample sizes and intervals. Not for placing or sizing wagers (never done), tests on past seasons (see backtesting), fixing calibration (see probability-calibration) or retraining (see model-building)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Prediction Tracker

The honesty loop for a model: record what it predicted before the event, grade it after, and report how good it is with the uncertainty attached. This tracks predictions, not wagers. It has no money columns of any kind.

## Rules for numbers

- Call your sport's SportsDataHQ MCP tools for outcomes and market prices. Do not fill results from memory.
- Cite the tool call behind each outcome and each closing price.
- State sample size and the season convention for every metric.
- If there are too few resolved predictions, say "not enough data" instead of calling the model good or bad.

## Data

| Need | Tool |
|------|------|
| Final results (hockey `get_games`, football `get_games`, basketball `list_games`, soccer `list_games`, tennis `get_matches`, golf `get_leaderboard`, UFC `get_event`) | the sport's results tool |
| Closing fair probability across books | `get_game_probabilities` (or `get_odds` and the margin removal in `odds-market-analysis`) |
| Open to close movement | `get_line_movement` |

Logging and metrics use a local CSV or SQLite file. There is no hosted prediction log; do not invent tools such as `log_prediction` or `get_clv`.

## Storage schema

CSV for under 200 rows, SQLite beyond that.

```
date,event_id,sport,market,outcome,model_prob,model_version,open_fair_prob,close_fair_prob,result,brier,log_loss,notes
```

- `model_prob`: probability for the stated outcome, 0 to 1, recorded before the event
- `model_version`: so results are not mixed across retrains
- `open_fair_prob`, `close_fair_prob`: market fair probability for the same outcome (margin removed)
- `result`: 1 if the outcome happened, 0 if not, blank while open
- `brier`: (model_prob - result)^2; `log_loss`: -ln(p) if result is 1, -ln(1-p) if 0

## How it works

### Step 1: Log at prediction time
Write the row with result blank before the event starts. Logging afterwards biases the record.

### Step 2: Resolve
Pull outcomes with the sport's results tool, match by event id or teams and date, and fill `result`, `brier`, `log_loss`. Push or void events are excluded and counted separately.

### Step 3: Closing-line comparison
After close, fill `close_fair_prob` from `get_game_probabilities` (or compute it). Compute the market's own Brier score and log loss for the same events.

```python
skill = market_brier - model_brier     # positive: model scored better than the closing market
moved_toward = abs(close - model_prob) < abs(open - model_prob)
```
Report the share of events where the market moved toward the model between open and close. Both are measures of model quality. Matching the closing market is a good result.

### Step 4: Running metrics
```python
import numpy as np
n = len(resolved)
brier = resolved.brier.mean()
logloss = resolved.log_loss.mean()
accuracy = ((resolved.model_prob > 0.5) == resolved.result.astype(bool)).mean()
```
Add a calibration table: bin `model_prob` (for example 0.1 wide), show mean predicted, observed frequency and count per bin (see `probability-calibration`). Report a bootstrap or normal interval for Brier and log loss. Break results out per season and per model_version.

### Step 5: Drift check
Compute rolling 50-event Brier and the closing market's rolling Brier. Flag drift when the model's rolling Brier is worse than its own full-history Brier by more than the interval, or worse than the market's for 3 consecutive windows. A flag means audit the data and features (`backtesting`, `probability-calibration`), not that something must be done to any wager.

### Step 6: How much data is enough
For a Brier difference between model and market, report the paired difference with its interval. If the interval includes zero, say the data cannot tell them apart yet. As a guide, expect to need several hundred events to separate small differences, and report the actual interval rather than the guide. Do not call the model good from fewer than about 100 resolved events.

## Anti-patterns

| Rationalization | Why it is wrong | Do this instead |
|-----------------|-----------------|-----------------|
| "I'll log them later" | Memory favors the hits | Log before the event |
| "Accuracy is 58%, so it works" | Accuracy ignores probabilities and sample size | Report Brier, log loss, n and interval |
| "It backtested well" | Backtests overfit | Live record and closing-line comparison come first |
| "Mixing versions is fine" | It hides drift | Keep `model_version` and report per version |
| "Drop the bad week" | Selective reporting | Report all resolved events |

## Output format

```
PREDICTION TRACKER: updated [date]   (season convention: [..])
Predictions: N total | open X | resolved Y
Brier: 0.xxx (95% interval 0.xxx to 0.xxx)   Market closing Brier: 0.xxx
Log loss: 0.xxx   Accuracy: xx.x% (n = Y)
Model moved-toward-by-close share: xx% (n = Y)
By season: [table]   By model_version: [table]
Calibration: [bin table]
Status: [IN LINE WITH MARKET / BEHIND MARKET / NOT ENOUGH DATA]
```

## What to do next

| Finding | Skill |
|---------|-------|
| Behind market for several windows | `backtesting` |
| Calibration bins off | `probability-calibration` |
| Need to retrain | `model-building` |
| Want a chart of rolling Brier or calibration | `visualization` |
| Compare with the market's probability | `market-vs-model` |
