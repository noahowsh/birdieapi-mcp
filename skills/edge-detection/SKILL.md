---
name: edge-detection
description: "Compares a golf win probability against outright prices to estimate expected value, size stakes on mutually exclusive winner bets, and judge whether an apparent edge is real. Use when the user has a model probability for a golfer and asks about EV, Kelly, fractional Kelly across a field, longshot variance, how many majors it takes to confirm an edge, or whether a price is worth taking. Do not use for exploring prices -- see odds-explorer. Do not use for devigging -- see odds-analysis. Do not use for validating the model -- see walk-forward-validation or backtesting. Do not use for each-way, matchup or top-10 bets -- their prices are not in the data."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Edge Detection

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_winner_odds` (5 credits) supplies prices for the four men's majors. The rest is arithmetic on a probability you bring (see `outright-model`).
> With the user's own prices and probabilities, skip the tool: no credits.

You are an expert in turning a probability and a price into an honest estimate of expected value. Golf outrights are the high-variance end of betting: most prices are longshots, one golfer wins, and a skilled bettor can lose for years. Everything here is an estimate, not a promise.

> **Honest framing.** An outright model that disagrees with the market by a few points is far more likely to be miscalibrated than right. The market is a strong baseline. This skill exists to find out whether an edge is plausible, not to manufacture one.

## When to Use

- "My model has McIlroy at 9% and the price is +1400. Is that value?"
- "How much should I stake across five golfers?"
- "How many majors until I know my edge is real?"
- "Which book has the best number on the golfer I like?"

## When NOT to Use

- Browsing prices -- see `odds-explorer`
- Converting or devigging prices -- see `odds-analysis`
- Making the probability -- see `outright-model`
- Historical test of a strategy -- see `backtesting`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_winner_odds` | Prices by book: opening and latest pregame, with raw implied probability | 5 |
| `get_leaderboard` | Result, to settle a past bet | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_ev`, `get_edge`, `get_best_line` | Compute from `get_winner_odds` and the model probability |
| `get_live_odds`, `get_in_play_odds` | Not available; prices are pregame snapshots |
| `get_each_way_odds`, `get_top_10_odds`, `get_matchup_odds` | Not available |
| `get_clv` | Not available; see CLV limits below |

## How It Works

**Step 1: Expected value of a single outright.** With decimal odds `d` (American positive `a`: `d = a/100 + 1`) and win probability `p`:

```
EV per unit staked = p * d - 1
```

Example arithmetic (hypothetical numbers, not from the data): a +5000 price is `d = 51`. A model probability of 2.5% gives `EV = 0.025 * 51 - 1 = +0.275`, i.e. +27.5%. A model probability of 1.5% gives `EV = -0.235`. The same price flips from strongly positive to strongly negative inside a one-point range of `p`. This is why you quote EV as a range over the model's uncertainty, not as a point.

**Step 2: Use the right comparison price.** Pull the market:

```
get_winner_odds {"tournament_id": "401580344", "limit": 20}
```

For each golfer the best available price is the highest American price across `books[]` at `latest_pregame`. The latest pregame snapshot can be up to a week before the first tee for past majors, so the price you could actually have taken may differ. For an upcoming major the snapshot is refreshed daily, and every six hours in tournament week.

**Step 3: Honest edge, not raw gap.**

1. Compare your probability with the devigged market probability (`odds-analysis`), by two methods, before looking at EV. If your 4% versus a devigged 3.1% to 3.6% is the whole story, the edge is within method noise.
2. Require the edge to survive your model's own sensitivity range (the sigma and tau table in `outright-model`).
3. Haircut: shrink your probability toward the devigged market in log-odds (a weight of 0.5 is a defensible start, to be fitted with `walk-forward-validation`) before computing EV.

**Step 4: Longshot bias and the tail.** Probabilities for golfers priced beyond about +10000 are the least reliable part of any model and the part where the books' margin is largest. EV in the tail is dominated by `p` errors. Demand a larger edge there, or skip it.

**Step 5: Sizing mutually exclusive bets.** Only one golfer wins, so stakes on different golfers in the same event are negatively correlated, not independent. Single-bet Kelly `f = (p*d - 1)/(d - 1)` applied to each golfer and summed will overstate the right exposure. Solve the joint problem: choose stakes `s_i >= 0` to maximise expected log wealth over the outcomes "golfer j wins" and "someone not bet on wins".

```python
import numpy as np
from scipy.optimize import minimize

def joint_kelly(p, d, fraction=0.25):
    # p: win probabilities (sum < 1), d: decimal odds for the candidate golfers
    n = len(p); p_other = 1 - p.sum()
    def neg_log_growth(s):
        total = s.sum()
        wins = 1 - total + s * d            # wealth if golfer j wins
        other = 1 - total                   # wealth if nobody bet on wins
        return -(np.sum(p * np.log(np.maximum(wins, 1e-9))) + p_other * np.log(max(other, 1e-9)))
    res = minimize(neg_log_growth, np.full(n, 0.001), bounds=[(0, 0.1)] * n,
                   constraints=[{"type": "ineq", "fun": lambda s: 0.5 - s.sum()}])
    return res.x * fraction
```

Then apply a fractional multiplier. A quarter of full Kelly is a common starting point because the probability is uncertain; full Kelly on an overstated `p` is how bankrolls shrink. Cap the total outlay on one event (a few percent of bankroll is a reasonable ceiling for a market where the typical bet loses).

**Step 6: Variance and sample size.** The standard deviation of one unit-stake bet at probability `p` and decimal odds `d` is about `d * sqrt(p * (1 - p))`. To confirm a true EV of `e` at 95% (one-sided) you need roughly

```
n = (1.645 * sd / e)^2
```

Example arithmetic with the +5000 bet above: `sd ~ 51 * sqrt(0.025 * 0.975) = 8.0`, `e = 0.275`, so `n ~ 2,350` such bets. There are four majors a year. Even ten such bets per major takes decades to confirm. Say this plainly: results over a few seasons say almost nothing about whether an outright strategy has an edge. Use model quality metrics instead (`walk-forward-validation`).

**Step 7: Closing line value, with limits.** True CLV needs a closing price. The data has an opening snapshot (the first one) and the latest pregame snapshot, which for past majors can be a week early. Comparing your price with the latest snapshot is a weak proxy, and an opening-to-latest move for a golfer shows how the market shortened or drifted, not whether you were early. If the user logs their own price and the actual closing price from their book, use those.

## Rules that books vary on

Do not assume the rules. Ask or state: withdrawal before the first round (void or lose), dead heat rules in a playoff-free tie, and whether the book pays each way. Each-way terms are not in the data.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Market for one major | 5 | one call covers every book |
| Settle a bet | 2 | `get_leaderboard` |
| EV, Kelly, sample size | 0 | local |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| "Model says 4%, price implies 2%, huge edge" | The implied 2% includes margin, and the model may be overconfident | Devig, haircut, show the EV range |
| Sum single-bet Kelly across the field | Outcomes are mutually exclusive | Joint log-growth stakes |
| Full Kelly | One miscalibrated `p` is a deep drawdown | A fraction, with a cap per event |
| Backfit `sigma` to the market, then claim agreement | Circular | Estimate it from data |
| Treat a hit as proof | One win at 30-to-1 is one data point | Report the sample math |
| Quote the best price across books as available | You need an account and balance at that book | Name the book and the snapshot time |
| Imply certainty | Variance dominates | Use "estimate", "range", "if the model is right" |

## Output Format

```
Golfer: <name>   Event: <major>   Snapshot: latest pregame (<date>)
Best price: <book> +<american> (decimal <d>), raw implied <x.x%>
Devigged market: <low%> to <high%> (proportional to Shin)
Model probability: <x.x%> (sensitivity range <low%> to <high%>), haircut to <y.y%>
EV per unit: <low> to <high>
Stake (quarter Kelly, joint, event cap <c%>): <s% of bankroll>
Note: single-event outcome; confirming this edge would take <n> comparable bets.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A candidate with positive EV range | Test the method on past majors | `backtesting` |
| EV flips sign inside the range | Pass | none |
| Edge larger than the model's uncertainty | Check calibration | `probability-calibration` |
| Want the price context | Books and movement | `odds-explorer` |
