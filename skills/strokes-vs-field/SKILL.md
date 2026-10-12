---
name: strokes-vs-field
description: "Explains and uses BirdieAPI's strokes-versus-field numbers: the per-round vs_field and field-strength adjusted adj_vs_field, the get_ratings rating, and how to rank, compare and track golfers on them. Use when the user asks who is playing best, what a rating of 2.0 means, how to measure form, how to compare players from different fields, or what the closest thing to strokes gained is. Do not use for the official shot-level strokes gained categories -- they are not in the data. Do not use for par 3/4/5 splits -- see hole-scoring. Do not use for one player's profile -- see player-scouting."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Strokes Versus the Field

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_ratings` (2 credits) ranks everyone. `get_player_results` (5) gives each round. `get_leaders` (5) ranks a season on `vs_field` or `adj_vs_field`.

You are an expert in score-based golf ratings. Your goal is to give the user the right number for the question, say what it is and is not, and never present it as the official PGA Tour strokes gained statistic.

## What these numbers are

- **`vs_field` (round level):** the field's average score for that tournament, round and course, minus the player's score. A 68 against a field average of 71.5 is +3.5. Positive is better.
- **`adj_vs_field`:** the same idea corrected for how strong the field was. Each round's field average mixes the course's difficulty with the players' skill. The model solves both over every round of a tour and reports expected average-player score minus the player's score.
- **Rating (`get_ratings`):** strokes per round better than an average player in the same fields, field-strength adjusted, weighted toward recent rounds (half-life one year) and shrunk toward zero for players with few rounds. A rating of 2.0 means two strokes a round better than an average player on the same tour.
- It is **score-based**. It is the site's own strokes-versus-field rating, in the same spirit as strokes gained: total, but computed from scores. There is **no shot data**, so there is no off-the-tee, approach, around-the-green or putting split.

The glossary at https://birdieapi.com/glossary/strokes-versus-field reports how it tracks the PGA Tour's published SG: Total over 2015 to 2025 (a correlation of about 0.97 on season means for the raw number, about 0.96 for the adjusted one, which also runs about 0.7 strokes a round above SG: Total). Quote those from the page, and still call it a ranking and comparison number, not official strokes gained.

## When to Use

- Who is playing best right now, or was on a past date (`as_of`)
- Comparing two players from different schedules
- Measuring a player's form over the last N rounds
- Ranking a season on a stat
- Explaining to a user what "+2.0" means

## When NOT to Use

- Hole-type splits (`sg_par3`, `sg_par4`, `sg_par5`) -- see `hole-scoring`
- A single player profile -- see `player-scouting`
- Win probabilities -- see `outright-model`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_ratings` | Rating for every player active in the past year, best first. `limit`, `as_of`, `min_rounds`, `league` | 2 |
| `get_player_results` | Each tournament with every round's `field_avg`, `vs_field`, `adj_vs_field` | 5 |
| `get_leaders` | Season leaders on `vs_field`, `adj_vs_field`, `scoring_average` and other stats, with sample | 5 |
| `get_leaderboard` | Per-round `vs_field` for a whole tournament field | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_strokes_gained` | `get_ratings` or `get_leaders` with `stat` `adj_vs_field` |
| `get_sg_ott`, `get_sg_app`, `get_sg_putt` | Not available; no shot data |
| `get_world_ranking` | `get_ratings` |
| `get_ratings_history` | Call `get_ratings` with different `as_of` dates |

## How It Works

**Step 1: Rank the tour.**

```
get_ratings {"limit": 5}
```

Real response (trimmed, as of 2026-10-04):

```
1  Scottie Scheffler    3.31   weighted_rounds 133.1
2  Rory McIlroy         2.39   weighted_rounds  96.8
3  Tommy Fleetwood      2.19   weighted_rounds 119.8
4  Xander Schauffele    2.18   weighted_rounds 122.5
5  Collin Morikawa      2.05   weighted_rounds 114.9
```

`weighted_rounds` is the decay-weighted sample behind the rating. A rating on 30 weighted rounds is much softer than one on 130. Raise `min_rounds` to drop thin ratings (default 20).

**Step 2: Rank on a past date.** Use `as_of` to avoid hindsight:

```
get_ratings {"as_of": "2024-04-01", "limit": 3}
```

Real response: Scheffler 2.88, Rahm 2.58, Schauffele 2.48. The ratings as they stood before the 2024 Masters, not today's. This is the only correct input for backtesting a pre-tournament model.

**Step 3: Look at the rounds.**

```
get_player_results {"player_id": "9478", "season": 2025, "limit": 2}
```

Real round (Hero World Challenge, 20-player field): strokes 66, `field_avg` 69.05, `vs_field` 3.05, `adj_vs_field` 4.46. The adjusted number is higher because that field is stronger than an average tour field, so beating it counts for more. The raw number alone would understate the round.

**Step 4: Form.** Use `adj_vs_field` and weight recent rounds. A simple form figure:

```python
import numpy as np
def form(rounds, half_life=8):
    # rounds: adj_vs_field values, oldest first
    w = 0.5 ** (np.arange(len(rounds))[::-1] / half_life)
    return float(np.sum(w * rounds) / np.sum(w))
```

Report the number of rounds. Eight rounds is two tournaments; the standard deviation of a golfer's single round is large (typically 2 to 3 strokes), so form on eight rounds has a standard error near 1 stroke. Estimate the standard deviation from the user's own `get_player_results` pull rather than quoting a constant.

**Step 5: Compare within a tour only.** LPGA, LIV, DP World Tour, Korn Ferry and the PGA Tour each rate against their own fields. A 3.18 on the LPGA (Jeeno Thitikul, Nelly Korda in the live check) is not comparable to a 3.31 on the PGA Tour. For cross-tour questions use shared events, such as the majors, via `get_head_to_head`.

**Step 6: Leaders.**

```
get_leaders {"stat": "adj_vs_field", "season": 2025, "limit": 10, "min": 40}
```

`min` is the minimum rounds (default 40) for round-based stats. Report `sample` beside each name.

## Pitfalls

| Pitfall | Why it bites |
|---------|--------------|
| Using raw `vs_field` across events | A weak field flatters it; use `adj_vs_field` |
| Treating the rating as skill with no error | It is shrunk, decayed and noisy; show `weighted_rounds` |
| Mixing seasons without `as_of` | Today's rating is leaked into the past |
| Comparing LIV and PGA Tour ratings | Different fields; players with majors in both can be compared on those |
| Calling it "strokes gained" | It is a score-based strokes-versus-field rating |
| Reading 0.1-stroke gaps as real | Rank ties inside the noise band |

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Top-50 ratings | 2 | one call |
| Ratings at five past dates | 10 | for a trend |
| One player's season of rounds | 5 | |
| Season leaders on one stat | 5 | |

## Output Format

```
Ratings as of 2026-10-04 (PGA Tour, strokes versus the field per round, field-strength adjusted)
1. Scottie Scheffler  +3.31  (133 weighted rounds)
2. Rory McIlroy       +2.39  (97)
Score-based, not shot-level strokes gained. Measured within the PGA Tour.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A ranked list | Turn into win probabilities | `outright-model` |
| Form and rating for a player | Full scouting note | `player-scouting` |
| Want hole-type detail | Par 3/4/5 splits | `hole-scoring` |
| Inputs for a model | Build features | `feature-engineering` |
