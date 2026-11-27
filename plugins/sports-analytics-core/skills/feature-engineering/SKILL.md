---
name: feature-engineering
description: "Use when the user asks to prepare data for a model, build rolling averages or recent-form features, add rest days or back-to-back flags, adjust for strength of schedule, build starter or goalkeeper quality features, use Elo as an input, or check features for leakage. Enforces shift(1) before any rolling calculation. Not for looking up raw stats (call get_games, get_standings or get_team_stats), not for explaining hockey metrics (use nhl-advanced-stats), not for expected goals features (use nhl-xg-model), not for training (use model-building)."
metadata:
  version: 2.2.0
  author: SportsDataHQ
---

# Feature Engineering

You are an expert in sports feature engineering. The goal is to build model-ready features from raw data while guaranteeing zero temporal leakage. This is where most first models go wrong.

## Data

Call your sport's SportsDataHQ MCP tools. Hockey: get_games, get_team_stats, get_goalie_stats, get_head_to_head. Football: get_games, get_team_stats, get_plays. Basketball: list_games, get_team_stats, get_shot_chart. Baseball: get_games, get_team_stats, get_pitches. Soccer: list_games, get_team_stats, get_events. Tennis: get_matches, get_surface_splits. Golf: get_leaderboard, get_player_results. UFC: get_fighter_fights. Cricket: get_deliveries. Read your server's tool list for exact names.

Derived features have no tool of their own (rolling stats, rest days, strength of schedule, recent starter form): compute them from the game log.

Own data (CSV or JSON): verify game_date, home and away identifiers, result columns and stat columns; ISO 8601 dates; flag missing rows, do not silently drop.

## Rules for numbers

- Call the tools. Never fill a feature value from memory.
- Cite which tool call supplied each feature's source data (tool plus arguments).
- State the sample size behind every feature (games in the window, games in the training set) and the season convention the server uses.
- Where history is too short for a window, mark the feature missing and say "not enough data". Do not guess a value.

## When to Use

- Prepare data for a prediction model
- Rolling windows, moving averages, recent form
- Home and away splits, rest days, back-to-backs
- Strength-of-schedule adjustment
- Starter quality (goalie, pitcher, goalkeeper, quarterback)
- Elo ratings as model features
- Opponent-adjusted metrics

## When NOT to Use

- Raw lookups: call `get_games`, `get_standings` or `get_team_stats` (hockey) or your sport's stats tools
- What Corsi, Fenwick or PDO mean: use `nhl-advanced-stats`
- Expected goals features: use `nhl-xg-model`
- Training or evaluating the model: use `model-building` and `walk-forward-validation`

## Initial Assessment

1. Prediction target: win or loss, margin, total, or a player stat?
2. Data available: game logs, team stats, starter or player data?
3. History depth (seasons available fixes the valid window sizes)

## How It Works

### Step 0: Establish Temporal Ordering

Sort all data ascending by `game_date`. This is non-negotiable. Every calculation that follows depends on correct order. Verify sort before proceeding.

### Step 1: Apply `.shift(1)` Before ANY Rolling Calculation

**The single most important rule in this skill.**

For every stat column that will enter a rolling window:
```python
df['stat_shifted'] = df.groupby('team_id')['stat'].shift(1)
```

This ensures game N uses only games 1 through N-1. Without `.shift(1)`, game N includes its own outcome in its own feature, which is leakage.

Even season-level aggregate stats must be lagged. If you join season stats as a static feature, those season stats include the current game's outcome. Lag them.

### Step 2: Rolling Window Statistics

Compute rolling windows at multiple sizes. The "right" window is an empirical question, not a convention.

Required windows to test: **5, 10, 20, 40, 82 games**

```python
for window in [5, 10, 20, 40, 82]:
    df[f'goals_for_roll{window}'] = (
        df.groupby('team_id')['goals_for_shifted']
        .transform(lambda x: x.rolling(window, min_periods=window//2).mean())
    )
```

Run sensitivity analysis: does the model's walk-forward accuracy change meaningfully when you swap window sizes? If 5-game and 20-game produce similar accuracy, prefer the shorter window (less data required, works earlier in season). Document which window was chosen and why.

### Step 3: Home/Away Splits and Rest-Day Features

Compute all features separately for home context and away context. A team's road performance is a different signal than home performance.

**Rest-day feature:**
```python
df['rest_days'] = df.groupby('team_id')['game_date'].diff().dt.days - 1
df['back_to_back'] = (df['rest_days'] == 0).astype(int)
df['rest_bucket'] = pd.cut(df['rest_days'], bins=[-1, 0, 1, 2, 99],
                            labels=['b2b', '1day', '2day', '3plus'])
```

Back-to-backs carry a measurable performance cost in hockey and basketball. Measure the size in your own data (with the sample size) and include the feature wherever the schedule allows it.

### Step 4: Strength of Schedule Adjustment (Iterative)

Simple opponent win% is not SOS. It double-counts easy schedules. Use iterative SOS:

1. Initialize each team's strength rating as their win%
2. Each team's SOS = mean(opponents' current strength ratings)
3. Each team's adjusted rating = f(own record, SOS)
4. Repeat steps 2-3 until ratings converge (typically 10-20 iterations)

Do NOT use simple opponent win% as SOS. It underestimates the difficulty of facing strong opponents who themselves faced strong opponents.

Pull opponent records via `get_standings`. Recompute per-fold in walk-forward validation. Never use full-season SOS as a feature (that leaks final standings into early-season predictions).

### Step 5: Starter Quality Features (hockey example)

In hockey the starting goalie is a large source of game-to-game variance. The same idea applies to a starting pitcher (baseball), goalkeeper (soccer) or quarterback (football). Hockey features:

- **Starter SV%** (season to date, lagged): from `get_goalie_stats`
- **Recent form SV%** (last 5 starts, lagged): rolling on starts, not games
- **GSAA (Goals Saved Above Average)** (season to date, lagged): measures goalie quality net of shot quality
- **Confirmed starter flag**: 1 if starter announced, 0 if uncertain

```python
# GSAA formula: (league_avg_sv_pct - goalie_sv_pct) * shots_faced_against
# Negative GSAA = goalie is below average (worse than expected)
```

### Step 6: Elo Ratings as Features

Reference `elo-engineering` skill for Elo calculation details. As a feature input:

- Use **pre-game Elo** (before the game's result updates the rating)
- Elo difference (home_elo - away_elo) is often more predictive than raw Elo values
- Elo captures recent form implicitly, so no need to separately include win streak if Elo is in the model

### Step 7: Opponent-Adjusted Metrics

Raw goals-for is partially a function of opponent quality. Subtract opponent average:

```python
df['adj_goals_for'] = df['goals_for_roll10'] - df['opp_goals_against_roll10']
```

This isolates the team's contribution from the matchup context. Using home-minus-away differences for every feature encodes opponent context directly.

### Step 8: Construct Home-Minus-Away Differences

For matchup prediction, compute the difference between home team feature and away team feature:

```python
df['goal_diff_feature'] = df['home_goals_for_roll10'] - df['away_goals_for_roll10']
```

All features become single signed values. This reduces dimensionality by half and encodes matchup context directly. Confirm on your own walk-forward folds that the differenced form does at least as well.

### Step 9: Leakage Audit

Before handing features to `model-building`, audit every feature:

1. Does it use data from the game being predicted? -> Leakage
2. Does it use data from after the game being predicted? -> Leakage
3. Was `.shift(1)` applied before any rolling calculation? -> If no, leakage
4. Were season-level stats lagged? -> If no, leakage
5. Is a model value (xG, expected points, win probability) fitted on all history? -> Leakage in a backtest. Soccer has `xg_point_in_time` (get_events, get_shot_map) and basketball has `expected_points_point_in_time` (get_plays, get_shot_chart), each fitted only on earlier seasons: use them instead of `xg` and `expected_points`.

See `feature-catalog.md` for the full recommended feature list with leakage risk ratings.

## Anti-patterns

| Rationalization | Why It's Wrong | Do This Instead |
|----------------|---------------|-----------------|
| "k-fold is fine for feature selection" | k-fold on time series leaks future folds into training, inflating feature importance scores by 5-15% | Use walk-forward fold structure for all feature selection |
| "40-game window is standard" | 40 is arbitrary; the right window depends on your data | Test 5/10/20/40/82 windows, report sensitivity, pick empirically |
| "Elo is redundant with rolling win%" | Elo updates after every game and weights recent games more; win% is equally weighted across the season | Include Elo; it captures momentum that win% misses |
| "Don't need .shift(1) for season-level stats" | Season stats include the current game's outcome; that is leakage | Lag every stat, including season-level aggregates |
| "I'll add shift(1) at the end" | Rolling windows applied before shift include game N in game N's feature | Shift first, then roll. Order is not flexible. |
| "Opponent win% is a fine SOS proxy" | Simple opponent win% double-counts easy schedules | Use iterative SOS: run convergence loop on opponent ratings |
| "More features can't hurt" | More features increase overfitting risk in small sports datasets | Use feature importance from walk-forward folds to prune aggressively |
| "I'll just use this season's stats for the whole season" | Future games in the season leak into early-season features | Rebuild SOS and aggregate stats per fold in walk-forward |

## Output Format

Feature engineering produces:

1. **Feature matrix** (`X`): rows = games, columns = home-minus-away feature differences. All numeric. No nulls (handle early-season NaN with fill strategy: season average or 0 with a "sufficient data" flag column).
2. **Target vector** (`y`): 1 = home win, 0 = away win. For totals modeling: total goals.
3. **Game index**: game_id and game_date for temporal sorting in walk-forward splits.
4. **Feature audit log**: each feature name, window size, shift applied (Y/N), leakage risk (from catalog).

Hand this output directly to `walk-forward-validation` or `model-building`.

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Features built, need to evaluate a model | Validate with temporal splits | `walk-forward-validation` |
| Features built, ready to train | Train with walk-forward methodology baked in | `model-building` |
| Suspect a feature has leakage | Audit shift/roll order, check leakage risk in catalog | `feature-engineering` (re-run Step 9) |
| Want to add Elo as a feature | Build Elo ratings first | `elo-engineering` |
| Want expected goals features | xG requires shot-level data and a separate process | `nhl-xg-model` |
| Features look good, want to test on past seasons | Score the model against the market's probabilities on past seasons | `backtesting` |

## Credits

- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
