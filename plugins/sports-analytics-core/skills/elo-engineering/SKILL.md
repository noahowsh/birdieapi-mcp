---
name: elo-engineering
description: "Use when the user asks to build Elo ratings, rate teams or players, tune K-factor or home advantage, carry ratings across seasons, add margin-of-victory, or mentions Fading, Form or Component Elo. Works for team sports and for tennis, golf, UFC and cricket player or fighter ratings. Not for general feature construction (use feature-engineering), not for a full model (use model-building), not for plain team stats (use nhl-team-analysis for hockey or your sport's stats tools), not for season simulation (use nhl-playoff-simulation)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Elo Engineering

You are an expert in Elo rating construction. The goal is to build, tune and export multi-variant Elo systems that serve as model features or as standalone win-probability estimates.

## Data

Call your sport's SportsDataHQ MCP tools for historical results: get_games or list_games (hockey, football, basketball, baseball, soccer), get_matches (tennis), get_event and get_fighter_fights (UFC), get_leaderboard (golf), get_schedule where a server has no games list. Several servers also expose their own ratings (get_ratings); those are the server's published ratings, useful as a cross-check against your own build, not a substitute for it.

Own data: required columns are game_id, date, home_team, away_team, home_score, away_score. Sort ascending by date. Flag games with missing scores; do not silently drop.

## Rules for numbers

- Call the tools. Never recall results or ratings from memory.
- Cite which tool call supplied the games behind each rating table.
- State the sample size (games processed per team) and the season convention (2025 = which season) used for carryover.
- If a team or player has too few games for a stable rating, say "not enough data" and mark the rating provisional.

## When to Use

- Build an Elo rating system from scratch
- Add Elo-based features to an existing model
- Tune K-factor, home advantage or season regression
- Track team momentum or recent form
- Separate offensive and defensive strength ratings

## When NOT to Use

- Non-Elo features: use `feature-engineering`
- Comparing team stats without ratings: use `nhl-team-analysis` (hockey) or your sport's stats tools
- Training a full prediction model: use `model-building`
- Season simulations: use `nhl-playoff-simulation` (hockey)

## Initial Assessment

Before building, establish:
1. Which sport? (determines K-factor, HFA, carryover defaults; see `parameter-reference.md`)
2. How many seasons of history are available?
3. Single Elo variant or all 5? (all 5 recommended for model features)
4. Team sport (home/away) or individual sport (two competitors, surface or venue effects)?

## The 5 Variants

### 1. Standard Elo

The baseline. Ratings update after every game based on expected vs actual outcome.

```
expected_home = 1 / (1 + 10^((away_elo - home_elo - HFA) / 400))
new_home_elo = home_elo + K * MOV_multiplier * (actual - expected_home)
new_away_elo = away_elo + K * MOV_multiplier * ((1 - actual) - (1 - expected_home))
```

- `actual` = 1 (home win), 0 (away win), 0.5 (tie/OT loss handled by sport)
- `HFA` = home field advantage in Elo points (hockey default: 35; see parameter-reference.md for other sports)
- Initialize all teams at 1500

### 2. Fading Elo

Recent performance weighted more heavily via exponential decay. Useful when teams change significantly mid-season (trades, injuries).

```
weight = exp(-decay_rate * days_since_game)
weighted_K = K * weight
```

- Typical decay rate: 0.003-0.007 (tune via grid search)
- Apply the weighted K in place of standard K during update
- Higher decay = older games matter less

### 3. Form Elo

Short-term momentum. Only the last N games (default N=5, test N=7 and N=10) contribute to the rating. Ratings reset to a baseline each calculation.

**Process:**
1. For each team, take only their last N game results
2. Start from a shared baseline (league average at that date)
3. Apply standard Elo updates in chronological order
4. Output is a "form rating," not cumulative

- Best combined with Standard Elo as a second feature (captures different signal)
- Sensitive to N: run sensitivity across 5/7/10, keep all three in feature set initially

### 4. Component Elo

Separate offense and defense ratings per team. Offensive rating updates based on goals scored vs expected; defensive rating updates based on goals allowed vs expected.

```
expected_goals_for = f(home_off_elo, away_def_elo, HFA_goals)
off_update = K_component * (actual_goals_for - expected_goals_for)
def_update = K_component * (actual_goals_against - expected_goals_against)
```

- Requires scoring data from the games list or team stats tools
- K_component is typically smaller than standard K (hockey: 6-8)
- Outputs 4 ratings per team: home_off, home_def, away_off, away_def
- Combine into win probability: use logistic function on (home_off + away_def) - (away_off + home_def)

### 5. Flat-K Elo

Standard Elo with fixed K-factor: no margin-of-victory adjustment, no adaptation. Simpler and sometimes competitive when training data is limited.

```
new_elo = elo + K_flat * (actual - expected)
```

- K_flat is constant regardless of score margin
- Use as a baseline sanity check: if your tuned variants don't beat Flat-K, something is wrong
- Tune K_flat separately from Standard K (often 15-25 range)

## Margin-of-Victory Adjustment

Apply to Standard, Fading, and Component variants. Prevents a blowout from moving ratings far more than a narrow win when the true gap is already large.

```
MOV_multiplier = ln(abs(score_diff) + 1) * (2.2 / (win_elo_diff * 0.001 + 2.2))
```

- `score_diff` = absolute goal/point difference
- `win_elo_diff` = winner's Elo - loser's Elo before the game
- Cap MOV_multiplier at 1.8 to prevent extreme blowouts from dominating
- Do NOT apply to Form Elo (defeats the purpose of recency weighting)
- Do NOT apply to Flat-K Elo (it's intentionally simple)

## Tuning Process

Grid search to minimize log loss on held-out historical data.

**Parameters to tune (Standard Elo):**
- K-factor: test [5, 10, 15, 20, 25]
- HFA: test a range around the sport's default in parameter-reference.md (hockey: 20 to 80)
- MOV cap: test [1.5, 1.8, 2.0]

**Process:**
1. Train on seasons 1 through N-2
2. Validate on season N-1 (never season N, which is future data)
3. Report log loss and Brier score on validation set
4. Pick params with lowest log loss; break ties by Brier score
5. Retrain on seasons 1 through N-1, apply to current season

See `parameter-reference.md` for published starting points by sport.

## Season Carryover

At the start of each new season, blend each team's end-of-season rating toward 1500 (league mean). This accounts for roster turnover and regression to the mean.

```
new_season_elo = carryover * end_elo + (1 - carryover) * 1500
```

- Hockey carryover: 0.88 (12% regression)
- Higher regression for sports with more offseason change (see `parameter-reference.md` for other sports)

**Expansion teams:** Initialize at 1380-1400 (below mean) to reflect unknown quality.

## Season/Date Logic

- Process games in strict chronological order. Never process future games.
- "Current ratings" = ratings as of yesterday, using games through yesterday only
- When building features for a model: rating used for game on date D must be computed from games through D-1 (no leakage)
- Off-season: ratings stay frozen at end-of-season values until carryover is applied on opening day

## Anti-patterns

| Rationalization | Why It's Wrong | Do This Instead |
|----------------|---------------|-----------------|
| "Initialize all teams at 1000 for simplicity" | Scale doesn't matter, but 1500 is conventional and matches published benchmarks you'll want to compare against | Use 1500. Deviation gains nothing. |
| "Use the same K for all sports" | Sports differ in games per season and score variance. K must reflect both. | Use sport-specific defaults in parameter-reference.md. Tune from there. |
| "Skip MOV adjustment to keep it simple" | Without MOV, a 6-1 blowout and a 2-1 win shift ratings identically. Signal is lost. | Implement the logarithmic MOV multiplier. It's 3 lines of code. |
| "One Elo variant is enough" | Each variant captures different signal; Standard and Form are often the two most useful. | Build all 5. Use feature selection to prune later if needed. |
| "Don't regress ratings between seasons" | Last season's best team is not the same team this season. Over-confident carry-forward pollutes predictions. | Apply carryover. Hockey uses 0.88 (12% regression); sports with more roster churn regress more. |
| "Use end-of-season ratings for next season's opening day" | Without regression, teams that had lucky seasons stay overrated. | Apply carryover formula on day 1 of the new season. |

## Output Format

For each variant, produce a ratings table:

```
team         | elo_standard | elo_fading | elo_form | elo_off | elo_def | elo_flat | as_of_date
-------------|-------------|------------|----------|---------|---------|----------|----------
Team A| 1487.3      | 1491.2     | 1502.1   | 1495.6  | 1478.9  | 1489.1   | 2026-05-01
Team B | 1534.8      | 1529.4     | 1518.7   | 1541.2  | 1528.3  | 1532.0   | 2026-05-01
```

For model features: output as one row per game with home/away ratings as of game date.

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Elo variants built, ready to add to model | Combine with other features | `feature-engineering` |
| Ratings built, want a full model | Train on Elo + other features | `model-building` |
| Model trained, need to verify calibration | Check probability output quality | `probability-calibration` |
| Want to simulate playoff bracket | Use Elo to seed simulations | `nhl-playoff-simulation` |
| Elo accuracy unclear | Backtest against the market's no-margin probabilities | `backtesting` |

## Credits

- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
