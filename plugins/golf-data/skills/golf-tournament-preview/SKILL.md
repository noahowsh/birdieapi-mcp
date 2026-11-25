---
name: golf-tournament-preview
description: "Use when the user wants a preview of a golf tournament or a player's chances: 'preview this week's PGA Tour event', 'who's playing best going into the Masters', 'course history at Augusta for Scheffler', 'field strength this week', 'LPGA preview'. Produces a report: what's on, the strongest players by our strokes-versus-field rating, course or event history for the names that matter, and winner prices for the four men's majors. Not for a finished tournament's leaderboard (call get_leaderboard) or modeling (see model-building)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Golf tournament preview

A tournament preview from live BirdieAPI calls. The PGA Tour is the default; pass `league` for lpga, liv, dpwt or kornferry.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the BirdieAPI MCP server (`https://mcp.birdieapi.com/mcp`). Call them; never recall a ranking or result.
- Strokes versus the field (vs_field) = the field's average score that round minus the player's: positive is better. Our rating is that number decay-weighted over recent rounds; 2.0 means two strokes a round better than an average player in the same fields.
- Winner prices exist only for the four men's majors. Other events: say no prices are held.
- Coverage is thin for parts of the LPGA and DP World Tour history; say so when it matters.

## Default path (about 20 credits)
1. **What's on.** `get_schedule(days)` (1 cr): tournaments, courses, defending champion. Note the tournament id.
2. **Who's playing best.** `get_ratings(limit: 30)` (2 cr): top players by our rating with rounds counted.
3. **Course or event history.** `get_course_history(player_id, tournament_id or course_id)` (5 cr) for the 3-5 names the user cares about: finishes and strokes vs field at this event or course.
4. **Course profile (optional).** `get_course(tournament_id)` (2 cr): how each hole played.
5. **Prices (majors only).** `get_winner_odds(tournament_id)` (5 cr): opening and latest winner prices by book, and movement.

## How to weigh course history
Course fit is real but small: recent form (our rating) matters far more than history at one course. Give history as context ("finished top 10 here in 4 of 6 starts, +1.8 strokes vs field per round") and never as the headline.

## Output template
```
<Tournament> | <course> | <dates> | defending: <name>
Form (our rating, strokes vs field per round): top 10 with rounds counted
Names to watch: <player: rating, course history line>
Prices (majors only): <player: latest price, moved from opening>
What to watch: 2-3 bullets from the numbers
Data: get_schedule, get_ratings, get_course_history[, get_winner_odds] | <tour>, <season>
```

## Rules
- Ratings need rounds: show how many. Under ~20 recent rounds, say the rating is unstable.
- Prices are information about the market only: no pick, stake or bet.
