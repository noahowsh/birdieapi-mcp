---
name: course-fit
description: "Measures how a golfer has played at one tournament or one course across every year, and how much of that record is course fit rather than general form. Use when the user asks who plays well at Augusta or Pebble Beach, how a player's record at an event looks, whether course history matters, or how to blend course form with overall rating. Do not use for ranking current form on its own -- see strokes-vs-field. Do not use for how the holes of a course played -- see hole-scoring. Do not use for turning fit into a win probability -- see outright-model."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Course Fit

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_course_history` (5 credits) returns a player's record at one tournament or one course across years. `get_course` (2) describes the course. `get_ratings` (2) gives the baseline.

You are an expert in separating "this player is good" from "this player is good here". Golf course history is real but noisy, and most of it is just general quality. Your job is to measure the part that is left over and say how sure you are.

## When to Use

- "How has Scottie Scheffler done at the Masters?"
- "Who has the best record at Pebble Beach since 2010?"
- Comparing a field's course records before a tournament
- Deciding how much weight course history gets in a model
- Checking whether a hot player has a poor record at this venue

## When NOT to Use

- Current form or the rating -- see `strokes-vs-field`
- Hole difficulty and setup -- see `hole-scoring`
- Final probabilities -- see `outright-model`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_course_history` | One player at one tournament (any edition's `tournament_id`, every year returned) or at one course (`course_id`, across tournaments): finishes, rounds, `vs_field`, summary | 5 |
| `get_course` | Par and yards per hole, how each hole played, for one tournament's course | 2 |
| `list_tournaments` | Find the tournament id and `course_id` values | 1 |
| `get_ratings` | The player's overall rating for the baseline | 2 |
| `get_player_results` | Raw rounds if you want your own course filter | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_course_fit`, `get_fit_score` | Compute it from `get_course_history` and `get_ratings` as below |
| A whole field's course history in one call | One `get_course_history` call per player; shortlist first |
| `get_course_stats_by_year` | `get_course` per edition |
| `get_course_conditions`, `get_weather` | Not available |

## How It Works

**Step 1: Pick tournament or course.** Pass `tournament_id` of any year to get every edition of that event. Pass `course_id` to get every tournament played on that course (useful for a course that hosts different events). Get ids from `list_tournaments`; its `courses[]` lists each tournament's `course_id`.

**Step 2: Pull the record.**

```
get_course_history {"player_id": "9478", "tournament_id": "401580344"}
```

Real response (trimmed), Scottie Scheffler at the Masters:

```
summary: starts 7, wins 2, top_tens 5, made_cut 7, average_finish 7.9, vs_field 2.78
editions: 2026  finish 2   vs_field 3.30   rounds 70 74 65 68
          2025  finish 4   vs_field 2.68   rounds 68 71 72 69
          2024  finish 1   vs_field 4.57   rounds 66 72 71 68
          2023  finish T10 vs_field 2.01
          2022  finish 1   vs_field 4.36
          2021  finish T18 vs_field 1.23
```

Here `vs_field` is the player's average strokes versus the field per round at that event. Seven starts is 28 rounds.

**Step 3: Compare with the baseline.** The question is not whether 2.78 is good. It is whether it is better than he is in general. Pull his rating (or his `vs_field` over a comparable window):

```
get_ratings {"limit": 50}
```

A simple fit measure for player `i` at event `e`:

```
fit_raw = mean(event vs_field) - overall level at the time of those rounds
```

For a fair "overall level" use the rating as it stood before each edition (`get_ratings` with `as_of` per year), not today's rating. Using today's rating for a 2021 start leaks the future.

**Step 4: Shrink.** Course history is a small sample. Blend it toward zero:

```
fit = n_rounds / (n_rounds + k) * fit_raw
```

`k` is the number of rounds at which course history deserves half weight. Do not hard-code one. Treat `k` as a parameter, fit it with `walk-forward-validation`, and report the value used. A starting assumption of a few dozen rounds is a guess, not a finding.

**Step 5: Check what the fit is made of.** A record can come from the course's design (long par 5s, firm greens) or from a few hot weeks. Use `get_course` to profile the holes and `hole-scoring` to see whether the player's par-type split lines up with what the course rewards. If a course has four reachable par 5s and the player's `sg_par5` is elite, that is a mechanism. A good record with no mechanism is lower confidence.

**Step 6: Treat course changes as breaks.** A course can be redesigned, or a tournament can move venues. `courses` is listed per edition; if the venue changed, split the record at the change. Do not mix.

## How much does course history matter

Say what is known and what is not. In general, course-specific skill exists in golf but is small relative to general skill, which is why shrinkage is the right default. The size for a given course and tour should be measured, not assumed: run the shrinkage fit on past editions with `walk-forward-validation` and see whether adding `fit` improves out-of-sample log loss on winners or on finishing scores. If it does not, drop it.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| One player's record at one event | 5 | |
| Ten-player shortlist | 50 | |
| Whole field of 90 | 450 | do not; shortlist by rating first |
| Baseline ratings at one date | 2 | |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Rank players by average finish at the course | Finish depends on field size and luck | Use `vs_field` per round |
| Add course history without a baseline | It double-counts general skill | Subtract the overall level first |
| Use today's rating as the baseline for a 2019 start | Leakage | `as_of` before each edition |
| Trust 2 starts | 8 rounds is noise | Shrink and show `n_rounds` |
| Ignore a venue move | Different course | Split the record |
| Call a player a "course horse" on one win | One week of luck | Require multiple editions |

## Output Format

```
Scottie Scheffler at the Masters (Augusta National), 7 starts
Wins 2, top tens 5, average finish 7.9, strokes versus the field +2.78 a round.
Baseline rating before each start: see get_ratings as_of.
Shrunk fit estimate: +X.XX a round (n = 28 rounds, k = <value used>)
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A fit number per golfer | Feed it into a win model | `outright-model` |
| A mechanism question | Look at hole splits | `hole-scoring` |
| Fit used as a feature | Check for leakage | `feature-engineering` |
| Want to validate the weight | Out-of-sample test | `walk-forward-validation` |
