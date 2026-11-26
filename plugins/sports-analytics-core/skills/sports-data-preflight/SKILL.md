---
name: sports-data-preflight
description: "Use when a sports number looks wrong or the data may not line up, in plain wording: 'why don't these numbers match', 'is this the right season', 'I joined two tables and lost rows', 'duplicate players in my data', 'two players share a name, which one', 'is this the NHL or the minors', 'my totals are off by a few games', 'does this date belong to last season', 'is this enough games to say anything'. Use this whenever ids, season convention, league, joins, duplicates or sample size could be the problem, and before comparing players across seasons or careers, for any sport. Checks ids, season convention, league, duplicates and sample size, and says not enough data when it is. Not for a plain single lookup (call the tool directly), explaining a stat or building a model (see model-building)."
metadata:
  version: 2.1.0
  author: SportsDataHQ
---

# Sports data preflight

Most wrong answers in sports analysis come from the data step, not the math: the wrong player with the same name, a season boundary off by one, a league mixed in, a game counted twice, or a conclusion drawn from eight games. Run this checklist before you compute anything.

## The five checks

1. **Resolve every entity to an id with a search call.** Never pass a name where a tool wants an id, and never guess an id.
   - Players: `search_players` (or `search_fighters` for UFC). If two results match, show both and ask, or pick by team and position and say so.
   - Teams: the sport's `list_teams`; most tools also accept the team abbreviation.
   - Games, matches, fights: get the id from `get_schedule`, `get_games`/`list_games`/`get_matches`, or the event (`get_event`, `get_tournament`).
2. **Pin the season convention for the sport** and say it in the answer:

   | Sport | `season` means |
   |---|---|
   | NHL | 8-digit id, start year + end year (20252026) |
   | NFL, college football | the year the regular season starts (2025 = 2025-26) |
   | NBA, college basketball | the year the season ends (2026 = 2025-26); WNBA calendar year |
   | MLB, college baseball | calendar year |
   | Soccer | the year the season starts (2025 = 2025-26); MLS, NWSL, Liga MX, Brazil, Argentina calendar year |
   | Tennis, UFC | calendar year |
   | Golf | tour season year (PGA Tour 2014 to 2024 seasons began the previous October) |
   | Cricket | a year (2024) or split season (2024/25) |
3. **Confirm the league.** Multi-league APIs default to the flagship (NHL, NFL, NBA, MLB, Premier League, ATP, PGA Tour). Pass `league` explicitly when the user means another, and never mix leagues in one average.
4. **Deduplicate.** Count each game once per team or player; drop rows repeated across pages; for odds, one row per bookmaker per snapshot unless the user asked for all.
5. **Decide if there is enough data.** State the sample size beside every rate. Rough floors before a rate means much: 10+ games for team form, 20+ games or 200+ plate appearances or 100+ shots for a player rate, 30+ balls for a batter vs bowler matchup, 50+ cases for any backtest. Below the floor, say "not enough data to say" and show the raw counts instead.

## While you analyze

- Call the tools; do not answer from memory. Sports facts change daily and models invent plausible numbers.
- Name the tool call behind each number ("from get_team_stats, 2025 season").
- Keep credit costs in mind: list and search calls cost 1 to 2 credits, play-level calls 10, line movement and backtests up to 25. Pull a season once and reuse it rather than one call per game.
- Odds and prices are information about the market, never a recommendation.

## Output

Start the answer with one line: `Data: <tools used>, <season(s) and league>, <sample size>.` Then the analysis.

## Credits

- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
