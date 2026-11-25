---
name: nl-to-query
description: "Use when the user asks a research question in plain English and does not name a tool or field, for example 'show me games where the home team was outshot but won', 'how often does the team that scores first win', 'find back-to-back losses', 'who leads the league in X when Y'. Translates the question into conditions, calls your sport's SportsDataHQ MCP tools, retries with adjusted filters when results look wrong, and reports counts with sample size. Not for a lookup where the tool is obvious (use nhl-game-lookup, nhl-team-analysis or nhl-goalie-analysis for hockey), not for building model features (use feature-engineering)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Natural Language to Query

Map what the user means to what the data contains, run it, and validate the result. Works with any sport's SportsDataHQ MCP server; the bundled dictionary (`schema-dictionary.md`) covers hockey terms in detail, and the method applies to every sport.

## Rules for numbers

- Call the tools. Never answer a count or rate from memory.
- Cite which tool call (and parameters) produced each number.
- State sample size (matching rows out of total rows) and the season convention (calendar year, or the year the season starts or ends; the sport's tool notes say which).
- If the data cannot answer the question, say "not enough data" instead of guessing.

## Tools by sport

Pick the tool that holds the unit of analysis. Names differ by sport; read the server's tool list first.

| Question about | Examples |
|----------------|----------|
| Games and results | hockey `get_games`, basketball `list_games`, soccer `list_games`, tennis `get_matches` |
| Event or location data | hockey `get_shot_map`, basketball `get_shot_chart`, football `get_plays`, baseball `get_pitches`, soccer `get_events`, cricket `get_deliveries` |
| Single contest detail | tennis `get_match`, UFC `get_fight`, golf `get_leaderboard`, hockey `get_game_detail` |
| Team or player aggregates | `get_team_stats`, `get_player_stats` or `get_player`, hockey `get_goalie_stats` |
| Market data (information only) | `get_odds`, `get_game_probabilities`, `get_line_movement` |

Do not invent tools such as `search_games`, `filter_games` or `aggregate_stats`. Pull rows, filter and aggregate client-side, and show row counts before and after each filter.

## Season resolution

Seasons are named differently by sport (the year the season starts, the year it ends, or the calendar year). Read the server's notes and state the convention you used. "This season" is the one in progress or most recently completed; "last season" is the one before it; "last 30 games" is counted back from today's date.

## How it works

1. **Parse**: conditions (home, outshot, won), metrics (shots, goals, save rate), comparators, and time scope.
2. **Map to fields** using the dictionary or the tool's documented fields. Ask when a term is ambiguous (for example "won": regulation only, or including extra time?).
3. **Choose the tool** from the table above. Prefer pre-aggregated tools when they answer the question; use row-level tools when conditions need per-game values.
4. **Run it** and count rows.
5. **Self-correct**: zero rows, an implausibly large count or odd values mean a bad filter, field name or date range. Drop one filter at a time to find the culprit, inspect one raw row, and retry. After the third failed attempt, report what was tried and what came back. Do not make up a result.
6. **Report**: exact conditions, M matches out of N rows, the rate, and a small-sample warning under 30 rows.

Common hockey mappings:

| User said | Field | Operator | Value |
|-----------|-------|----------|-------|
| "outshot 2:1" | shots_against / shots_for | > | 2.0 |
| "back-to-back" | rest_days | = | 0 |
| "shutout" | goals_against | = | 0 |
| "blowout" | abs(goal_differential) | >= | 4 |
| "strong goalie game" | sv_pct | >= | .915 |

Other sports use the same pattern. Examples: basketball "hot shooting night" (team three-point rate above a stated cutoff), football "third and long" (down = 3, distance >= 7 in `get_plays`), baseball "pitcher went deep" (innings >= 7), soccer "dominated shots" (shots share above 0.6).

## Using the user's own data

1. Check the columns the conditions need exist.
2. Map their column names to the dictionary terms.
3. Apply filters in sequence with counts after each.

## Anti-patterns

| Rationalization | Why it is wrong | Do this instead |
|-----------------|-----------------|-----------------|
| "The user probably means field X" | Guessed fields give silently wrong results | Map explicitly and flag ambiguity |
| "Zero results means no games match" | Often a bad filter or field name | Remove filters one at a time |
| "I remember roughly how often that happens" | Memory differs from the data | Retrieve it |
| "12 matches is enough" | Too few to conclude | Report N and call it anecdotal |

## Output format

```
Query: "[original question]"
Translated conditions: [field operator value] ...
Data source: [tool calls, parameters]
Time window: [dates or season, convention]
Total rows in window: N   Matched: M (M/N %)
[first 5 matching rows]
Interpretation: [one sentence]
Caveat: [sample size or data limits]
```

## What to do next

| Finding | Skill |
|---------|-------|
| Interesting pattern, hockey team or player | `nhl-team-analysis`, `nhl-player-scouting` |
| Pattern worth modeling | `feature-engineering` |
| Pattern worth testing historically | `backtesting` |
| Goalie condition | `nhl-goalie-analysis` |
| Formal hypothesis test | `nhl-research-workflow` |
