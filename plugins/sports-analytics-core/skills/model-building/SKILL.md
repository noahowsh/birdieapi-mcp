---
name: model-building
description: "Use when the user wants to build a prediction model for game or match outcomes, train a classifier, choose between logistic regression, random forest or XGBoost, tune hyperparameters, see which features matter or combine models. Always walk-forward; refuses k-fold. Works for any sport. Not for building features (use feature-engineering), not for checking probability quality (use probability-calibration), not for fold design alone (use walk-forward-validation), not for expected goals models (use nhl-xg-model), not for comparing output with market probabilities (use market-vs-model)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Model Building

You are an expert in building sports prediction models. The goal is a classifier that gives honest accuracy and probability estimates on held-out walk-forward test folds. Training accuracy is never reported. Walk-forward test performance is the only number that matters.

## Data

Call your sport's SportsDataHQ MCP tools for historical results and inputs (hockey get_games and get_shot_map, football get_games and get_plays, basketball list_games and get_shot_chart, baseball get_games and get_pitches, soccer list_games and get_events, tennis get_matches and get_match, golf get_leaderboard, UFC get_fight, cricket get_deliveries). Features should already be built and audited upstream (feature-engineering). Training itself is local and calls no tools.

Own data (feature matrix CSV): columns game_id, game_date, season, all feature columns, and the target (for example home_win). Sorted ascending by game_date, no NaN in feature columns.

## Rules for numbers

- Call the tools for any data figure; never answer from memory.
- Cite which tool call supplied the training data (tool plus arguments).
- State sample size per fold (training and test games) and the season convention.
- Report intervals with every accuracy or log loss figure. If there are too few test games, say "not enough data" instead of ranking models on noise.

## When to Use

- Build a model that predicts outcomes
- Choose between logistic regression, random forest and XGBoost
- Tune hyperparameters
- Combine models into an ensemble
- Find which features matter

## When NOT to Use

- Feature construction: use `feature-engineering`
- Checking the fold design: use `walk-forward-validation`
- Checking probabilities are calibrated: use `probability-calibration`
- Expected goals models: use `nhl-xg-model`
- How our probability differs from the market's: use `market-vs-model`

## Initial Assessment

Before training, establish:
1. Are features built and audited for leakage? If not, start with `feature-engineering`.
2. How many seasons of historical data are available? (determines fold count)
3. Is the prediction target binary win/loss, or probability, or goal differential?

## How It Works

### Step 1: Start with Logistic Regression

Always start with the simplest model. Logistic regression provides:
- A performance floor to beat
- Interpretable coefficients (which features drive predictions)
- Fast training (iterate quickly)
- A calibration baseline (logistic outputs are well-calibrated by default)

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Fit on train only

lr = LogisticRegression(C=1.0, max_iter=1000)
lr.fit(X_train_scaled, y_train)
preds = lr.predict_proba(X_test_scaled)[:, 1]
```

**If logistic regression gets 58% walk-forward accuracy and XGBoost gets 59%, the added complexity is not worth it.** Report logistic regression as the model.

### Step 2: Model Selection Guidance

Progress through this ladder. Move to the next only if walk-forward accuracy improves by at least 1 percentage point.

| Model | When to Use | Key Advantage | Key Risk |
|-------|------------|---------------|----------|
| Logistic Regression | Always start here | Interpretable, calibrated, fast | Linear decision boundary |
| Random Forest | If LR plateau < 60% | Handles non-linearity, robust to outliers | More tuning, less interpretable |
| XGBoost | If RF improves over LR | Highest ceiling on structured data | Overfits on small sports datasets |
| Ensemble (hard vote) | After testing 3+ models | Reduces variance across model types | Complexity; only worthwhile if models are diverse |

### Step 3: Walk-Forward Hyperparameter Tuning

Hyperparameters are tuned using walk-forward folds, never on the full dataset.

**Correct approach:**
```python
# Tune on inner folds, evaluate on outer test fold
from sklearn.model_selection import TimeSeriesSplit

# Use TimeSeriesSplit within each training fold for HPO
inner_cv = TimeSeriesSplit(n_splits=3)
param_grid = {'n_estimators': [100, 200, 500], 'max_depth': [3, 5, 7], 'learning_rate': [0.05, 0.1, 0.2]}

# Grid search only on training data, never on test fold
grid_search = GridSearchCV(XGBClassifier(), param_grid, cv=inner_cv, scoring='neg_log_loss')
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

**Do not tune hyperparameters by looking at test fold accuracy.** That is test-set snooping. Tune on training folds only, lock parameters, then evaluate on the held-out test fold.

### Step 4: Ensemble Construction

If three or more models each reach 58%+ walk-forward accuracy independently, ensemble them.

**Test both combination rules on your own walk-forward folds.** Hard vote is often a robust choice when base models are diverse; probability averaging keeps more information and is better when you need probabilities rather than labels.

```python
# Hard vote: majority of models must agree
def hard_vote(preds_list, threshold=0.5):
    votes = [(p > threshold).astype(int) for p in preds_list]
    majority = np.round(np.mean(votes, axis=0))
    return majority

# Probability averaging (often worse):
def avg_proba(preds_list):
    return np.mean(preds_list, axis=0)
```

**Trade-off:** When models disagree on a game, that is a lower-confidence prediction. Hard vote can abstain there (no majority, no prediction). Probability averaging smooths the disagreement into a probability near 0.5, which is honest but loses the signal that the models split. If you need probabilities for calibration or for comparing with the market, average, then calibrate.

**Diversity requirement:** Models in an ensemble must use zero shared features. Three models with overlapping features do not reduce variance, they are correlated noise. Aim for separate feature sets across base models.

### Step 5: Feature Importance Analysis

After each walk-forward fold, extract feature importance:

```python
# XGBoost / Random Forest
importances = model.feature_importances_
feature_importance_df = pd.DataFrame({'feature': features, 'importance': importances})
feature_importance_df.sort_values('importance', ascending=False)

# Logistic Regression (use coefficient magnitude)
coef_df = pd.DataFrame({'feature': features, 'coef': np.abs(lr.coef_[0])})
coef_df.sort_values('coef', ascending=False)
```

Aggregate importance across folds. Features that consistently rank in the bottom 10% across all folds are candidates for removal. Remove them and retest, if walk-forward accuracy holds or improves, they're gone.

**Warning sign:** If a feature shows very high importance (>30% of total) in isolation, inspect it for leakage. Leaky features dominate importance rankings because they carry perfect information.

### Step 6: Overfitting Detection

Compare training accuracy vs walk-forward test accuracy per fold:

| Gap | Interpretation |
|-----|---------------|
| <2pp | No meaningful overfitting |
| 2-5pp | Moderate overfitting, consider regularization |
| 5-10pp | Significant overfitting, prune features, increase regularization |
| >10pp | Severe overfitting, model is memorizing training data |

**For XGBoost:** Increase `min_child_weight`, decrease `max_depth` (try 3-4), add `subsample=0.8`, add `colsample_bytree=0.8`.
**For Random Forest:** Increase `min_samples_leaf`, decrease `max_features`.
**For Logistic Regression:** Decrease `C` (stronger regularization).

### Step 7: Model Persistence

Save: model object, feature pipeline (scaler, encoders), version metadata.

```python
import joblib
import json
from datetime import datetime

# Save model
joblib.dump(model, 'model_v1.pkl')
joblib.dump(scaler, 'scaler_v1.pkl')

# Save metadata
metadata = {
    'version': '1.0',
    'trained_date': datetime.today().isoformat(),
    'train_seasons': ['2019-20', '2020-21', '2021-22', '2022-23'],
    'features': features,
    'walk_forward_accuracy': 0.597,
    'walk_forward_log_loss': 0.670,
    'n_walk_forward_folds': 3,
    'baseline_home_win': 0.548,
    'baseline_market': 0.572  # market no-margin probability, accuracy
}
with open('model_v1_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
```

Always version models. When you retrain, increment the version. Keep old models, if new model underperforms, you roll back.

## Anti-patterns

| Rationalization | Why It's Wrong | Do This Instead |
|----------------|---------------|-----------------|
| "90% accuracy on training data" | Meaningless. Training accuracy always inflates; the model has seen this data. | Report walk-forward test accuracy only. Training accuracy is not in the output. |
| "XGBoost always wins on tabular data" | Start with logistic regression baseline. If the gap is <1pp, the complexity isn't worth it. | Ladder up: LR first, RF second, XGBoost third. |
| "More features = better model" | More features = more overfitting risk on small sports datasets (1,000-5,000 games/season). | Use feature importance to prune. Start with 12 features, add only when walk-forward improves. |
| "My model beats the market this season" | Over how many games, with what interval? One season is a small sample. | Minimum 3 walk-forward folds. Report per fold with an interval, and compare log loss with the market's no-margin probability (see backtesting). |
| "Probability averaging is the right ensemble method" | Not always; it depends on the data. | Test hard vote and averaging on walk-forward folds, with diverse base models. |
| "I tuned hyperparameters on the test fold to maximize accuracy" | That is test-set snooping. Your reported accuracy will not generalize. | Tune only on training folds. Lock parameters before touching the test fold. |
| "I'll add more data later to fix overfitting" | More data helps, but overfitting from too many features or too deep trees isn't fixed by data volume. | Regularize the model now. Prune features. |
| "k-fold is fine for model comparison" | k-fold leaks future data into training on time series. Use walk-forward for all evaluation. | Walk-forward for model comparison, not just final evaluation. |

## Output Format

Model building produces the report below. All numbers are placeholders showing the format, not results:

```
Model Training Report
======================
Model: XGBoost (n_estimators=200, max_depth=4, lr=0.1)
Features: 24 (after pruning 8 low-importance features)
Ensemble: No (single model)

Walk-Forward Results (3 folds):
  Fold 1 (test: 2021-22): train_acc=63.1%, test_acc=59.1%, gap=4.0pp (acceptable)
  Fold 2 (test: 2022-23): train_acc=64.2%, test_acc=61.3%, gap=2.9pp (acceptable)
  Fold 3 (test: 2023-24): train_acc=62.8%, test_acc=58.7%, gap=4.1pp (acceptable)

Mean walk-forward test accuracy: 59.7% (std: ±1.1pp)
Mean log loss: 0.670
Mean Brier score: 0.237

Top 5 Features by Importance:
  1. elo_diff: 18.3%
  2. starter_gsaa_ytd (diff): 14.1%
  3. corsi_pct_roll10 (diff): 11.2%
  4. rest_days (home): 8.7%
  5. goal_diff_roll10 (diff): 7.9%

Baselines beaten:
  Home-win-always (54.8%): YES (+4.9pp)
  Market no-margin probability (57.2%): YES (+2.5pp)

Model saved: model_v1.pkl + scaler_v1.pkl + model_v1_metadata.json

Next: probability-calibration to verify probability outputs
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Model trained, want to verify probabilities are accurate | Check calibration curve | `probability-calibration` |
| Want to see how the model's probability differs from the market's | Compare with no-margin market probabilities | `market-vs-model` |
| Want to test the model on past seasons against the market | Walk-forward test with intervals | `backtesting` |
| Train accuracy >> test accuracy (>5pp gap) | Overfit, prune features, add regularization | `feature-engineering` + return here |
| Model doesn't beat baselines | More features needed or different architecture | `feature-engineering` + return here |
| Want to build xG model specifically | Different methodology, shot-level data | `nhl-xg-model` |
| Need to add Elo as a feature | Build Elo ratings first | `elo-engineering` |
