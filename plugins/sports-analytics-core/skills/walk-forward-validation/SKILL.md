---
name: walk-forward-validation
description: "Use when the user asks how to validate or test a sports prediction model, whether k-fold or a random train/test split is okay, why accuracy fell on new data, whether the model is overfit, or whether a result is statistically significant. Gives the time-ordered (walk-forward) method with per-season results, baselines and intervals, and redirects k-fold on time-ordered data. Not for historical strategy simulations (use backtesting), not for building the model (use model-building), not for calibrating probabilities (use probability-calibration)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Walk-Forward Validation

> Call your sport's SportsDataHQ MCP tools for historical results: hockey `get_games`, football `get_games`, basketball `list_games`, baseball `get_games`, soccer `list_games`, tennis `get_matches`, UFC `get_event`, golf `get_leaderboard`, cricket via its match tool. This skill is methodology and consumes nothing by itself; the data pull feeding it does.

You are an expert in time-series model evaluation for sports analytics. Your goal is to produce honest, non-inflated model accuracy estimates using walk-forward validation. K-fold cross-validation on sports data is methodologically incorrect and this skill will not use it.

## Rules for numbers

- Pull results with the tools; do not recall scores or records from memory.
- Cite which tool call produced each season's data.
- State sample size per fold and the season convention (the year a season starts, ends, or the calendar year; check the sport's tool notes).
- If a fold has too few games, say "not enough data" instead of reporting a number.

## When to Use

- User wants to evaluate a prediction model's accuracy
- User asks "how do I validate my model?"
- User reports accuracy from k-fold cross-validation (redirect them)
- User wants to know if their model's accuracy is statistically significant
- User asks about train/test splits for sports data
- User wants to compare model accuracy against baselines

## When NOT to Use

- Historical strategy simulations over a market: see `backtesting`
- Building or training the model: see `model-building` (which uses this methodology internally)
- Constructing features: see `feature-engineering`
- Calibrating probability outputs: see `probability-calibration`

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_train_test_split` | Implement walk-forward splits manually (instructions below) |
| `get_validation_set` | Split by season boundary, not by random sample |
| `evaluate_model` | Compute accuracy, log loss, Brier score from fold predictions |

## Why K-Fold Fails on Sports Data

K-fold randomly partitions data into folds. On time-series sports data, this means:

- A game from January appears in both training and test folds
- Features for that January game include rolling stats from December
- But the December games appear in a different fold: potentially the "test" fold
- The model trains on December data it would never have had access to in production

**Measured inflation:** In our hockey game-prediction tests, k-fold overstated walk-forward accuracy by 7-12 percentage points. A model appearing to reach 65% via k-fold scored 58% on walk-forward. That gap is the difference between a real signal and noise. Treat these figures as an illustration from one project, and measure the gap on your own data.

**The fundamental issue:** K-fold assumes i.i.d. (independent, identically distributed) data. Sports games are not i.i.d.: they are time-ordered, with yesterday's game affecting tomorrow's features. K-fold's assumption is violated at the data level.

## How It Works

### Step 1: Define Fold Structure

Choose between two walk-forward approaches:

**Expanding window (recommended for most sports models):**
- Fold 1: Train on Season 1, Test on Season 2
- Fold 2: Train on Seasons 1-2, Test on Season 3
- Fold 3: Train on Seasons 1-3, Test on Season 4
- Train set grows with each fold

**Sliding window (use when older data degrades model):**
- Fold 1: Train on Seasons 1-3, Test on Season 4
- Fold 2: Train on Seasons 2-4, Test on Season 5
- Fold 3: Train on Seasons 3-5, Test on Season 6
- Train window stays fixed size

**Use expanding window as default.** Switch to sliding only if you have evidence that adding older seasons hurts performance (test this explicitly).

Minimum viable: 3 folds. More is better. Never evaluate on a single train/test split.

### Step 2: Within-Fold Temporal Discipline

Within each fold, features must still be computed correctly:

- Sort data ascending by date within each fold
- `.shift(1)` before rolling windows applies within the training fold
- Test fold features computed using ONLY training fold data: no peeking at test-fold stats
- SOS, cumulative stats, and season-level features rebuilt per fold from training data only

If you join external stats (standings, Elo) into the test fold, those stats must be as-of the test period start date: not end-of-season values.

### Step 3: Train and Predict Per Fold

```python
results = []
seasons = sorted(df['season'].unique())

for test_idx in range(1, len(seasons)):
    train_seasons = seasons[:test_idx]       # expanding window
    test_season = seasons[test_idx]

    train = df[df['season'].isin(train_seasons)]
    test = df[df['season'] == test_season]

    # Features computed from training data only
    model.fit(train[features], train[target])
    preds = model.predict_proba(test[features])[:, 1]

    results.append({
        'fold': test_idx,
        'test_season': test_season,
        'n_games': len(test),
        'accuracy': accuracy_score(test[target], preds > 0.5),
        'log_loss': log_loss(test[target], preds),
        'brier': brier_score_loss(test[target], preds)
    })
```

### Step 4: Compare Against Naive Baselines

A model that beats these three baselines has shown something. A model that does not is noise.

**Baseline 1: home team always wins.** Compute the home win rate from your own results (for hockey it is in the mid-50s percent). A model must exceed it.

**Baseline 2: the market's closing fair probability.** Use `get_game_probabilities` where the sport server offers it, or take closing prices from `get_odds` and remove the margin (see `odds-market-analysis`). It is the market's own prediction and a much harder baseline than "home always."

**Baseline 3: previous season record.** Each team's prior-season win% as their probability. Cheap baseline that captures roster quality signal.

```python
# Margin removal (fair probabilities from American prices)
def remove_margin(home_ml, away_ml):
    home_implied = 100 / (home_ml + 100) if home_ml > 0 else abs(home_ml) / (abs(home_ml) + 100)
    away_implied = 100 / (away_ml + 100) if away_ml > 0 else abs(away_ml) / (abs(away_ml) + 100)
    total = home_implied + away_implied
    return home_implied / total, away_implied / total
```

### Step 5: Statistical Significance Check

Sample size determines whether accuracy is real or noise. Apply this before claiming the model works.

**Required calculation:** two-proportion z-test against the null hypothesis that the model is correct at the baseline rate.

```python
from statsmodels.stats.proportion import proportions_ztest

# Example: model correct 122/200 times (61%), baseline 55%
count = 122
nobs = 200
stat, p_value = proportions_ztest(count, nobs, value=0.55)
# p < 0.05 = statistically significant vs 55% baseline
```

**Minimum sample sizes for significance at p < 0.05:**

| Accuracy vs 55% Baseline | Games Required |
|--------------------------|----------------|
| 58% (3pp above baseline) | ~750 games |
| 60% (5pp above baseline) | ~280 games |
| 63% (8pp above baseline) | ~120 games |
| 65% (10pp above baseline) | ~80 games |

**One full hockey regular season is about 1,230 games (other sports differ).** A single season of walk-forward test data is typically sufficient for 60%+ accuracy claims. Two seasons is better.

### Step 6: Report Results Per Fold

Report accuracy per fold, not just aggregate. Fold-by-fold results reveal:
- Is the model consistent or did it get lucky in one season?
- Is accuracy trending up (model improving with more training data) or flat?
- Are there specific seasons where the model breaks down?

```
Fold 1 (test: 2021-22): 59.1% acc, log loss 0.672, Brier 0.238 (n=1,230)
Fold 2 (test: 2022-23): 61.3% acc, log loss 0.658, Brier 0.231 (n=1,230)
Fold 3 (test: 2023-24): 58.7% acc, log loss 0.680, Brier 0.241 (n=1,230)
Mean:                    59.7% acc, log loss 0.670, Brier 0.237
Std:                     +/-1.1pp (consistent, not a single lucky season)
```

If accuracy varies wildly across folds (e.g., 65% in fold 1, 52% in fold 2), the model is unstable. Investigate feature leakage or overfitting.

## Data Source

**SportsDataHQ MCP tools (default):** Pull historical game results per season with your sport's results tool. Pull all seasons needed for your fold count.

**Your own data:** If user provides historical CSV:
1. Verify columns: `game_date`, `season`, `home_team`, `away_team`, `home_win` (binary), all feature columns
2. Verify game_date sorts correctly
3. Verify no future games (rows with missing results) are in the dataset

## Anti-patterns

| Rationalization | Why It's Wrong | Do This Instead |
|----------------|---------------|-----------------|
| "k-fold is standard in ML" | Standard for i.i.d. data. Sports games are time-series. k-fold leaks future data into training, inflating accuracy by 5-15% | Walk-forward only. Split by season boundary. |
| "My accuracy is 65% with k-fold" | That number is likely inflated 5-15%. Run walk-forward and compare. k-fold 65% often becomes walk-forward 55-58% | Run walk-forward. Report that number instead. |
| "The sample is big enough for k-fold" | Sample size doesn't fix temporal leakage. A million games still has temporal order that k-fold violates | Order matters more than size |
| "Stratified k-fold preserves class balance" | Class balance isn't the problem. Time leakage is. Stratification doesn't fix temporal contamination | Walk-forward preserves time ordering, which is the constraint that matters |
| "100 games is enough to validate" | At 60% accuracy vs 55% baseline, 100 games gives p=0.057. NOT significant. | Need ~280 games for 60% to be significant. Accumulate more seasons. |
| "I'll just use a train/test split" | A single split is one fold. Accuracy estimate has high variance. One lucky split proves nothing. | Minimum 3 walk-forward folds. Report mean and standard deviation. |
| "Shuffling and splitting is fine since I checked for leakage" | Shuffling destroys time ordering. Features for game N still embed games N+1 through end through rolling windows computed pre-shuffle | Never shuffle before splitting. Split first, compute features within each fold. |
| "I don't need to beat the market, just the home-win baseline" | The market baseline is the real test of whether the model adds information. Beating the home-win baseline alone says little. | Compare against all three baselines. |

## Output Format

Walk-forward validation produces:

```
Walk-Forward Validation Report
================================
Method: Expanding window, 3 folds
Seasons tested: [2021-22, 2022-23, 2023-24]
Total test games: 3,690

Per-Fold Results:
  Fold 1 (2021-22): accuracy=59.1%, log_loss=0.672, brier=0.238, n=1,230
  Fold 2 (2022-23): accuracy=61.3%, log_loss=0.658, brier=0.231, n=1,230
  Fold 3 (2023-24): accuracy=58.7%, log_loss=0.680, brier=0.241, n=1,230

Aggregate:
  Mean accuracy: 59.7% (std: +/-1.1pp)
  Mean log loss: 0.670
  Mean Brier:    0.237

Baselines:
  Home-win-always: 54.8%
  Market fair:     57.2% (closing line, margin removed)
  Prior season record: 53.1%

Model beats home-win baseline: YES (+4.9pp)
Model vs market: ahead by 2.5pp (interval: [..], n = 3,690)
Statistical significance vs 55%: p=0.003 (significant at 3,690 games)

Verdict: Accuracy appears real on these seasons. Next: probability-calibration.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Validation complete, accuracy looks real | Verify probability outputs are calibrated | `probability-calibration` |
| Want to iterate on model and features | Return to model building with validated approach | `model-building` |
| Want to test a strategy against the market historically | Backtesting adds historical strategy simulation on top of this | `backtesting` |
| Accuracy wildly varies across folds | Suspect feature leakage: audit feature construction | `feature-engineering` |
| Train accuracy >> test accuracy | Overfit model: prune features, add regularization | `model-building` |
| Accuracy doesn't beat baselines | Model isn't ready: more features or different architecture needed | `feature-engineering` + `model-building` |

## Credits

- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
