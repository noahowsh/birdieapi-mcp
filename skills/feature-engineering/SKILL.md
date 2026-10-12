---
name: feature-engineering
description: "Builds leak-free model features for golf from BirdieAPI data: ratings as of a date, rolling strokes versus the field, field-strength adjusted form, course history with shrinkage, par-type splits, field and event features, with rules for time order and target definition. Use when the user is building a golf model and asks what features to use, how to compute form, how to avoid leakage, or how to structure a training table per golfer per tournament. Do not use for validating the model -- see walk-forward-validation. Do not use for the rating explanation -- see strokes-vs-field. Do not use for simulating tournaments -- see outright-model."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Feature Engineering

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_player_results` (5 credits per player) is the workhorse: every round with `adj_vs_field`. `get_ratings` (2) with `as_of` supplies point-in-time ratings. `get_leaderboard` (2) supplies finishes.

You are an expert in building point-in-time features for golf. Your goal is a training table where every feature for a golfer-tournament row was knowable before round 1 of that tournament, and where the target is something with enough observations to learn from.

## When to Use

- "What features should I use to predict who wins?"
- "How do I compute form without leaking the future?"
- "How should I lay out the training table?"
- Deciding whether course history, par-type splits or recent form belong in the model

## When NOT to Use

- Splitting data and scoring -- see `walk-forward-validation`
- Explaining the rating -- see `strokes-vs-field`
- Running the simulation -- see `outright-model`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_player_results` | Round-level `strokes`, `field_avg`, `vs_field`, `adj_vs_field`, finish, per tournament | 5 |
| `get_ratings` | Rating at `as_of` | 2 |
| `get_leaderboard` | The whole field, finishing order, cut status, rounds | 2 |
| `get_course_history` | Record at an event or course | 5 |
| `get_player_stats` | Season hole scoring, `sg_par*`, ball-striking lines | 5 |
| `list_tournaments` | The event calendar and `start_date` for time ordering | 1 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_features`, `get_training_data` | Build the table yourself from the calls above |
| `get_world_ranking_history` | `get_ratings` at different `as_of` dates |
| `get_weather`, `get_tee_times`, `get_wave` | Not available; do not feature them |
| `get_field` for a future event | Not available |

## The table

One row per golfer per tournament. Order by `start_date`.

| Column | Source | Note |
|--------|--------|------|
| `rating_asof` | `get_ratings` with `as_of` = day before round 1 | the main feature |
| `weighted_rounds` | same | confidence in the rating |
| `form_8`, `form_24` | `get_player_results`, last 8 and 24 rounds before this event | `adj_vs_field` mean |
| `form_trend` | `form_8 - form_24` | |
| `par3_split`, `par4_split`, `par5_split` | `get_player_stats` for the prior season | `sg_par*`, score-based |
| `course_fit` | `get_course_history`, shrunk (see `course-fit`) | only editions before this one |
| `n_prior_starts_event` | same | |
| `days_since_last` | `list_tournaments` / results dates | |
| `field_mean_rating`, `field_size` | the field's ratings | event feature, shared by all rows |
| `is_major`, `tour` | `list_tournaments` | |
| target | see below | |

## Targets

Winners are rare: one per event. Train on targets with enough data, then convert.

- **Best:** round-level `adj_vs_field` for each golfer-round. Thousands of rows per season. Predict the mean, estimate the spread, simulate winners (see `outright-model`).
- **Good:** made cut (binary), top 10 (binary), finishing percentile.
- **Last:** winner (binary). Fewer than one positive per hundred rows. Use only for evaluation, not training, unless you pool many events.

## How It Works

**Step 1: Choose the unit and the clock.** The clock is the tournament `start_date`. Every feature for a row uses data strictly before it.

**Step 2: Rolling form with a shift.**

```python
import pandas as pd

# rounds: one row per golfer-round, columns: player_id, start_date, round, adj_vs_field
rounds = rounds.sort_values(["player_id", "start_date", "round"])
g = rounds.groupby("player_id")["adj_vs_field"]
rounds["form_8"] = g.transform(lambda s: s.shift(1).rolling(8, min_periods=4).mean())
```

`shift(1)` is the leakage guard: a round's own score is never in its own feature. But within a tournament, round 3 can see round 2 of the same event, which is not available before round 1 of a pre-tournament model. For pre-tournament features, aggregate by tournament first and shift by tournament:

```python
per_event = rounds.groupby(["player_id", "start_date"])["adj_vs_field"].mean().reset_index()
per_event["form_2ev"] = (per_event.groupby("player_id")["adj_vs_field"]
                         .transform(lambda s: s.shift(1).rolling(2, min_periods=1).mean()))
```

**Step 3: Point-in-time ratings.** Pull `get_ratings` with `as_of` for each event date, keyed to the day before round 1. One call returns up to 500 players, so one call per event. For 30 events that is 60 credits.

```
get_ratings {"as_of": "2024-04-04", "limit": 500, "min_rounds": 20}
```

**Step 4: Course history inside the clock.** For event edition `E`, include only editions before `E`. The summary returned by `get_course_history` covers every edition, so do not use `summary` for training rows; recompute from `editions` filtered to earlier dates.

**Step 5: Season-level stats.** `get_player_stats` returns a full season. For an event in April 2024 use 2023, not 2024. The 2024 line already contains the event.

**Step 6: Field features.** Field mean rating and size are event-level. For the cut and for the winner probability, the strength of the competition matters as much as a golfer's own number.

## Leakage checklist

| Leak | How it happens | Fix |
|------|----------------|-----|
| Today's rating on a past row | `get_ratings` without `as_of` | `as_of` day before |
| Season stats for the same season | `get_player_stats` season = event year | use the prior season |
| `get_course_history` summary | Includes the target edition | rebuild from `editions` |
| Rolling window without shift | Row includes its own round | `shift(1)` and tournament-level shifts |
| Random split | Same tournament in train and test | split by date |
| Field proxy from results | Using the finished leaderboard as the pre-event field | the priced list or the user's list |

## Cross-tour features

Ids are shared across tours, so a LIV golfer's PGA Tour history joins on `player_id`. Ratings are not comparable across tours. Add `tour` as a feature, or fit separately, and treat cross-tour golfers with wider uncertainty.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Ratings for 30 events | 60 | one call per event |
| Rounds for 100 golfers | 500 | one call per golfer; exceeds the free tier |
| Course history for the top 20 in one event | 100 | |

If the free tier is the budget, train on ratings and leaderboards only (2 credits each) and add rounds for a shortlist.

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Predict the winner label directly | About 1 positive per 100 rows | Predict round scores, simulate |
| Use finishing position as the target | Depends on field size | Use strokes versus the field or percentile |
| Hand-pick features after seeing test results | Selection leakage | Fix the list before the test period |
| Standardise on the full dataset | Test statistics leak into train | Fit scalers in the training window |
| Many highly correlated form windows | Overfit with few tournaments | Two or three windows |

## Output Format

```
Training table: <N> golfer-events, <first season>-<last season>, one row per golfer per event
Features: rating_asof, weighted_rounds, form_8, form_24, par5_split, course_fit (shrunk), field_mean_rating
Target: mean adj_vs_field per round (regression), winners kept for evaluation
Leakage checks: ratings as_of day before round 1; season stats from prior season; no random split
```

## What to Do Next

| What You Built | Next Action | Skill |
|----------------|-------------|-------|
| A feature table | Validate in time order | `walk-forward-validation` |
| A model | Simulate winners | `outright-model` |
| Probabilities | Check calibration | `probability-calibration` |
