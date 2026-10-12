---
name: walk-forward-validation
description: "Validates golf models in time order: expanding-window splits by tournament date, tournament-grouped evaluation, point-in-time ratings, metrics for round scores, made cut, top 10 and winner probabilities, a market baseline, and significance checks with the small number of majors. Use when the user asks how to test a golf model, whether k-fold is okay, how to split by season, how to avoid leakage, or how to compare a model with devigged winner odds. Do not use for building features -- see feature-engineering. Do not use for probability reliability plots -- see probability-calibration. Do not use for simulating betting returns -- see backtesting."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Walk-Forward Validation

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> Validation is computation on data you already pulled. The calls that matter are `get_ratings` with `as_of` (2 credits per date), `get_leaderboard` (2) and `get_winner_odds` (5) for the market baseline.

You are an expert in honest model evaluation. Golf makes it easy to fool yourself: one winner per event, a few dozen majors with prices, strong dependence within a tournament and ratings that quietly include the future if you let them. Your goal is a test whose number you would stand behind.

## When to Use

- "Can I use k-fold cross-validation on golf results?" (No.)
- "How do I split train and test?"
- "Does my model beat the market?"
- "How many majors do I need before this is meaningful?"

## When NOT to Use

- Feature construction -- see `feature-engineering`
- Reliability diagrams and scaling -- see `probability-calibration`
- Money simulation -- see `backtesting`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_ratings` | Point-in-time rating via `as_of` | 2 |
| `get_leaderboard` | Outcomes: finish, cut status, rounds | 2 |
| `get_winner_odds` | Market baseline for majors from 2021 | 5 |
| `list_tournaments` | The calendar and `major` flag, for ordering and subsets | 1 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_predictions` | Not served; the model is yours |
| `get_historical_odds` for non-majors | Not available; only majors have prices |
| `get_closing_line` | The latest pregame snapshot, which can be a week early for past majors |

## Rules

1. **Time order only.** Train on events before a date, test on events after. Never shuffle, never k-fold.
2. **Group by tournament.** All rows of one tournament go in the same fold. Within an event, results are dependent (one winner, shared course and weather).
3. **Point-in-time inputs.** Ratings with `as_of` the day before round 1. Season stats from the prior season. Course history from earlier editions.
4. **Freeze choices before testing.** Features, hyperparameters, `sigma` and `tau` are set on the training window.
5. **Compare against baselines.** At least the rating alone, and the devigged market where it exists.

## How It Works

**Step 1: Build the event list.**

```
list_tournaments {"season": 2023, "status": "final"}
```

Repeat per season and sort by `start_date`. Add `"major": true` for the majors only.

**Step 2: Choose a scheme.** An expanding window by season is the default:

| Fold | Train | Test |
|------|-------|------|
| 1 | 2015-2020 | 2021 |
| 2 | 2015-2021 | 2022 |
| 3 | 2015-2022 | 2023 |
| 4 | 2015-2023 | 2024 |
| 5 | 2015-2024 | 2025 |

Rating-based models need little training data. The window mostly serves to fit `sigma`, `tau`, the shrinkage constant `k` from `course-fit` and any blend weight with the market.

**Step 3: Pick metrics by target.**

| Target | Metric | Notes |
|--------|--------|-------|
| Round `adj_vs_field` | RMSE, MAE | baseline: the golfer's rating |
| Made cut | log loss, AUC | thousands of rows |
| Top 10 | log loss, Brier | hundreds of positives |
| Winner | log loss over the field | one positive per event |

For winners, the score of one event is `-log(p_winner)`. Average over events.

```python
import numpy as np

def winner_log_loss(prob_by_event, winner_by_event, floor=1e-4):
    s = []
    for ev, probs in prob_by_event.items():        # probs: dict player_id -> prob, sums to 1
        p = max(probs.get(winner_by_event[ev], 0.0), floor)
        s.append(-np.log(p))
    return float(np.mean(s))
```

The floor stops one zero from producing infinity; state it. A winner at 0.2% costs 6.2 nats and a winner at 15% costs 1.9, so a handful of long-priced winners dominate the mean.

**Step 4: The market baseline.** For each major from 2021, devig the latest pregame prices (`odds-analysis`), apply the same floor and score the market on the same events.

```
get_winner_odds {"season": 2025, "limit": 200}
```

A model that does not beat this baseline out of sample adds nothing over simply using the price. Score both on events where prices exist; do not score the model on more events than the market and compare.

**Step 5: Significance.** About two dozen majors have prices, so about two dozen winners. Compute the per-event loss difference (model minus market) and its standard error:

```python
d = np.array(model_losses) - np.array(market_losses)
se = d.std(ddof=1) / np.sqrt(len(d))
print(d.mean(), se)         # |mean| < 2 * se: no demonstrated difference
```

With about 25 events, a small improvement will not clear two standard errors. Say "no demonstrated difference" rather than "slightly better". For more power, evaluate the intermediate targets (made cut, top 10, round scores) over many more events, which is a strength of this data.

**Step 6: Report by subset.** Split majors from regular events only if each subset has enough rows. Put the count next to every number.

**Step 7: Keep a final holdout.** If you iterate on the 2025 fold it becomes a training fold. Hold the latest full season untouched until the end.

## Common failures

| Failure | Symptom | Fix |
|---------|---------|-----|
| Random split | Test loss far better than live | split by date and tournament |
| Current rating on past events | Suspiciously strong results for recent stars | `as_of` |
| A zero-probability winner | Infinite loss | floor, and report it |
| Tuning on the test fold | Gains vanish next year | frozen design, final holdout |
| Different event sets for model and market | Apples to oranges | same events |
| Counting golfers as independent | Fake sample size | the unit is the tournament |

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Ratings, one date per event, 100 events | 200 | |
| Leaderboards, 100 events | 200 | |
| Market for every major, 2021-2026 | 30 | one `season` call returns four majors, six seasons at 5 credits |
| Whole study on the free tier | spread over months | 500 credits a month |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Report accuracy at picking the winner | One positive per 100 rows; accuracy is meaningless | Log loss over the field |
| Call a 0.05 nat edge "significant" on 25 majors | Within noise | Show the standard error |
| Validate once and ship | Regimes change | Re-run each season |
| Score with finishing-position correlation | Field size varies | Use strokes versus the field |

## Output Format

```
Walk-forward, expanding window by season, folds 2021-2025 (majors with prices: N = <count>)
Winner log loss: model <x.xx>, devigged market <x.xx>, rating-only <x.xx>
Difference (model - market): <mean> +/- <se> over N events. Demonstrated: <yes/no>.
Made-cut log loss over <rows> golfer-events: <x.xxx>
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Model passes | Check probability reliability | `probability-calibration` |
| Model is no better than the market | Treat the market as the estimate | `odds-analysis` |
| Want to simulate returns | Money backtest | `backtesting` |
