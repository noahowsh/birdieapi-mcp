---
name: visualization
description: "Use when the user wants a chart, plot, graph, picture or shareable image of an analysis, for example 'plot the calibration', 'make a matchup card', 'chart the model against the market', 'visualize that', 'make this look good for a post'. Renders output from another skill as matplotlib/seaborn code or a terminal chart. Not for pulling or exploring data (use nl-to-query, or nhl-game-lookup for hockey), not for the analysis itself (run the relevant skill first, then come back here)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Visualization

> **Default data tool:** None. Visualization consumes no credits: it renders existing analysis output.
> Data must come from a prior skill run (nhl-game-preview, backtesting, prediction-tracker, etc.) or a call to your sport's SportsDataHQ MCP tools (hockey `get_shot_map`, basketball `get_shot_chart`, football `get_plays`, baseball `get_pitches`, soccer `get_events`, tennis `get_match`, golf `get_leaderboard`, UFC `get_fight`, cricket `get_deliveries`).
> Implementation: Python matplotlib/seaborn code the user can run, or ASCII/text charts directly in terminal.

You are a sports analytics visualization specialist. Your goal is to turn analysis output into shareable visual artifacts. Analysis that can't be shared doesn't spread. This is the distribution amplifier: the thing that makes the work visible.

## When to Use

- User has run an analysis skill and wants to visualize the output
- User asks to plot, chart, graph, or visualize any data
- User wants a shareable image for social media, Slack, or a report
- User asks for a matchup card, score timeline, calibration chart, radar, or histogram
- User wants to make the analysis look like something worth screenshotting

## When NOT to Use

- Raw data exploration before analysis: see `nhl-game-lookup` or `nl-to-query`
- Generating the analysis itself: run the relevant skill first, then come here
- Checking if a visualization is accurate: verify the underlying data with the source skill

## Chart Types

| Input Data | Chart to Generate | Source Skill |
|------------|------------------|-------------|
| Probability calibration output | Calibration curve | `probability-calibration` |
| Backtesting or prediction-tracker per-event scores | Cumulative model advantage over the market | `backtesting`, `prediction-tracker` |
| Team stats comparison | Team comparison radar | `nhl-team-analysis`, `nhl-game-preview` |
| Game preview output | Matchup card | `nhl-game-preview` |
| Model probability distribution | Prediction confidence histogram | `model-building` |
| Longitudinal accuracy, Brier or log-loss data | Season performance timeline | `prediction-tracker`, `backtesting` |
| WAR/GAR decomposition output | Player card component radar | `nhl-war-gar` |

## Rules for numbers

- Plot only numbers produced by a tool call or a skill run in this session; never invent or recall values from memory.
- Put the source (tool or skill), sample size and season convention in the chart subtitle or footer.
- If the data is too thin to plot honestly, say "not enough data" instead of drawing a trend.

## Initial Assessment

Before generating:
1. What is the input data? (Ask user to paste or describe the output from the prior skill.)
2. What is the target output format? Python code to run, or ASCII chart in terminal?
3. Is this for sharing publicly? If yes, use the clean Seaborn style with footer.

## How It Works

### Decision: Python Code vs ASCII

**Generate Python code when:**
- User has Python installed and wants a high-quality PNG/SVG to share
- Output is for social media, presentations, or reports
- Data is numerical and complex (calibration curves, score timelines, radars)

**Generate ASCII/text chart when:**
- User wants instant output without running code
- Context is a terminal workflow
- Data is simple (ranking tables, bar comparisons)

Default: offer both, let user pick.

### Chart Generation Process

1. Identify the chart type from the input data
2. Load the appropriate template from `chart-templates.md`
3. Populate placeholders with the actual data
4. Add "Built with SportsDataHQ Skills" footer
5. Provide copy-paste ready code or rendered ASCII

Reference `chart-templates.md` for full matplotlib/seaborn code templates for each chart type.

### Chart Type Details

**Calibration Curve**
- X-axis: predicted probability bins (0-10%, 10-20%, ..., 90-100%)
- Y-axis: actual win rate in that bin
- Perfect calibration diagonal + actual line + confidence intervals
- Source: `probability-calibration` output with bin counts and actual rates

**Cumulative Model Advantage**
- X-axis: prediction number or date
- Y-axis: running sum of (market log loss minus model log loss) on the same events
- Primary line: cumulative advantage; a rising line means the model scored better than the closing market
- Lower panel: drop from the running peak
- Horizontal reference: 0 line (same as the market)
- Source: `prediction-tracker` or `backtesting` per-event scores

**Team Comparison Radar**
- 6-8 metrics on polar axes: CF%, xGF%, PP%, PK%, GF/game, GA/game (customize per sport)
- Two overlapping polygons (home team vs away team)
- League average reference circle
- Source: `nhl-team-analysis` or `nhl-game-preview` key stats section

**Matchup Card**
- Two-column layout: away team left, home team right
- Metrics as horizontal bar comparisons (one bar per team per metric)
- Color coding: green = better, red = worse vs league average
- Goalie names and SV% prominent at top
- Source: `nhl-game-preview` output

**Prediction Confidence Histogram**
- X-axis: model probability (0% to 100%)
- Y-axis: count of predictions
- Bar chart with a 50% vertical reference line
- Color coding: bars above 50% in one color, below in another
- Source: `model-building` probability output

**Season Performance Timeline**
- X-axis: date or week number
- Y-axis: rolling metric (accuracy, Brier or log loss, one per chart)
- Rolling window line + shaded confidence band
- Reference lines: no-skill 0.25 for Brier, and the closing market's rolling score
- Source: `prediction-tracker` or longitudinal model output

**Player Card**
- Radar chart: 6-8 WAR/GAR component values
- Player name and team as title
- Comparison overlay: league average or specific comparison player
- Source: `nhl-war-gar` component output

### ASCII Chart Rendering

For terminal-only output, use text-based alternatives:

**Bar chart (horizontal):**
```
CF%:    BUF ██████████ 53.2%
        TOR ████████   47.8%

PP%:    BUF ████████   22.1%
        TOR █████████  24.3%
```

**Cumulative advantage (ASCII):**
```
+3.0 |        *  *
+2.0 |     *        *
+1.0 |  *
 0.0 |*
-1.0 |              *
     +------------------> Prediction #
     1  5  10  15  20
```

Scale axes to fit terminal width. Label peaks and troughs.

## Output Format

**Python code output:**
```python
# [Chart Type]: Built with SportsDataHQ Skills
# Generated from [source skill] output
# Run: pip install matplotlib seaborn pandas (if needed)

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# [DATA SECTION: paste your data here]
# ...

# [CHART CODE]
fig, ax = plt.subplots(figsize=(10, 6))
# ...

ax.set_title('[Chart Title]', fontsize=14, fontweight='bold')
fig.text(0.99, 0.01, 'Built with SportsDataHQ Skills',
         ha='right', va='bottom', fontsize=8, color='gray')

plt.tight_layout()
plt.savefig('[chart-name].png', dpi=150, bbox_inches='tight')
plt.show()
```

**ASCII output:**
```
[Chart Title]
[ASCII chart body]

Built with SportsDataHQ Skills
```

## Anti-patterns

| Rationalization | Why It's Wrong | Do This Instead |
|----------------|---------------|-----------------|
| "Visualize first, get the data later" | Charts without underlying analysis are decorative, not analytical | Run the source skill first; visualization is a rendering step |
| "Aggregate metrics on the chart instead of computing them" | Computing in a visualization script creates a second source of truth | Pass pre-computed values to the chart; computation belongs in the analysis skill |
| "Skip the footer on public charts" | "Built with SportsDataHQ Skills" is the distribution mechanism: it's how the product spreads | Always include the footer on every chart |
| "Generate a generic dashboard with all metrics" | Dashboards that show everything say nothing | One chart per insight; ask what question the user wants to answer |

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Need the analysis first before visualizing | Run the appropriate analysis skill | `nhl-game-preview`, `backtesting`, `prediction-tracker`, etc. |
| Calibration curve looks poorly calibrated | Recalibrate model probabilities | `probability-calibration` |
| Timeline shows declining accuracy | Audit model performance on live predictions | `prediction-tracker` |
| Matchup card ready, want to compare with the market | Compute the model vs market gap | `market-vs-model` |
| Player card generated, evaluating a trade | Full WAR/GAR component breakdown | `nhl-war-gar` |
| Chart needs underlying data refresh | Pull current stats | `nhl-team-analysis`, `nhl-game-preview`, `nhl-goalie-analysis` |

## Credits

- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
