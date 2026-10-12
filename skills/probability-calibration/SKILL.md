---
name: probability-calibration
description: "Checks and repairs golf probabilities: reliability tables for made-cut, top-10 and winner probabilities, Brier score and log loss, pooled calibration across golfers, isotonic and Platt scaling, and why winner calibration needs outcomes beyond the majors. Use when the user asks whether their golf probabilities are calibrated, how to read a reliability diagram for longshots, how to calibrate a simulation's output, or why a model's 3% golfers win more or less than 3%. Do not use for building the model -- see outright-model. Do not use for time-ordered testing -- see walk-forward-validation. Do not use for turning probabilities into stakes -- see edge-detection."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Probability Calibration

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> Calibration is computation. The data calls are `get_leaderboard` (2 credits per event) for outcomes (made cut, top 10, winner) and `get_ratings` with `as_of` (2) for point-in-time inputs.

You are an expert in probability reliability. Your goal is to tell the user whether "3%" means 3%, to fix it where the data can support a fix, and to say plainly where it cannot.

## When to Use

- "Are my top-10 probabilities calibrated?"
- "My simulation gives longshots too much (or too little) chance."
- "How do I make a reliability plot for winner probabilities?"
- Before sending probabilities to `edge-detection`

## When NOT to Use

- Building the probabilities -- see `outright-model`
- Out-of-sample splits -- see `walk-forward-validation`
- EV and stakes -- see `edge-detection`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_leaderboard` | Outcomes per golfer: `position`, `status` (cut, wd, dq), rounds | 2 |
| `get_ratings` | Point-in-time inputs | 2 |
| `get_winner_odds` | Devigged market probabilities as a reference | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_calibration`, `get_brier` | Compute locally |
| `get_top10_odds` | Not available; calibrate model top-10 against outcomes, not against prices |

## Why winners are hard to calibrate

A major has about 90 to 156 starters and one winner. Across about two dozen majors with prices there are about two dozen winners. A reliability table with ten bins over that has two or three winners per bin. It cannot tell 3% from 6%.

So calibrate in layers:

| Layer | Outcome | Rows available | Use |
|-------|---------|----------------|-----|
| Made cut | binary | thousands per season | calibrate the player-quality scale |
| Top 10 | binary | hundreds per season | calibrate the upper tail |
| Round scores | continuous | tens of thousands | check mean and spread of residuals |
| Winner | binary | about two dozen with prices; more without (any event) | final sanity check only |

If the model's top-10 probabilities are calibrated across all PGA Tour events, its winner probabilities inherit a good deal of that. Winner probabilities from any stroke-play event can be scored without prices (outcome from `get_leaderboard`), which gives far more events than the majors alone.

## How It Works

**Step 1: Collect predictions and outcomes.** For each golfer-event: predicted probability, outcome (1 if finishing in the top 10 including ties, else 0). Take the outcome from `position` in `get_leaderboard`. Use the same tie rule as the prediction target and say which.

```
get_leaderboard {"tournament_id": "401580344"}
```

**Step 2: Reliability table.** Bin by predicted probability. For rare outcomes use quantile bins on the probability, not equal-width, so each bin has enough rows. Report count, mean predicted, observed rate and an interval.

```python
import numpy as np, pandas as pd

def reliability(p, y, bins=10):
    df = pd.DataFrame({"p": p, "y": y})
    df["bin"] = pd.qcut(df["p"], bins, duplicates="drop")
    out = df.groupby("bin", observed=True).agg(n=("y", "size"), pred=("p", "mean"), obs=("y", "mean"))
    out["se"] = np.sqrt(out["obs"] * (1 - out["obs"]) / out["n"])
    return out
```

Read: a bin is "off" only if `|pred - obs| > 2 * se`. With `n` of 50 and an observed rate near 3%, `se` is about 2.4 points, so almost nothing is distinguishable. Increase `n` before concluding.

**Step 3: Scores.** Brier for the mean squared error, log loss for the tails:

```python
brier = np.mean((p - y) ** 2)
logloss = -np.mean(y * np.log(np.clip(p, 1e-6, 1)) + (1 - y) * np.log(np.clip(1 - p, 1e-6, 1)))
```

For rare events the Brier score is dominated by the zeros. Always compare with the base rate: predicting the constant `y.mean()` gives a baseline Brier of `base * (1 - base)`. Skill = `1 - brier / baseline`.

**Step 4: Pooled calibration across golfers.** Pool all golfer-events; do not calibrate per golfer (too little data). If the shape is off in the tail, fit a monotone map.

```python
from sklearn.isotonic import IsotonicRegression
iso = IsotonicRegression(out_of_bounds="clip").fit(p_train, y_train)
p_cal = iso.predict(p_test)
```

Isotonic regression is flexible and needs a few hundred positives. For fewer, use a one-parameter power map on the log-odds (temperature) instead: `logit(p') = a * logit(p)` with `a` fitted by maximum likelihood.

**Step 5: Renormalise winners.** After mapping each golfer's win probability, rescale within the event so the field sums to 1. Otherwise your probabilities will not describe a single winner.

**Step 6: Longshot check.** Sum the model's probabilities for golfers ranked below, say, 40th. Compare that share with how often golfers ranked below 40th in pre-event rating have actually won, across as many events as you have. If the model gives the tail 0% and the tail has won in several events, or the reverse, it is wrong in a visible way. This check needs no prices.

## Reading the simulation's uncertainty

In `outright-model`, a rating-uncertainty parameter `tau` flattens the field and lifts longshots; a smaller `sigma` concentrates probability on the best. Calibration is how you choose them: pick the `(sigma, tau)` pair that minimises made-cut and top-10 log loss on a training window, then confirm out of sample. Do not choose them to match the winner market.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Outcomes for 100 events | 200 | `get_leaderboard` each |
| Ratings at 100 event dates | 200 | |
| Market reference for majors | 30 | `season` calls, 6 seasons |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Ten equal-width bins on winner probabilities | Empty bins, huge error | Quantile bins, pooled outcomes, show the interval |
| Calibrate on the test period | Leakage | Fit the map on training events only |
| Declare "well calibrated" from 25 majors | No power | Use made-cut and top-10 layers |
| Calibrate then forget to renormalise | The field no longer sums to 1 | Rescale per event |
| Match the market instead of the outcomes | The market is a baseline, not the truth | Score against results |
| Use finishing position ties inconsistently | Top-10 label shifts | One tie rule, stated |

## Output Format

```
Calibration, top-10 probability, <N> golfer-events (<first>-<last>)
Quantile bins: predicted vs observed with 2-se intervals (table)
Brier <x.xxx> vs base-rate baseline <x.xxx>, log loss <x.xxx>
Tail check: golfers ranked below 40th carry <x>% of model win probability; <y>% of past winners came from there
Fix applied: <none | isotonic | temperature a = x.xx>, fitted on training events only
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Calibrated | Compare with the market | `edge-detection` |
| Tail off | Revisit `tau` and `sigma` | `outright-model` |
| Unsure of out-of-sample behaviour | Time-ordered test | `walk-forward-validation` |
