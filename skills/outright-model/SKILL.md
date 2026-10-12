---
name: outright-model
description: "Builds a win-probability model for a golf tournament from BirdieAPI ratings: rating as of a date, course fit, field list, Monte Carlo simulation of four rounds with a cut, and a comparison with the devigged market. Use when the user wants the chance a golfer wins a major or any stroke-play event, wants to simulate a tournament, or asks why a model disagrees with the odds. Do not use for deciding or sizing bets -- see edge-detection. Do not use for validating the model's history -- see walk-forward-validation. Do not use for plain player lookups -- see player-scouting."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Outright Model

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_ratings` with `as_of` (2 credits) is the input. `get_course_history` (5) adds fit. `get_winner_odds` (5) gives the market to compare against. `get_leaderboard` (2) gives past fields and cut sizes.

You are an expert in simulation models for golf winners. Your goal is to produce honest win probabilities with uncertainty, show which assumptions move them most, and compare them with the market without implying a bet follows.

## When to Use

- "What is the chance Scheffler wins the PGA Championship?"
- "Simulate the Open with these ratings."
- "Why does my model give the favourite 7% when the books imply 15%?"
- Building the probability input for `edge-detection`

## When NOT to Use

- Staking or EV -- see `edge-detection`
- Testing the model over history -- see `walk-forward-validation` and `backtesting`
- Calibrating the output -- see `probability-calibration`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_ratings` | Rating per player, `as_of` any date, `min_rounds`, `limit` up to 500 | 2 |
| `get_player_results` | Rounds with `adj_vs_field`, to estimate round-to-round spread | 5 |
| `get_course_history` | Course fit inputs (see `course-fit`) | 5 |
| `get_leaderboard` | Past fields and `cut_count` for the same event | 2 |
| `list_tournaments` | Tournament row with `cut_round`, `cut_score`, `cut_count`, `field_size` | 1 |
| `get_winner_odds` | The market's priced golfers (a field proxy) and prices | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_win_probability`, `get_predictions` | Build it here; BirdieAPI does not serve model predictions |
| `get_field` for an upcoming event | Not available. Use the priced golfers from `get_winner_odds` as a proxy, or ask the user for the field |
| `get_tee_times`, `get_weather` | Not available; weather and wave draw are not modelled |
| `get_live_leaderboard` | Not available; no in-play updating |

## Model

For golfer `i` in a field of `n`, in round `r`:

```
strokes_vs_field[i, r] = skill[i] + fit[i] - field_mean + eps[i, r]
skill[i]  ~ Normal(rating[i], tau)        # rating uncertainty, drawn once per simulated tournament
eps[i, r] ~ Normal(0, sigma)               # round-to-round noise
```

Higher is better. Winner = highest total over four rounds (after the cut: 36 holes, then the cut line, then the weekend). Ties are rare in a continuous simulation; real ties go to a playoff, which is close to a coin toss among the tied.

Inputs:
- `rating[i]` from `get_ratings` with `as_of` = the day before the first round.
- `fit[i]` from `course-fit` (optional, shrunk).
- `sigma`: round-to-round standard deviation, estimated from `get_player_results` (`adj_vs_field` per round).
- `tau`: how uncertain the rating is. Larger for few `weighted_rounds`.
- The field: `n` golfers and their ratings. The field mean cancels in the winner comparison but matters for the cut.

## How It Works

**Step 1: Ratings before the event.**

```
get_ratings {"as_of": "2024-04-04", "limit": 500, "min_rounds": 20}
```

Real response: 313 rated players, best 2.88 (Scottie Scheffler), lowest -1.68. Ratings are within one tour, so for LIV golfers in a major, widen `tau` and say why; their rating is built against LIV fields.

**Step 2: The field.** The upcoming field is not in the data. Take the priced golfers as a proxy:

```
get_winner_odds {"tournament_id": "401580344", "limit": 200, "bookmaker": "draftkings"}
```

115 golfers were priced for the 2024 Masters; 97 of them had a rating. The unrated ones (old champions, amateurs, qualifiers) are mostly weak. Dropping them makes the field artificially strong and pushes every probability down. Give them a rating below the lowest rated player, or flag it in the output.

**Step 3: Estimate sigma.**

```
get_player_results {"player_id": "9478", "season": 2023, "limit": 50}
```

Real response: 96 rounds with `adj_vs_field`, mean 3.35, standard deviation 2.53. Pool several players rather than using one. Note this standard deviation also includes slow drift in form, so it slightly overstates pure round noise; that is a modelling choice to state, not hide.

**Step 4: Simulate.**

```python
import numpy as np

def simulate(rating, sigma, tau, cut_n, n_sims=20000, seed=7):
    rng = np.random.default_rng(seed)
    wins = np.zeros(len(rating))
    for _ in range(n_sims // 1000):
        skill = rating[None, :] + rng.normal(0, tau, (1000, len(rating)))
        tot = np.zeros((1000, len(rating)))
        for rd in range(4):
            tot += skill + rng.normal(0, sigma, (1000, len(rating)))
            if rd == 1:                                   # cut after round 2
                kth = np.sort(tot, axis=1)[:, -cut_n][:, None]
                tot = np.where(tot < kth, -1e9, tot)
        wins += np.bincount(np.argmax(tot, axis=1), minlength=len(rating))
    return wins / n_sims
```

`cut_n` comes from the tournament row (`cut_count` was 50 for the 2024 Masters). Ties at the cut line would let a few more through; ignore them for winner probabilities and say so.

**Step 5: Run the sensitivity, not one number.** First-pass illustration on the 97 rated, priced golfers of the 2024 Masters (ratings as of 2024-04-04, 20,000 simulations, seed 7, no course fit):

| Assumptions | Scheffler | Rahm | Schauffele | McIlroy |
|-------------|-----------|------|------------|---------|
| sigma 2.53, tau 1.0 | 6.7% | 5.2% | 4.2% | 3.7% |
| sigma 2.53, tau 0.5 | 8.7% | 6.3% | 5.0% | 4.4% |
| sigma 2.53, tau 0.0 | 9.7% | 6.8% | 5.6% | 4.8% |
| sigma 2.0, tau 0.0 | 14.2% | 8.8% | 7.2% | 6.1% |

For comparison, the DraftKings latest price devigged by the power or Shin method put Scheffler at 15% to 16% (see `odds-analysis`). The favourite's probability swings from 6.7% to 14.2% on two assumptions. That is the main lesson: the output of a rating-based simulation is governed by `sigma` and `tau`, which must be estimated and validated, not picked to match the market. Matching the market by tuning the inputs defeats the point of the comparison.

**Step 6: Add fit and the market.** Add `fit[i]` from `course-fit` to `skill`. Then compare to the devigged market: where the model disagrees by more than its own sensitivity range, ask why before concluding anything. Common reasons: ratings lag a form change; injury or withdrawal knowledge the data lacks; a field mismatch; a wrong `sigma`.

**Step 7: Blend, don't replace.** The market contains information a rating does not (injury news, equipment, preparation). A defensible final probability is a weighted average of model and devigged market in log-odds, with the weight set by out-of-sample log loss in `walk-forward-validation`.

## Limits to state every time

- Only about two dozen majors have winner prices in the data, so only about two dozen winners to validate against. See `backtesting`.
- Score-based ratings, no shot data, no weather, no tee times, no injury information.
- Four-round stroke play only. Match play and team formats are not modelled.
- The 2024 numbers above are a worked illustration of method, not a forecast or a recommendation.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Ratings as of a date | 2 | one call, up to 500 players |
| Market and field proxy | 5 | one call |
| Sigma from five players | 25 | pool across players |
| Course fit for top 20 | 100 | optional |
| Minimal build (ratings, market, one sigma pull) | 12 | |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Use today's rating for a past event | Leakage | `as_of` the day before |
| Tune `sigma` until the favourite matches the books | Circular; no information left to compare | Estimate it from data |
| Drop unrated golfers silently | Field too strong, probabilities too low | Include with a low rating, or disclose |
| Report 6.73% | False precision | Report a range from the sensitivity table |
| Call the output a pick | It is a probability with wide error | Pass to `edge-detection` with caveats |
| Ignore the cut | Players who miss it cannot win | Apply it after round 2 |

## Output Format

```
2024 Masters win probability, rating-based simulation (97 golfers, 20,000 runs)
Scottie Scheffler: 7% to 14% depending on sigma and tau (see table). Market, devigged: 15% to 16%.
Inputs: ratings as of 2024-04-04; sigma from data; no course fit; no weather or injury information.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A probability set | Check calibration on past majors | `probability-calibration` |
| A difference from the market | Edge and stake | `edge-detection` |
| A fit input | Build it properly | `course-fit` |
| Parameters to tune | Walk-forward | `walk-forward-validation` |
