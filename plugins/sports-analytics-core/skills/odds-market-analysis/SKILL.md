---
name: odds-market-analysis
description: "Use when the user asks what odds mean as a probability, how to convert American, decimal or fractional odds, what the bookmaker margin (vig, juice, overround) is, how to remove it (devig, no-vig line, Shin, power, multiplicative), how a line moved, or how a closing line compares with our model. Odds are treated as information about the market, never as an instruction to wager. Not for browsing current prices (use nhl-odds-explorer for hockey), not for comparing our model with the market (use market-vs-model), not for calibrating model output (use probability-calibration)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Odds and Market Analysis

Turn prices into probabilities and measure how the market moves. Odds are information about what the market thinks. This skill does not size stakes and does not recommend wagers.

## Rules for numbers

- Call your sport's SportsDataHQ MCP tools. Do not quote prices or probabilities from memory.
- Cite the tool call behind each number (for example "get_odds for game X, book Y").
- State sample size (books, games, snapshots) and the season convention.
- If prices are missing for a game or book, say "not enough data" instead of guessing.

## Data

| Need | Tool |
|------|------|
| Prices by book (moneyline, spread, total) | `get_odds` |
| Average implied and fair (no-margin) probability across books | `get_game_probabilities`, `get_prop_probabilities` |
| Opening to closing movement | `get_line_movement`, `get_prop_movement` |
| Period and alternate markets, opening and closing by book | `get_market_odds`, `get_alt_lines` |
| Past prop results against the market with sample size and interval | `get_prop_backtest` |

Examples: hockey puck line and totals, basketball spreads, football spreads and totals, baseball run lines, soccer three-way (home/draw/away), tennis and UFC two-way moneylines, golf winner prices for the majors. Availability differs by sport server; check that server's tool notes and do not invent tools such as `get_no_vig_line`. Compute those from `get_odds` using the methods below, or read the fair probability straight from `get_game_probabilities`.

For a user's own CSV, work with the file directly.

## Initial assessment

1. Which format: American, decimal or fractional?
2. Two-way market (moneyline, over/under) or three-way (soccer home/draw/away)?
3. How many books? More books give a steadier estimate.

## Format conversion

```
American -> decimal:  +150 -> 150/100 + 1 = 2.50     -180 -> 100/180 + 1 = 1.556
Decimal -> American:  2.50 -> (2.50 - 1) * 100 = +150   1.556 -> -100 / 0.556 = -180
American -> fractional: +150 -> 3/2    -180 -> 5/9
```

Raw implied probability (margin included):

```
positive American: 100 / (american + 100)     +150 -> 0.400
negative American: abs(a) / (abs(a) + 100)    -180 -> 0.643
decimal:           1 / decimal
```

## Margin (vig)

On a two-way market the raw probabilities sum to more than 1.

```
total_implied = raw_home + raw_away
margin = total_implied - 1.0
```

Example: Sabres +150 / Leafs -180 gives 0.400 + 0.643 = 1.043, a 4.3% margin. Typical ranges: main moneylines 3-6%, main totals 4-5%, player props 7-12%.

## Four ways to remove the margin

### 1. Multiplicative
Divide each raw probability by the total. Fast, assumes the margin is spread proportionally.
```
fair_i = raw_i / total_implied
```

### 2. Power
Find exponent k so that the sum of raw_i^(1/k) equals 1 (numerical solve, for example `scipy.optimize.brentq`). Better than multiplicative on lopsided markets.

### 3. Shin
Models a share z of informed money. Solve for z, then compute fair probabilities.

```python
import math
from scipy.optimize import brentq

def shin_gap(z, raw):
    return sum(p**2 / (z + (1 - z) * p) for p in raw) - 1

z = brentq(shin_gap, 0, 0.5, args=(raw_probs,))
fair = [(math.sqrt(z**2 + 4 * (1 - z) * p**2) - z) / (2 * (1 - z)) for p in raw_probs]
```
Works for three-way markets with three raw probabilities. Check that the result sums to 1. Preferred for research and for comparison with a model.

### 4. Worst case
Put all the margin on one side. Gives a bound, not an estimate.

| Method | Use | Accuracy |
|--------|-----|----------|
| Multiplicative | Quick check, balanced markets | Moderate |
| Power | Heavy favorites | Good |
| Shin | Research, model comparison | Best with several books |
| Worst case | Bounds only | Conservative |

Default: Shin. If the sport server offers `get_game_probabilities`, use its fair probability and say that is where it came from.

## Worked example

Sabres +150 / Leafs -180: raw 40.0% / 64.3% (total 104.3%).

| Method | Sabres | Leafs |
|--------|--------|-------|
| Multiplicative | 38.4% | 61.7% |
| Power | 38.5% | 61.5% |
| Shin | 38.3% | 61.7% |
| Raw | 40.0% | 64.3% |

Comparing a model against raw probabilities would compare it with a number inflated by the margin. Always use fair probability.

## No-margin line

Convert a fair probability back to American odds:
```
fair_prob > 0.5:  -100 * p / (1 - p)
fair_prob < 0.5:  +100 * (1 - p) / p
```
Fair 38.3% gives +161 / -161. A posted +150 is the price with the margin built in.

## Line movement

Pull opening and closing prices with `get_line_movement`. Report the move in fair probability points, not just in American odds, because the same cents mean different things at different prices. Movement has many causes (injury news, lineup news, volume, repositioning). Describe it, with the time and the books involved; do not claim a cause unless a tool result shows it. Lack of movement is no information.

## Closing line as a measure of model quality

The closing fair probability is the market's final estimate and a strong benchmark. To judge a model:
- Compare model log loss or Brier score with the closing fair probability's on the same games.
- Report how often the market moved toward the model's number between open and close.
- Report sample size and an interval. Under about 100 games the answer is mostly noise.

Matching the closing line is a good result. Beating it consistently is rare. This is a statement about the model, not an instruction to do anything.

## Anti-patterns

| Rationalization | Why it is wrong | Do this instead |
|-----------------|-----------------|-----------------|
| "Use the raw implied probability" | It includes the margin | Remove the margin first |
| "Multiplicative is fine on a heavy favorite" | It diverges from Shin by 1-2 points at -300 and beyond | Use Shin or the cross-book fair probability |
| "Props have the same margin as moneylines" | Props carry 7-12% | Compute the margin from the two sides each time |
| "The line moved, so informed money did it" | Movement has many causes | Describe the move; do not assign a cause without evidence |

## Output format

```
Game: [Away] at [Home]   Book: [name]   Source: get_odds
Raw odds: [A] +150 / [B] -180
Raw implied: 40.0% / 64.3% (total 104.3%, margin 4.3%)
Fair (Shin): 38.3% / 61.7%    No-margin line: +161 / -161
```

## What to do next

| Finding | Next skill |
|---------|-----------|
| Fair probability in hand, have a model | `market-vs-model` |
| Want current prices across books (hockey) | `nhl-odds-explorer` |
| Model probabilities need checking | `probability-calibration` |
| Want a historical test | `backtesting` |
| Odds term unclear | `docs/market-glossary.md` |
