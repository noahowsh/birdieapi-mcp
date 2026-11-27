# SportsDataHQ: analytics core

Sport-agnostic skills: model building, feature engineering, backtesting, walk-forward validation, calibration, Elo, visualization, data pipelines, and comparing a model with the market as information.

## Skills

- `backtesting`: Use when the user asks whether a sports model or system would have worked in the past, for any sport, in plain wording.
- `data-pipeline`: Use when the user wants to automate a sports model: run predictions every morning, set up a cron job or GitHub Action, store predictions in a database, version models, retrain on a schedule or get alerted when accuracy drifts.
- `elo-engineering`: Use when the user asks to build Elo ratings, rate teams or players, tune K-factor or home advantage, carry ratings across seasons, add margin-of-victory, or mentions Fading, Form or Component Elo.
- `feature-engineering`: Use when the user asks to prepare data for a model, build rolling averages or recent-form features, add rest days or back-to-back flags, adjust for strength of schedule, build starter or goalkeeper quality features, use Elo as an input, or check features for leakage.
- `market-vs-model`: Use when the user compares their own model's numbers with the betting market, for any sport, in plain wording.
- `model-building`: Use when the user wants to build or choose a model that predicts sports outcomes, for any sport, in plain wording.
- `odds-market-analysis`: Use when the user asks what betting odds mean as numbers, for any sport, in plain wording.
- `prediction-tracker`: Use when the user wants to log model predictions and grade them as games finish, for any sport, in plain wording.
- `probability-calibration`: Use when the user asks about the quality of a model's probabilities, for any sport, in plain wording.
- `season-pack-offline`: Use when no SportsDataHQ MCP tools are available in this session (no get_standings, get_leaders or similar tools listed) and the user asks about a sport's last completed season, or says they have no key or want to try before signing up.
- `sports-data-preflight`: Use when a sports number looks wrong or the data may not line up, in plain wording.
- `visualization`: Use when the user wants a chart, plot, graph, picture or shareable image of an analysis, for example 'plot the calibration', 'make a matchup card', 'chart the model against the market', 'visualize that', 'make this look good for a post'.
- `walk-forward-validation`: Use when the user asks how to validate or test a sports prediction model, whether k-fold or a random train/test split is okay, why accuracy fell on new data, whether the model is overfit, or whether a result is statistically significant.

## Data it sends

These skills hold methods only (modelling, validation, metrics). They make no calls of their own; the numbers come from whichever SportsDataHQ sport plugin you also install.

Privacy policy: https://app.sportsdatahq.com/privacy

## Install

```
/plugin marketplace add sports-data-hq/sportsdatahq-skills
/plugin install sports-analytics-core@sportsdatahq
```

More: https://sportsdatahq.com/#skills. Licence: MIT (see LICENSE).
