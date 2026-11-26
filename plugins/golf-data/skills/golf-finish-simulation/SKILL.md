---
name: golf-finish-simulation
description: "Use when the user wants golf win or finish chances from a simulation, in fan or analyst wording: 'who is most likely to win this week', 'Cantlay's chance of a top 5', 'odds he makes the cut', 'will a longshot win', 'run the field 10,000 times', 'percent chance to finish top 20', 'simulate the PGA', 'top 10 chances for Schauffele', 'odds a nobody wins', 'probability of a debut winner'. Use this whenever someone wants probabilities for a golf tournament outcome. Also use it for bare follow-ups with no name given, and load it instead of answering from memory or going straight to the raw tools. Runs a Monte Carlo simulation in code from strokes-versus-field ratings and round-to-round spread, with the method and simulation error stated. Not for a field preview (see golf-tournament-preview), a player's form (see golf-strokes-vs-field), course record (see golf-course-history), a played event's recap (see golf-leaderboard-story) or sportsbook prices."
metadata:
  version: 2.2.0
  author: SportsDataHQ
---

# Golf finish simulation

Probabilities from a simulation, not from memory. This skill simulates a tournament from our strokes-versus-field ratings and the round-to-round spread of results, runs the code, and reports win, top-5, top-10 and cut-making rates with their simulation error.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the BirdieAPI MCP server (`https://mcp.birdieapi.com/mcp`). Call them; never fill in a number from memory.
- Seasons are tour season years; PGA Tour seasons from 2014 to 2024 began the previous October. Pass `league` for other tours. Players from `search_players` (1 cr); the field from `get_leaderboard(tournament_id)` (2 cr) once it is set, otherwise the user supplies the list.
- Our rating (`get_ratings`, 2 cr) is strokes per round better than an average player in the same fields, adjusted for field strength and weighted to recent rounds: positive is better. Use it as each player's mean round score relative to the field.
- Round-to-round spread is not given. Compute it from `get_player_results(player_id, season, limit)` (5 cr): the standard deviation of `adj_vs_field` across a player's recent rounds. Use a pooled value over the field sample if one player has under 20 rounds, and say which. If no rounds can be read, stop; do not assume a spread.
- Not modelled: course fit, weather, tee-time waves, pressure or rust. Say so. The simulation is for ratings-based probabilities, not a forecast of one week.
- Majors only: `get_winner_odds` (5 cr) shows sportsbook winner prices; show the market's no-margin probability beside ours as information, never as advice.

## Default path (about 20 to 60 credits plus a local run)
1. **Field and ratings.** `get_leaderboard(tournament_id)` (2 cr) or the user's list; `get_ratings(limit, min_rounds)` (2 cr) for each player's rating.
2. **Spread.** `get_player_results(player_id, limit)` (5 cr) for a sample of players (at least 5, including top and mid-rated); compute the standard deviation of `adj_vs_field` per round, pooled.
3. **Run the simulation in code.** For each of 20,000 or more runs: each player's round = -(rating) + normal(0, spread) (lower is better); 36 holes, cut to the top 65 and ties, then 36 more holes for those who make it; ties broken at random (state it). Set a seed. Count wins, top 5, top 10, top 20 and cuts made.
4. **Report** each rate with its standard error sqrt(p(1-p)/runs) and the run count. Print real output from the code; never write a probability that the run did not produce.
5. **Compare (optional, majors).** `get_winner_odds(tournament_id)` (5 cr): the market's no-margin probability beside the simulated win rate.

## Method and limits
Ratings are strokes versus the field, so a rating of 1.5 is a mean of 1.5 strokes per round better than the field average; the field's average is the zero line, so scores are simulated relative to the field and course difficulty drops out. Cut rule: top 65 and ties after 36 holes unless the event differs; say what you used. Rates below 1% are shown as under 1% with the error. This does not know who is injured or withdrew; check the leaderboard status.

## Output template
```
<Tournament> | <tour, season> | field <n> | simulations <runs>, seed <s>
Method: ratings <as of date>, round spread <v> (from <k> players, <r> rounds), cut <rule>, ties <rule>
Top of the table: <player>: win <%> (+/- <se>), top 5 <%>, top 10 <%>, made cut <%>
  ... 8 to 15 rows
Market (majors only, optional): <player>: market no-margin <%> vs simulated <%>
Limits: course fit, weather and injuries not modelled
Data: get_leaderboard, get_ratings, get_player_results[, get_winner_odds] | <tour>, <season>; probabilities from the simulation run
```

## Rules
- Every probability comes from a simulation run you executed in this session; never write one that was not printed.
- State runs, seed, spread, cut rule and tie rule.
- Show standard error beside each rate.
- Market prices are shown only as information, beside the simulation.
- Every number names its tool (the Data line, plus inline where it could be doubted) and every rate shows its sample size.
- If a tool returns too little, say "not enough data" and stop; do not estimate or borrow another sample.
- Odds and prices are information about the market only: no picks, leans, stakes, payouts or sportsbook links.
- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.

## Example prompts
- "Who is most likely to win the Masters by our ratings?"
- "Simulate this week's tournament"
- "Chance Scottie Scheffler finishes top 10"
