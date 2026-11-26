---
name: backtesting
description: "Use when the user asks whether a sports model or system would have worked in the past, for any sport, in plain wording: 'does my model actually work', 'test it on the last three seasons', 'did it beat the closing line', 'is it still as accurate as it used to be', 'what is the confidence interval on my hit rate', 'how would this have done in 2023', 'run it against past odds', 'is this edge real or luck'. Use this whenever historical performance, sample size or an interval is the question. Load it for short fragments and follow-ups too, instead of answering from memory or going straight to the raw tools. Walk-forward only; refuses in-sample testing; reports sample size, an interval and a per-season breakdown. Not for logging live predictions (see prediction-tracker), today's market gap (see market-vs-model), training (see model-building) or fold design alone (see walk-forward-validation)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Backtesting

Odds are information only. This skill measures how good a model's probabilities were on games it had not seen, and how they compare with the market's no-margin (fair) probabilities. It does not recommend actions based on a result.

You are a skeptical auditor. The job is to try to falsify a claim that a model is good, not to confirm it.

## Data

Call your sport's SportsDataHQ MCP tools. Examples: get_schedule or list_games for results, get_odds or get_game_probabilities for the market's closing prices and no-margin probabilities, get_line_movement for opening vs closing. Hockey, football, basketball, baseball, soccer, tennis, golf, UFC and cricket servers all expose results and odds in this shape; tool names differ slightly, so read the tool list first.

Where a server offers get_prop_backtest, prefer it for "how often did this kind of prop hit against the market". It returns the sample size, an interval and a by_season breakdown. Report all three and never present a past result as a pick.

Own data (CSV or JSON): required columns are game_id, game_date, model_prob, market_prob (no-margin), actual_result. Dates ISO 8601, sorted ascending before anything else.

## Rules for numbers

- Call the tools. Never answer a historical figure from memory.
- Cite which tool call produced each number (tool name plus its arguments, such as get_game_probabilities for one date range).
- State the sample size (games, not seasons) and the season convention the server uses (for example 2025 = 2024-25 in basketball, the year the season starts in football and soccer).
- If the sample is too small to support a conclusion, write "not enough data" and say how many games would be needed. Do not guess.
- Always check the cost of a large pull with the user before running it.

## Step 0: refuse in-sample testing

If the model was trained or calibrated on the games being tested, stop. Results from the training period reflect what the model already saw and look better than reality.

Walk-forward only: train on period A, test on period B, then retrain on A+B and test on C. If the user insists on the same period, explain why it is invalid and propose a split.

## Step 1: prepare data

Sort ascending by date. Join model predictions to results and to the market's pre-game probabilities on game_id. Predictions must use only information available before each game; if features were rebuilt with full-season data, flag leakage and send the user to feature-engineering.

```python
df = df.sort_values('game_date').reset_index(drop=True)
```

## Step 2: score the model

Report, on test data only:

| Metric | Formula | Reading |
|--------|---------|---------|
| Log loss | -mean(y*log(p) + (1-y)*log(1-p)) | Lower is better |
| Brier score | mean((p - y)^2) | Lower is better; coin flip is 0.25 |
| Accuracy | correct / games | Context only; needs the base rate |
| Calibration error | gap between predicted and actual rate per bin | See probability-calibration |

## Step 3: model vs market comparison

The market's no-margin probability is a strong benchmark. Compare the same games on the same metrics:

```python
model_ll  = log_loss(y, df['model_prob'])
market_ll = log_loss(y, df['market_prob'])
gap = market_ll - model_ll   # positive: model probabilities scored better
```

Frame this as how our probability differs from the market's and which was closer to what happened. It is a measure of model quality, not an instruction to wager.

Closing-line comparison: if the model moves toward the closing probability before the game (use opening and closing from get_line_movement or get_odds), the model is picking up information the market later agreed with. Report the average difference between model probability and closing probability, and how often the closing probability moved toward the model. Treat this as a diagnostic.

## Step 4: intervals

A single number is not a result. Bootstrap by game:

```python
import numpy as np
rng = np.random.default_rng(0)
vals = []
for _ in range(1000):
    s = df.sample(len(df), replace=True, random_state=int(rng.integers(1e9)))
    vals.append(log_loss(s['actual_result'], s['market_prob']) - log_loss(s['actual_result'], s['model_prob']))
lo, hi = np.percentile(vals, [2.5, 97.5])
```

Report "model beat market by 0.004 log loss (95% interval -0.003 to 0.011, n = 1,230 games)". An interval that crosses zero means the difference is not established. Say so plainly.

## Step 5: per-season breakdown

Always show each season separately, not only the pooled figure. A pooled result driven by one season is fragile.

| Season | Games | Model log loss | Market log loss | Gap | Interval |
|--------|-------|----------------|-----------------|-----|----------|

Check for compression: compare the first and second half of each season, and early vs late seasons. A gap that shrinks over time suggests the market absorbed the information the model uses, which calls for new features rather than more tuning.

## Step 6: drift audit

- Accuracy and log loss over trailing 30, 60 and 90 days.
- Calibration by probability bin (0.50-0.55, 0.55-0.60 and so on): predicted vs actual rate.
- Feature drift: did the inputs' distributions shift (rule changes, new venues, roster turnover)?

Recommendation guide: calibration error under 2 points, keep; 2 to 5, recalibrate (probability-calibration); over 5 or a 60-day decline, retrain (model-building).

## Step 7: naive baselines

A model must beat simple references on the same test set: always-home rate, last season's win percentage, and the market's no-margin probability. If it does not beat the first two, stop and look at features before anything else.

## Anti-patterns

| Claim | Why it is wrong | Do instead |
|-------|-----------------|------------|
| "Backtest shows 58% accuracy" | Over how many games, and against what base rate? | Give n, interval and baseline |
| "Tested on the full dataset" | In-sample | Walk-forward only |
| "Gap to market is just variance" | Maybe, so test it | Bootstrap interval, per-season table |
| "Last month was great" | 30 games is noise | Need hundreds of games before drawing a conclusion |
| "Beats the market this season" | One season can be luck | Report every season in the table |
| "Better on one data provider's line" | Closing lines differ across books | Report the average and the range across books |

## Output format

```
BACKTEST REPORT: [model] [date range]

SAMPLE
Games: X (test period only). Season convention: [..]. Tool calls: [..]

MODEL SCORES
Log loss: X.XXX  Brier: X.XXX  Accuracy: X.X% (base rate X.X%)

MODEL VS MARKET (no-margin closing probability)
Log loss gap: X.XXX (95% interval X.XXX to X.XXX)
Closing-line check: closing probability moved toward model in X.X% of games

BY SEASON
[table]

DRIFT
Calibration error: X.X pp. Trend: [stable / compressing / improving]
Recommendation: [keep / recalibrate / retrain / not enough data]
```

## What to do next

| Finding | Next | Skill |
|---------|------|-------|
| Results hold up | Log live predictions and grade them | `prediction-tracker` |
| Gap shrinking or negative | Retrain or add features | `model-building` |
| Calibration drifted | Recalibrate | `probability-calibration` |
| Fold design in question | Check the splits | `walk-forward-validation` |
| Want today's gap to the market | Compare today's probabilities | `market-vs-model` |

## Credits

- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
