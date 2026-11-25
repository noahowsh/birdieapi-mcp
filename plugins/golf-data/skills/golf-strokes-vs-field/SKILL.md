---
name: golf-strokes-vs-field
description: "Use when the user wants to know how a golfer is really playing or how golfers compare: 'who is playing best', 'strokes gained for Scheffler', 'is he good on par 5s', 'rank the field by scoring versus the field', 'is his form real', 'how does he score on par 3s'. Reports strokes versus the field per round (raw and field-strength adjusted), by hole type on the PGA Tour, with rounds counted. Not for a tournament preview (see golf-tournament-preview), a player's record at one course (see golf-course-history) or modeling (see model-building)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# Golf strokes versus the field

Strokes versus the field is the field's average score on the same course that round minus the player's score; positive is better. It is the best single measure of how someone is scoring. This skill reports it and its parts, from BirdieAPI.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the BirdieAPI MCP server (`https://mcp.birdieapi.com/mcp`). Call them; never fill in a number from memory.
- Player ids from `search_players(name)` (1 cr); ids are the same on every tour. The PGA Tour is the default; pass `league` for lpga, liv, dpwt or kornferry. PGA Tour seasons from 2014 to 2024 began the October before (the 2015 season opened in October 2014).
- `vs_field` is raw; `adj_vs_field` also accounts for how strong the field was. Our rating is the same number decay-weighted over recent rounds.
- The hole-type splits (`sg_par3`, `sg_par4`, `sg_par5`) are score-based and available for the PGA Tour and Korn Ferry Tour only. Shot-level strokes gained (off the tee, approach, around the green, putting) are not in the data; do not report them.
- Hole-by-hole strokes exist for the PGA Tour (2001 on) and Korn Ferry Tour; the LPGA has them only for 2013-16 and some 2026 events; DP World Tour and LIV have round scores only. Coverage on those tours is thin in places; say so.

## Default path (about 18 credits)
1. **Resolve the player.** `search_players(name)` (1 cr).
2. **Season numbers.** `get_player_stats(player_id, season)` (5 cr): scoring average, strokes versus the field, birdies and bogeys per round, and by hole type on the PGA Tour.
3. **Round by round.** `get_player_results(player_id, season, limit)` (5 cr): each tournament's rounds with the field's average and strokes versus the field, raw and adjusted, for form over time.
4. **Where he ranks.** `get_leaders(stat: "adj_vs_field", season)` (5 cr), and `sg_par3`, `sg_par4` or `sg_par5` for the hole type asked about. Use `min` to set a rounds floor.
5. **Current form (optional).** `get_ratings()` (2 cr): our decay-weighted rating for the top players, with rounds counted.

## Reading it
2.0 means two strokes a round better than the average player in the same fields. Season numbers over fewer than 40 rounds are unstable; say so. Compare players only on the same tour and season (field strength differs by tour). Hole-type splits are noisier than the total: a par-5 edge over one season can be luck.

## Output template
```
<Player> | <tour, season> | rounds <n>, starts <n>
Strokes vs field per round: raw <v> | field-strength adjusted <v> (rank <r> of <q> with at least <min> rounds)
By hole type (PGA/KF only, score-based): par 3 <v> | par 4 <v> | par 5 <v>
Recent form: <last 5 starts: finish, adjusted strokes vs field per round> | our rating <v> over <rounds>
Read: 2-3 bullets with rounds counted
Data: search_players, get_player_stats, get_player_results, get_leaders | <tour>, <season>
```

## Rules
- Say raw or adjusted for every strokes figure.
- Show rounds beside every rating or rank; under about 20 recent rounds the rating is unstable.
- Never report shot-level strokes gained; the data is score-based.
- Every number names its tool (the Data line, plus inline where it could be doubted) and every rate shows its sample size.
- If a tool returns too little, say "not enough data" and stop; do not estimate or borrow another sample.
- Odds and prices are information about the market only: no picks, leans, stakes, payouts or sportsbook links.

## Example prompts
- "How is Scottie Scheffler playing this season?"
- "Who is best on par 5s on the PGA Tour?"
- "Strokes versus the field for Rory over his last five starts"
