---
name: odds-analysis
description: "Converts golf outright prices to implied probability, measures the overround of a many-runner winner market, and devigs it with the proportional, power and Shin methods. Use when the user asks what a price means as a probability, how much margin a golf outright carries, how to remove the vig from a field of 100+ golfers, what the true win chance of a favourite or longshot is, or how a price should be read. Do not use for finding the best book or movement -- see odds-explorer. Do not use for comparing with a model -- see edge-detection. Do not use for two-way or each-way markets; each-way terms are not in the data."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Odds Analysis

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_winner_odds` (5 credits) supplies prices. The method below is arithmetic you run yourself.
> With the user's own prices, no credits are used.

You are an expert in turning prices into probabilities. Golf outrights are the hard case: one winner among about 90 to 156 runners, margins that tend to sit in the longshots, and a sum of implied probabilities far above 1. Do this carefully or every downstream edge is wrong.

## When to Use

- "What is +400 as a probability?"
- "How much margin is in this market?"
- "What is Scheffler's true win probability once I take the vig out?"
- Choosing between proportional, power and Shin devigging for a big field
- Checking whether a user's model probability for a golfer is even in range

## When NOT to Use

- Finding the best book or reading movement -- see `odds-explorer`
- Model versus market -- see `edge-detection`
- Two-way markets (matchups, round bets) and each-way terms -- not in the data; the same formulas apply to the user's own two-way lines with a different normalisation

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_winner_odds` | Winner prices by golfer and book with raw implied probability | 5 |

Everything else here is calculation.

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_devigged_odds`, `get_true_probability` | Compute from `get_winner_odds` with the methods below |
| `get_each_way_terms` | Not available; do not assume terms |
| `get_odds` for non-majors | Not available |

## Step 1: Price to implied probability

American price `a`:
- positive: `p = 100 / (a + 100)`. +400 gives 0.200. +1000 gives 0.0909.
- negative: `p = |a| / (|a| + 100)`. -150 gives 0.600.

`get_winner_odds` already returns this as `implied_prob`. It is the raw probability and it includes the book's margin. It is not a belief.

Decimal odds `d = a/100 + 1` for positive `a`. Profit per unit stake `b = d - 1`.

## Step 2: Overround of the whole field

Sum the raw implied probabilities of every golfer at one book at one snapshot:

```
overround = sum(p_i) - 1
```

Real example: 2024 Masters, DraftKings latest pregame price, all 115 golfers priced.

```
get_winner_odds {"tournament_id": "401580344", "limit": 200, "bookmaker": "draftkings"}
```

```
golfers priced: 115
sum of latest implied probabilities: 1.642   (overround 64%)
sum of opening implied probabilities: 1.632
top of the board (raw): Scheffler 20.0% (+400), McIlroy 9.1% (+1000), Rahm 7.7% (+1200),
                        Koepka 5.3% (+1800), Schauffele 4.8% (+2000), Spieth 4.3% (+2200)
tail: Olazabal +500000 (0.02%)
```

A 64% overround is not a 64% hold on every bet. It is the sum of many small margins, and most of it sits in the longshots. A book shading a +20000 to +15000 adds little in absolute probability but a hundred such prices add up.

Do not report a "vig of 164%". Say: "the 115 prices sum to 1.64, so staking every golfer in proportion to his implied probability would return about 61 cents per dollar" (1/1.642 = 0.609). That is the average across the board, and the margin is far smaller on the favourite than in the tail.

## Step 3: Devig

Three methods. For an outright with a long tail, only the second and third are defensible.

**Proportional (multiplicative):** `q_i = p_i / sum(p)`. Divides every golfer by 1.642. It cuts the favourite and the longshot by the same percentage, so it understates favourites and overstates longshots when the margin is concentrated in the tail.

**Power:** find `k > 1` such that `sum(p_i^k) = 1`, then `q_i = p_i^k`. Because `p < 1`, raising to a power shrinks small probabilities more, which matches margin concentrated in longshots. Solve `k` by bisection.

**Shin:** solves for a proportion `z` of insider money and sets
`q_i = (sqrt(z^2 + 4(1 - z) p_i^2 / S) - z) / (2(1 - z))` with `S = sum(p)`, choosing `z` so `sum(q_i) = 1`. It is the usual choice when the field is large and favourite-longshot bias is visible.

Real comparison for the same market (computed from the 115 DraftKings prices):

| Golfer | Raw | Proportional | Power (k = 1.142) | Shin (z = 0.0075) |
|--------|-----|--------------|-------------------|-------------------|
| Scheffler | 20.0% | 12.2% | 15.9% | 15.3% |
| McIlroy | 9.1% | 5.5% | 6.5% | 6.8% |
| Rahm | 7.7% | 4.7% | 5.3% | 5.7% |
| Koepka | 5.3% | 3.2% | 3.5% | 3.8% |
| Schauffele | 4.8% | 2.9% | 3.1% | 3.4% |
| Spieth | 4.3% | 2.6% | 2.8% | 3.0% |

The range for Scheffler across methods is 12.2% to 15.9%. That spread is larger than most claimed edges. State it. A model that says 16% is "an edge" under proportional and "no edge" under power.

```python
import numpy as np

def devig_power(p, tol=1e-12):
    lo, hi = 1.0, 10.0
    for _ in range(200):
        k = (lo + hi) / 2
        if np.sum(p ** k) > 1: lo = k
        else: hi = k
    return p ** k, k

def devig_shin(p):
    S = p.sum()
    def total(z): return np.sum((np.sqrt(z*z + 4*(1-z)*p*p/S) - z) / (2*(1-z)))
    lo, hi = 0.0, 0.999
    for _ in range(200):
        z = (lo + hi) / 2
        if total(z) > 1: lo = z
        else: hi = z
    q = (np.sqrt(z*z + 4*(1-z)*p*p/S) - z) / (2*(1-z))
    return q, z
```

## Step 4: Use more than one book

A single book's margin is a property of that book. Devig each book separately, then average the devigged probabilities (not the American prices). A sharp book such as Pinnacle, when present, usually carries a smaller margin; check `books[]` rather than assuming. Report the spread of devigged values across books as the market's uncertainty.

## Step 5: Sanity checks before using the number

- Devigged probabilities must sum to 1 (to within 1e-6).
- Never report a probability below the smallest meaningful value for the field. A +500000 price is not a 0.02% belief; the tail is noise. Group golfers beyond rank 40 as "the field".
- A major winner prior: with 89 to 156 starters in recent majors the average golfer has roughly a 1% chance or less (1 in 89 to 1 in 156). A model giving 3% to a rank-60 player needs a reason.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Price one major at one book | 5 | `limit` 200 and `bookmaker` |
| Compare all books for the top 20 | 5 | default call |
| Devig math | 0 | local |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Treat `implied_prob` as the true probability | It includes margin | Devig the full field |
| Proportional-devig a 115-runner market and call it true | Over-credits longshots, under-credits favourites | Show power or Shin beside it |
| Devig only the top 20 golfers | The tail's mass is missing, so the sum is below the real total | Devig the whole priced field |
| Average American odds across books | Not linear | Average devigged probabilities |
| Quote one devigged number to two decimals | False precision | Quote a range across methods and books |
| Assume each-way terms | Not in the data | Ask the user |

## Output Format

```
2024 Masters, DraftKings latest pregame (115 golfers)
Raw implied sum: 1.642
Scottie Scheffler: +400 = 20.0% raw
  devigged: 12.2% proportional / 15.9% power / 15.3% Shin
  working range: 15% to 16% (power and Shin agree; proportional likely too low)
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A devigged market | Compare with a model | `edge-detection` |
| Need the prices first | Pull and compare books | `odds-explorer` |
| Want to test a rule across majors | Historical test | `backtesting` |
| Model probabilities look off | Check calibration | `probability-calibration` |
