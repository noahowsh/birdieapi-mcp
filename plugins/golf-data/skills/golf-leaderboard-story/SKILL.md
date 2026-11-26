---
name: golf-leaderboard-story
description: "Use when the user wants the story of a golf tournament that has been played or is under way, in fan or analyst wording: 'what happened at Riviera', 'how did Scottie win', 'who charged on Sunday', 'where did he blow it', 'why did the leader collapse', 'recap the Open', 'back nine breakdown', 'how did he lose a 4 shot lead', 'how did he win it', 'who made a charge on the final day', 'where did it go wrong for him', 'how did the lead slip away'. Use this whenever someone asks how a result came about. Also use it for bare follow-ups with no name given, and load it instead of answering from memory or going straight to the raw tools. Builds a round-by-round and hole-by-hole account from the leaderboard and scorecards, with strokes versus the field. Not for who will win (see golf-finish-simulation), a field preview (see golf-tournament-preview), a player's form over time (see golf-strokes-vs-field) or course history (see golf-course-history)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Golf leaderboard story

Final scores hide where a tournament turned. This skill reads the leaderboard and scorecards from BirdieAPI and tells it round by round and hole by hole, with strokes versus the field.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the BirdieAPI MCP server (`https://mcp.birdieapi.com/mcp`). Call them; never fill in a number from memory.
- Seasons are tour season years; PGA Tour seasons from 2014 to 2024 began the previous October. Pass `league` for the LPGA, LIV, DP World Tour or Korn Ferry Tour. Find the id with `list_tournaments(season)` (1 cr) or `get_schedule` (1 cr).
- `get_leaderboard(tournament_id)` (2 cr) returns every player's position, status, score to par, strokes, each round's score and strokes versus the field, and any playoff.
- `get_scorecard(tournament_id, player_id)` (2 cr) returns holes with par, yards and result. Hole-by-hole is held for the PGA Tour (2001 on) and Korn Ferry Tour; the LPGA has it only for 2013-16 and some 2026 events; the DP World Tour and LIV have round scores only. Say when hole detail is not held.
- Strokes versus the field is the field's average that round minus the player's score: positive is better.

## Default path (about 10 to 20 credits)
1. **Find the event.** `list_tournaments(season, league)` (1 cr).
2. **The leaderboard.** `get_leaderboard(tournament_id, limit: 15)` (2 cr): top finishers with round scores and strokes versus the field; note the playoff and the cut status.
3. **The turning rounds.** From round-by-round lines: who led after each round, the largest round gains, and who dropped.
4. **The turning holes.** `get_scorecard(tournament_id, player_id)` (2 cr) for the winner and the one or two key players: holes where the result changed the lead, birdie or bogey runs, par-5 scoring.
5. **Context (optional).** `get_ratings(as_of: <event start>)` (2 cr) to say whether the winner was a favourite by our rating; `get_course(course_id)` (2 cr) for how holes played.

## Reading it
Describe what the scorecards show; do not guess at causes (weather, pins, nerves) that no tool returns. Say who was leading after each round only from the leaderboard rows. Call a rating gap a favourite only as our rating says. If the tournament is in progress, state the round it is after.

## Output template
```
<Tournament> | <tour, season> | status <final / after round n> | winner <name> at <score to par>
Round by round: R1 <leader, score> | R2 <...> | R3 <...> | R4 <...>
The move: <player> gained <v> strokes versus the field in round <n>
Turning holes: <hole, par, result, what it did to the lead>
Playoff (if any): <result>
Read: 2-3 bullets limited to what the rows show
Data: list_tournaments, get_leaderboard, get_scorecard[, get_ratings, get_course] | <tour>, <season>
```

## Rules
- Do not state causes the data does not carry (weather, pin positions, nerves).
- Say when hole-by-hole is not held for the tour or year.
- For a live event, name the round it is after and do not call it final.
- Every number names its tool (the Data line, plus inline where it could be doubted) and every rate shows its sample size.
- If a tool returns too little, say "not enough data" and stop; do not estimate or borrow another sample.
- Odds and prices are information about the market only: no picks, leans, stakes, payouts or sportsbook links.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.

## Example prompts
- "What happened at the Open this year?"
- "How did Scheffler win the Masters?"
- "Who made the move on Sunday at the PGA?"
