---
name: dispatch
description: "Routes golf analytics requests to the right 2-3 skills. Load this FIRST when a golf data or betting-analytics request comes in and you are unsure which skills to activate. Prevents loading all 16 skills when only 2-3 are needed. Do not use when the request clearly names one skill's job, such as devigging a price -- load odds-analysis directly."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Skill Dispatch Guide

Match the request to a pattern below, load those skills, and stop. Always load `birdieapi-tool` alongside any skill that needs live data.

## Scope check first

BirdieAPI covers the PGA Tour, LPGA, LIV, DP World Tour and Korn Ferry Tour as historical and next-morning data. The only odds are the winner prices of the four men's majors. If the user wants live scores, tee times, weather, round or matchup odds, top-10 markets or each-way terms, say it is not in the data and offer the nearest thing that is.

## First-use persona detection

| Signal | Persona | Start With |
|--------|---------|-----------|
| "Who won last week?" / "What is on this week?" | **Explorer** | `tournament-lookup` |
| "How is Scheffler playing?" | **Scout** | `player-scouting` + `strokes-vs-field` |
| "Who should I back at the Masters?" | **Outright bettor** | `tournament-preview` + `odds-explorer` |
| "Build me a model of who wins" | **Builder** | `outright-model` + `feature-engineering` |
| "Is my model any good?" | **Validator** | `walk-forward-validation` + `probability-calibration` |
| "What does a +2000 price mean?" | **New bettor** | `odds-analysis` |

## Request patterns -> skills

### "Who won?" / "Results of the 2024 Masters" / "What is on this week?"
1. `tournament-lookup`
2. `birdieapi-tool`: `list_tournaments`, `get_schedule`, `get_leaderboard`

### "Tell me about Rory McIlroy" / "Compare Scheffler and Schauffele"
1. `player-scouting`
2. `strokes-vs-field` if the user wants form or ratings

### "Who is playing best?" / "What is a rating of 2.0?" / "Field-strength adjusted"
1. `strokes-vs-field`
2. `birdieapi-tool`: `get_ratings`, `get_player_results`

### "Who is best on par 5s?" / "Which holes play hardest?" / "Birdie rate"
1. `hole-scoring`
2. `course-fit` if a specific course is involved

### "Who plays well at Augusta?" / "Course history" / "Course fit"
1. `course-fit`
2. `hole-scoring` for the hole-level view of the course

### "Preview the PGA Championship" / "Who are the contenders?"
1. `tournament-preview`
2. `odds-explorer` for the market side
3. `course-fit` if there is time and the credit budget

### "What are the odds?" / "Which book has the best price on Scheffler?" / "How did the price move?"
1. `odds-explorer`
2. `odds-analysis` for implied probability and devigging

### "Devig this" / "What is 2000 worth as a probability?" / "Overround"
1. `odds-analysis`

### "Build a winner-probability model" / "Simulate the Open"
1. `outright-model`
2. `feature-engineering` for inputs
3. `walk-forward-validation` before trusting any output

### "Walk-forward" / "Is k-fold okay?" / "Leakage"
1. `walk-forward-validation`
2. `feature-engineering`

### "Are my probabilities calibrated?" / "Brier" / "Log loss"
1. `probability-calibration`

### "Is there an edge?" / "Kelly" / "EV on a longshot"
1. `edge-detection` (needs a model probability; if none, route to `outright-model`)
2. `odds-explorer` for the price
3. `probability-calibration` to check the probability first

### "Backtest" / "Has this worked in past majors?" / "Track my bets"
1. `backtesting`
2. `birdieapi-tool`: `get_winner_odds`

### "How do I call this?" / "What does it cost?" / "Which tool?"
1. `birdieapi-tool`

### "How does the LPGA / LIV / DP World Tour / Korn Ferry work here?"
1. `birdieapi-tool` for the `league` argument and what each tour holds
2. `tournament-lookup` or `strokes-vs-field` for the actual question
3. Remember: no hole-by-hole outside the PGA Tour and Korn Ferry Tour, no odds outside the four men's majors

### "Who will win the [major]?"
1. `tournament-preview` for the picture
2. `outright-model` for probabilities with a sensitivity range
3. `odds-explorer` for the market, then `odds-analysis` to devig it
4. Do not name a pick without the caveats from `outright-model`

## Common chains

| Goal | Chain |
|------|-------|
| Preview a major | `tournament-lookup` -> `course-fit` -> `tournament-preview` -> `odds-explorer` |
| Build and test a model | `feature-engineering` -> `outright-model` -> `walk-forward-validation` -> `probability-calibration` |
| Decide whether a price is value | `odds-explorer` -> `odds-analysis` -> `outright-model` -> `edge-detection` |
| Test a betting rule | `odds-explorer` -> `backtesting` -> `walk-forward-validation` |

## Things the data cannot answer

Say this first, then route to the nearest skill:

| Request | Not in the data | Nearest skill |
|---------|------------------|---------------|
| Live scores, tee times, weather | Next-morning data only | `tournament-lookup` for the finished rounds |
| Strokes gained off the tee, approach, putting | No shot data | `hole-scoring`, `strokes-vs-field` |
| Round, matchup or top-10 odds | Only major winner prices | `odds-explorer` |
| Each-way terms | Not held | `odds-analysis` for the outright |
| LIV team standings | Individual results only | `tournament-lookup` |

## Credit-aware routing

Before a multi-call plan, add up the credits from `birdieapi-tool` and tell the user. A preview is about 40 to 60 credits. A backtest across every major in the odds archive is one `get_winner_odds` call per major (5 credits each) plus the leaderboards (2 each).

## When NOT to Use This Guide

Single-skill requests do not need dispatch. "Devig +450 / +900 / +1200" goes straight to `odds-analysis`.
