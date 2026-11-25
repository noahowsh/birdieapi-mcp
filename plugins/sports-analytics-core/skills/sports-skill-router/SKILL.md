---
name: sports-skill-router
description: "Use when a sports data or analytics request comes in and it is unclear which skill to load, for example 'help me with this sports data', 'where do I start', 'what can you do with hockey stats', 'which skill handles X'. Routes the request to the right two or three skills so not all of them load. Not for answering the question itself: once routed, the chosen skill does the work. Single-skill requests (for example 'devig these odds') can go straight to odds-market-analysis without this router."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Skill Router

Match the request to a pattern below, load those skills, and stop. Do not load everything.

Data comes from your sport's SportsDataHQ MCP server (for hockey, the PuckAPI MCP server; see `nhl-puckapi-tools`). Every skill that reports numbers must call the tools, cite the call behind each number, state sample size and season convention, and say "not enough data" when it lacks data.

Odds are information only. If a request asks what to wager, explain the market and the model's view with the relevant skill; do not recommend bets or stakes.

## First-use persona detection

| Signal | Persona | Start with |
|--------|---------|-----------|
| "What games are on tonight?", exploring data | Explorer | `nhl-game-lookup` (hockey) or your sport's tools |
| "Help me build a model", "I want to predict" | Builder | `feature-engineering` + `model-building` |
| "Show me tonight's slate" | Daily user | `nhl-daily-slate` + `nhl-odds-explorer` |
| "I have a model, is it any good?" | Validator | `walk-forward-validation` + `probability-calibration` |
| "I'm new to hockey analytics" | Learner | `nhl-advanced-stats` + `nhl-research-workflow` |
| "How do odds work?" | New to odds | `odds-market-analysis` |

## Core skills (any sport)

| Request | Load |
|---------|------|
| "How do I validate my model?", "is k-fold okay?" | `walk-forward-validation` |
| "Are my probabilities calibrated?", "Brier score" | `probability-calibration` |
| "Backtest my model", "is it any good historically?" | `backtesting` (+ `walk-forward-validation`) |
| "Build features", "what features should I use?" | `feature-engineering` |
| "Train a model", "XGBoost" | `model-building` (+ `walk-forward-validation`, `feature-engineering`) |
| "Build an Elo rating" | `elo-engineering` |
| "Odds to probability", "remove the margin", "closing line" | `odds-market-analysis` |
| "How does our probability differ from the market's?" | `market-vs-model` (+ `probability-calibration`) |
| "Log my predictions", "how accurate have I been?" | `prediction-tracker` |
| "Run this daily", "pipeline", "schedule" | `data-pipeline` |
| "Show me games where...", plain-English data query | `nl-to-query` |
| "Make a chart", "calibration plot", "shot map" | `visualization` (needs output from another skill) |

Examples of sport tools these skills work with: hockey `get_shot_map`, football `get_plays`, basketball `get_shot_chart`, baseball `get_pitches`, soccer `get_events`, tennis `get_match`, golf `get_leaderboard`, UFC `get_fight`, cricket `get_deliveries`.

## Hockey skills (NHL plugin)

| Request | Load |
|---------|------|
| Who plays tonight, schedule, results, head to head | `nhl-game-lookup` |
| How a team is doing, standings, strength of schedule | `nhl-team-analysis` |
| A player's stats, comparison, prospect NHLe | `nhl-player-scouting` |
| Goalie stats, workload, who starts | `nhl-goalie-analysis` |
| Current odds across books, line movement | `nhl-odds-explorer` (+ `odds-market-analysis` for the math) |
| What is Corsi, xG, PDO | `nhl-advanced-stats` |
| Use AI to structure a hockey analysis | `nhl-research-workflow` |
| Expected goals model from play-by-play | `nhl-xg-model` |
| Over/under totals research | `nhl-totals-model` |
| Player prop research | `nhl-player-props-research` (+ `nhl-player-scouting`) |
| WAR, GAR, RAPM, player value | `nhl-war-gar` |
| Playoff or season odds simulation | `nhl-playoff-simulation` (+ `elo-engineering`) |
| Preview one game | `nhl-game-preview` |
| Tonight's full slate | `nhl-daily-slate` |
| Which endpoint to call | `nhl-puckapi-tools` |

## Reference docs

- Hockey term: `docs/hockey-glossary.md`
- Odds or market term: `docs/market-glossary.md`
- Which data tool to use: `docs/tool-routing.md`
- Date or season confusion: `docs/season-logic.md`

## When not to use this router

Single-skill requests do not need it. "Devig +150 / -180" goes straight to `odds-market-analysis`.
