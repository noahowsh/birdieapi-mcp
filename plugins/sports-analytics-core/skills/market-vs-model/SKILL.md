---
name: market-vs-model
description: "Use when the user compares their own model's numbers with the betting market, for any sport, in plain wording: 'where do we disagree with the market', 'who does the book like more than my model', 'does my model have an edge on the close', 'rank tonight's games by the gap', 'our price vs fair price', 'is the market higher on them than my numbers', 'how big a gap is real', 'gap between us and closing lines'. Use this whenever a model probability sits next to a market probability. Load it for short fragments and follow-ups too, instead of answering from memory or going straight to the raw tools. Covers the model vs no-margin market gap, closing-line comparison and how large a sample must be before a gap means anything. Odds are information only: no stakes, no picks. Not for odds math (see odds-market-analysis), raw price lookups, historical accuracy (see backtesting) or calibration (see probability-calibration)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Model vs Market

Compare the probability our model gives an outcome with the probability the market implies. This skill reports how the two differ and whether the model's view tends to be right. It does not tell anyone to wager and it does not size stakes. Odds are information.

## Rules for numbers

- Call your sport's SportsDataHQ MCP tools. Do not answer from memory.
- Cite the tool call behind each number (for example "get_game_probabilities, game X").
- State the sample size and the season convention (calendar year, or the year the season starts or ends; check your sport's tool notes).
- If there is not enough data, say "not enough data" instead of guessing.
- Never present a past result as a pick or a prediction of what to do next.

## Data

| Need | Tool (any sport server that offers it) |
|------|------------------------------------------|
| Market probability, implied and fair (no-margin), averaged across books | `get_game_probabilities`, `get_prop_probabilities` |
| Prices by book | `get_odds` |
| Opening to closing movement | `get_line_movement`, `get_prop_movement` |
| Period and alternate markets | `get_market_odds`, `get_alt_lines` |
| How a kind of prop did against the market, with sample size and interval | `get_prop_backtest` |
| Our model's probability | the sport's prediction tool (for hockey, `get_predictions`), or the user's own file |

Examples by sport: hockey `get_game_probabilities` for an NHL game, basketball `get_game_probabilities` for an NBA game, soccer `get_game_probabilities` for home/draw/away, tennis and UFC `get_odds` for the two-way moneyline, golf `get_winner_odds` for majors.

Not every tool exists on every server. If a tool is missing, say so and use the closest one listed in that server's tool notes. Do not invent tools such as `get_ev` or `get_clv`.

User-supplied files: require `game_id`, `model_prob`, and market odds (American or decimal). Check model probabilities are in [0, 1] and sum to about 1 per game. Warn if they were not calibrated (see `probability-calibration`), because gaps from uncalibrated probabilities are unreliable.

## How it works

### Step 1: Market probability without the margin

Convert each price to implied probability, then remove the margin to get the fair probability (see `odds-market-analysis`). Prefer the fair probability from `get_game_probabilities`, which averages across books. Show both the raw implied and the fair number.

### Step 2: The model vs market gap

```python
gap = model_prob - market_fair_prob   # in percentage points
```

Report per outcome: model probability, market fair probability, gap. A positive gap means our model rates the outcome higher than the market does.

Read gaps with care:
- A gap under about 3 points is within typical calibration error. Say so.
- A gap over about 10 points is far more often a model error or missing information (injury, lineup, starter) than a true difference. Check calibration and inputs first.
- Compare against several books and the average, not one price. A gap that exists against one book only is a book difference, not a model view.

### Step 3: Rank a slate by gap

Sort games by absolute gap. Present as "where our model differs most from the market", with the likely reason (rest, starter, injuries) taken from tool output. Frame it as a list of disagreements to investigate, not a list of things to do.

### Step 4: Closing-line comparison (model quality)

The closing line is the market's best final estimate. If the model's probabilities move toward the closing fair probability more often than away from it, the model is picking up real information.

```python
# for each prediction: model_prob, open_fair, close_fair
moved_toward_model = (abs(close_fair - model_prob) < abs(open_fair - model_prob))
share = moved_toward_model.mean()
```

Pull `get_line_movement` for opening and closing prices. Report the share, the sample size and an interval. Sustained movement toward the model over 100+ predictions is a good sign. Near 50% means the model adds little beyond the market. Consistently away means the market knows something the model does not.

Also compare log loss or Brier score of the model against the market's closing fair probability on the same games (see `prediction-tracker` and `backtesting`). The market is a hard benchmark; matching it is a good result.

### Step 5: How big a sample is enough

At small samples, apparent differences are noise. For a hit rate p over n predictions, the 95% interval is about p +/- 1.96 * sqrt(p(1-p)/n). With n = 40 that is roughly 15 points wide each way at p = 0.5. Do not call a pattern real unless the interval excludes the benchmark. For historical tests, use `get_prop_backtest` where it exists: report its sample size, interval and by_season breakdown, and say that a past result is not a forecast.

## Anti-patterns

| Rationalization | Why it is wrong | Do this instead |
|-----------------|-----------------|-----------------|
| "The model says 65% and the market says 55%, so the model found something" | A 10-point gap is usually a calibration or input error | Check calibration and lineup information first |
| "The line has not moved, so the market agrees with us" | No movement is silence, not agreement | Treat movement as signal and absence of movement as no information |
| "Our hit rate is 60%" | A rate without sample size and odds context says little | Report n, interval, and the market's own rate on the same games |
| "One book differs, so the model is right" | A single book can be stale | Compare to the cross-book fair probability |
| "Recent results confirm the gap" | Small samples mislead | Report by-season results and the interval |

## Output format

```
MODEL VS MARKET: [Date]  (season convention: [..])

[Home] vs [Away]
Our probability:        [X.X%]  (source: [tool or file])
Market, implied:        [X.X%]  (get_odds, [book])
Market, fair:           [X.X%]  (get_game_probabilities)
Gap (model - market):   [+/-X.X points]
Context:                [injury, starter, rest notes from tools]

SLATE SUMMARY
Games compared: N   Median absolute gap: X.X points
Largest gaps: [list]
```

## What to do next

| Finding | Next skill |
|---------|-----------|
| Need odds converted or margin removed | `odds-market-analysis` |
| Probabilities look off | `probability-calibration` |
| Want to log predictions and grade them | `prediction-tracker` |
| Want historical validation | `backtesting` or `walk-forward-validation` |
| Hockey slate view | `nhl-daily-slate` |

## Credits

- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
