---
name: odds-explorer
description: "Compares the outright winner prices of the four men's majors (Masters, PGA Championship, U.S. Open, Open Championship) across sportsbooks, finds the best price on a golfer, and reads how a price moved from the opening snapshot to the latest pregame snapshot. Use when the user asks about majors odds, who is favoured, which book has the best price, how a golfer's price changed, or a golfer's prices across majors. Do not use for converting prices or devigging -- see odds-analysis. Do not use for comparing a model with the market -- see edge-detection. Do not use for non-major tournaments, round, matchup, top-10 or each-way markets -- they are not in the data."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Odds Explorer

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_winner_odds` (5 credits per call) is the only odds tool. One call can return a whole major's field, all four majors of a season, or one golfer across the majors.

You are an expert in golf outright markets. Your goal is to show the user what the books priced, where the best number is, and how the market moved, without implying the data is a live feed.

## What is and is not in the data

- **In:** pre-tournament winner prices for the Masters, PGA Championship, U.S. Open and Open Championship, by sportsbook. Weekly snapshots from 2021 (the first seasons have fewer), plus the 2020 U.S. Open from a single snapshot. Source: The Odds API.
- **Opening** is the first snapshot a book had for that golfer. **Latest** is the last price before the first round. For past majors the latest price can be up to a week before the first tee time, so it is not a closing line.
- **Not in:** any other tournament, the LPGA, LIV or DP World Tour, round or matchup markets, finishing-position markets (top 5, top 10, top 20), in-play prices, each-way terms.
- Books seen in the data include DraftKings, FanDuel, BetMGM, Bovada, BetOnline, ESPN BET, Pinnacle and MyBookie. The set varies by golfer and year.

## When to Use

- "Who was the favourite at the 2024 Masters and at what price?"
- "Which book had the best number on Scheffler?"
- "How did McIlroy's price move into the US Open?"
- One golfer's price across every major he was priced for
- A sanity check before running `odds-analysis` or `edge-detection`

## When NOT to Use

- Implied probability, overround, devigging -- see `odds-analysis`
- A model probability versus a price -- see `edge-detection`
- Backtesting past prices -- see `backtesting`
- Non-major events -- no prices exist; ask for the user's own lines

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_winner_odds` | Winner prices by golfer and book: opening and latest pregame price with implied probability | 5 |
| `list_tournaments` | Find a major's `tournament_id` (use `major: true`) | 1 |
| `search_players` | Find a golfer's `player_id` | 1 |

`get_winner_odds` takes `tournament_id`, or `season` (all four majors), or `player_id`, optionally `major` (`masters`, `pga_championship`, `us_open`, `the_open`), `bookmaker` (e.g. `draftkings`, `pinnacle`) and `limit` (golfers per tournament, favourites first, default 20, max 200). It has no `league` argument.

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_odds`, `get_live_odds` | `get_winner_odds` (majors, pre-tournament) |
| `get_line_movement` | `get_winner_odds` returns opening and latest per book; there is no full time series |
| `get_closing_line` | The latest pregame snapshot is the nearest thing; label it as such |
| `get_matchup_odds`, `get_top_10_odds`, `get_round_odds` | Not available |
| `get_best_book` | Compare the `books[]` array yourself |

## How It Works

**Step 1: Get the id.**

```
list_tournaments {"season": 2024, "major": true}
```

**Step 2: Pull the market.** For a whole field, favourites first:

```
get_winner_odds {"tournament_id": "401580344", "limit": 5}
```

Real response (trimmed): `snapshots 51`, `first_captured_at 2023-04-21`, `last_captured_at 2024-04-05`, `golfers_priced 121`. Each golfer has `median_implied_prob_opening`, `median_implied_prob_latest` and `books[]`. Each book has `opening` and `latest_pregame`, each with `price` (American, positive for longshots), `implied_prob` and `captured_at`, and `snapshots`.

For Scottie Scheffler at the 2024 Masters:

```
betmgm      open +900  (10.0%)  latest +400 (20.0%)
betonlineag open +1000 (9.1%)   latest +400 (20.0%)
draftkings  open +900  (10.0%)  latest +400 (20.0%)
fanduel     open +700  (12.5%)  latest +430 (18.9%)
pinnacle    open +1022 (8.9%)   latest +407 (19.7%)
```

**Step 3: One book, or one golfer.**

```
get_winner_odds {"tournament_id": "401580344", "limit": 1, "bookmaker": "pinnacle"}
get_winner_odds {"player_id": "9478"}
```

**Step 4: Find the best price.** For a golfer, the best number at a given snapshot is the highest American price (a +430 beats a +400). Compare the `latest_pregame.price` across `books[]`. Report the spread, not only the best: FanDuel +430 versus +400 elsewhere is a real difference (18.9% versus 20.0% implied).

**Step 5: Read movement.** Compare `opening` with `latest_pregame` per book.
- Shortening (+900 to +400) means the implied probability rose from 10.0% to 20.0%.
- Opening dates differ by book (April 2023 for most, October 2023 for Pinnacle in this example). Do not compare an opening price at one book with an opening at another as if they were the same date; use `captured_at`.
- A weekly snapshot cannot show intra-week or steam moves. Do not claim sharp action from it.

**Step 6: Count snapshots.** `snapshots` per book tells you how dense the series is. Fewer than ten means the movement read is coarse.

## Practical notes on outrights

- Long shots carry the most margin. The 2024 Masters DraftKings latest prices for 115 golfers summed to a raw implied probability of 1.64 (see `odds-analysis`). Do not read a +50000 price as a 0.2% belief.
- The `median_implied_prob_*` fields are the median across books. The median hides a book that is an outlier; check `books[]` when it matters.
- A golfer can be priced at a book and absent at another. Missing is not zero.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| One major, all golfers | 5 | `limit` does not change the cost |
| All four majors of a season | 5 | one call with `season` |
| One golfer across majors | 5 | `player_id` |
| Id lookups | 1 each | |

A full pre-tournament scan of one major is about 6 to 8 credits including lookups.

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Call the latest price the closing line | Up to a week before first tee for past majors | Say "latest pregame snapshot" |
| Say "the books have him at 20%" | 20.0% is the raw implied probability including margin | Devig first (`odds-analysis`) |
| Look for top-10 or matchup prices | Not held | Ask for the user's own lines |
| Infer sharp money from a weekly series | Weekly snapshots cannot show timing | Describe the move and the dates only |
| Average prices across books to get the "market" | Averaging American odds is wrong | Average implied probabilities, or use the median field |

## Output Format

```
2024 Masters, winner market, latest pregame snapshot (5 Apr 2024)
Scottie Scheffler: +400 at BetMGM, BetOnline, DraftKings, Bovada; +430 at FanDuel (best); +407 Pinnacle
Move since first snapshot: +900 to +400 at DraftKings (10.0% to 20.0% raw implied)
Snapshots: 48 (DraftKings). Raw implied probabilities include margin.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A price to convert or devig | True probabilities | `odds-analysis` |
| A model probability | Edge and sizing | `edge-detection` |
| Want the field context | Form and course record | `tournament-preview` |
| Want to test a rule on past majors | Historical test | `backtesting` |
