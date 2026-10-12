---
name: backtesting
description: "Tests golf outright betting rules on past majors using BirdieAPI's winner prices and results: strategy simulation, ROI with bootstrap intervals, price-movement analysis, bet-log structure and the limits of a sample of about two dozen majors. Use when the user asks whether a rule would have made money on past majors, whether favourites or longshots were mispriced, how a price moved into the first round, or how to log and review their own bets. Do not use for building the model -- see outright-model. Do not use for proper out-of-sample splits of a model -- see walk-forward-validation. Do not use for live pricing -- see odds-explorer."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Backtesting

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_winner_odds` (5 credits) with `season` returns all four majors of a season in one call. `get_leaderboard` (2) settles each event. `list_tournaments` (1) finds ids and the winner.

You are an expert in testing betting rules against history without fooling anyone, including the user and yourself. With about two dozen majors in the price archive, most backtests of outright strategies are anecdotes. Your goal is to run them anyway, report the uncertainty at full size, and keep the user from over-reading the result.

## What the data supports

- Winner prices for the Masters, PGA Championship, U.S. Open and Open Championship from 2021, plus the 2020 U.S. Open from a single snapshot. Weekly snapshots, then daily (every six hours in tournament week) while a major's market is open.
- Per book: the opening price (first snapshot) and the latest pregame price. For past majors the latest price can be up to a week before the first tee time.
- Not available: other tournaments, round or matchup markets, top-N markets, in-play, each-way terms, a true closing price.
- Outcomes: `winner_id` from `list_tournaments` or position from `get_leaderboard`.

## When to Use

- "Would backing every pre-tournament favourite have made money?"
- "Did the market underprice players ranked top 5 by rating?"
- "How did Scheffler's price move across the 2025 majors?"
- "How should I log my bets so I can review them?"

## When NOT to Use

- Building the probability -- see `outright-model`
- Time-ordered model validation -- see `walk-forward-validation`
- Current prices -- see `odds-explorer`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_winner_odds` | Prices for all four majors of `season`, or one `tournament_id`, or one `player_id` across majors | 5 |
| `list_tournaments` | Majors only with `major: true`; winner and id | 1 |
| `get_leaderboard` | Result and positions | 2 |
| `get_ratings` | Point-in-time ratings (`as_of`) for rating-based rules | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_historical_odds` for non-majors | Not available |
| `get_closing_line` | The latest pregame snapshot, with the timing caveat |
| `get_line_movement` | Opening and latest per book from `get_winner_odds` only |
| `get_bet_history`, `get_results_for_bets` | Keep the user's bet log yourself |

## How It Works

**Step 1: Pull every major.** One call per season gives four majors:

```
get_winner_odds {"season": 2025, "limit": 200}
```

Real response (limit 1, season 2025): four tournaments (Masters, PGA Championship, U.S. Open, The Open), each with `snapshots` (47, 49, 27, 32), `golfers_priced` (125, 197, 197, 202) and the favourite, Scottie Scheffler, with latest median implied probability 18.2%, 18.2%, 26.7% and 17.5%. Repeat for 2021 through the latest completed season. Season 2021 holds six majors because it includes the 2020 U.S. Open and the November 2020 Masters.

Cost: six seasons at 5 credits is 30 credits.

**Step 2: Settle.** The winner of each major is `winner_id` in the `list_tournaments` row. For golfers with no match in the price list, the bet was never available; do not invent one.

**Step 3: Define the rule before looking at results.** Examples:
- Back the pre-event favourite at the best latest price.
- Back every golfer in the rating top 5 whose devigged price is above their rating-model probability.
- Back the golfer whose price shortened most from opening to latest.

Write the rule, the stake, the price source (a named book, or the best across books) and the price time (latest pregame) in the log before running it.

**Step 4: Simulate flat staking.**

```python
def settle(bets):
    # bets: list of dicts: event, player_id, decimal_odds, stake, won (bool)
    pnl = [b["stake"] * (b["decimal_odds"] - 1) if b["won"] else -b["stake"] for b in bets]
    staked = sum(b["stake"] for b in bets)
    return sum(pnl), sum(pnl) / staked, len(bets)
```

Convert the book's American `price` to decimal: `d = price/100 + 1` for positive prices.

**Step 5: Put an interval on it.** Resample events, not bets:

```python
import numpy as np
rng = np.random.default_rng(1)
def bootstrap_roi(per_event_pnl, per_event_staked, n=10000):
    k = len(per_event_pnl); out = []
    for _ in range(n):
        idx = rng.integers(0, k, k)
        out.append(per_event_pnl[idx].sum() / per_event_staked[idx].sum())
    return np.percentile(out, [5, 50, 95])
```

With about two dozen events, one winner at a long price moves the whole ROI. A 90% interval from -100% to +300% is a normal result, not a failure of the method. Report it as such.

**Step 6: Price movement, descriptive only.** For each major, compare `opening` and `latest_pregame` for the favourite and the top ten. The question "did shortening predict winning" has about two dozen outcomes. Report the table and do not fit a rule.

**Step 7: Stale latest price.** Latest can be a week before the first tee. A rule that assumes you could have bought that price on Thursday morning is optimistic. Report results at the latest snapshot and say what that means.

**Step 8: Selection and look-ahead.**
- Use ratings `as_of` the day before round 1, not today's.
- Do not pick the "best book" per golfer using information that only exists after the fact; pick at the snapshot.
- If you test ten rules and report the best, you have fit the noise. Count the rules tried and adjust your expectations accordingly.

## Logging real bets (bet tracker)

Keep a flat log so results can be reviewed honestly. One row per bet:

| Column | Meaning |
|--------|---------|
| `placed_at` | timestamp |
| `event` | tournament name and `tournament_id` |
| `player_id` | from `search_players` |
| `book`, `american_price`, `stake` | what you took |
| `model_prob`, `devig_market_prob` | at the time, with the method used |
| `closing_price` | the book's own closing price if you can get it |
| `result` | win, lose, void (withdrawal), dead heat |
| `notes` | rule that triggered the bet |

Review quarterly, not after each event. Report: bets, units staked, units won, ROI, average price, and the price versus the book's closing price. If the sample is small, say that nothing can be concluded.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| All majors 2021-2026 prices | 30 | six `season` calls |
| Winners and ids | 6 | one `list_tournaments` call per season with `major: true` |
| Ratings at each event date (26) | 52 | rating rules |
| Leaderboards to settle (optional) | 52 | the winner is in `list_tournaments` |
| Full study with ratings | about 90 | inside the free monthly 500 |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Report "favourites returned +X%" from 25 events | One result moves it | Show the bootstrap interval |
| Call the latest price the closing line | Up to a week early | "latest pregame snapshot" |
| Use today's rating | Leakage | `as_of` |
| Test many rules, show the best | Multiple comparisons | Pre-register, count tries |
| Assume each-way terms | Not in the data | State outright-only |
| Treat unavailable golfers as lost bets | Never priced | Exclude, and count |
| Promise a result | Variance | "If the pattern holds, which about two dozen events cannot show" |

## Output Format

```
Backtest: favourite at best latest pregame price, 2021-2025 majors (N = <events>)
Staked <units>, returned <units>, ROI <x%>. Winners among favourites: <k> of <N>.
Bootstrap 90% interval over events: <low%> to <high%>.
Caveats: latest price up to a week pre-tee; 25 events cannot distinguish skill from luck.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A rule worth keeping | Re-test with a held-out season | `walk-forward-validation` |
| A probability model behind it | Check reliability | `probability-calibration` |
| Want to price next major | Current prices | `odds-explorer` |
