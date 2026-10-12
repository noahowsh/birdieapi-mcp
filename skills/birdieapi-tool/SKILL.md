---
name: birdieapi-tool
description: "Default data source for the BirdieAPI skills. Routes every call to the 14 BirdieAPI tools for PGA Tour, LPGA, LIV, DP World Tour and Korn Ferry Tour tournaments, leaderboards, scorecards, courses, player results, ratings and the winner prices of the four men's majors. Use when any other skill needs golf data, or when the user asks which tool to call, what a call costs, or how to connect. Do not use for analysis, modeling or bet sizing -- see strokes-vs-field, outright-model or edge-detection."
metadata:
  version: 1.0.0
  author: BirdieAPI
  user-invocable: false
---

# BirdieAPI Tool

Every other skill delegates data retrieval here. This skill owns the 14 tools, the credit costs, the league switch and the response envelope.

**Coverage (from birdieapi.com/data and the league pages, check them before quoting a number):**

| Dataset | What is there |
|---------|---------------|
| PGA Tour leaderboards and results | Every player in every field since 2001 |
| PGA Tour hole-by-hole scores | About 99% of PGA Tour rounds since 2001, with par and yards per hole |
| PGA Tour tournament stat lines | Driving distance and accuracy, greens in regulation, putts per green, sand saves, from 2011 |
| Major winner odds | The four men's majors, weekly snapshots from 2021 (plus the 2020 U.S. Open) |
| LPGA, LIV, DP World Tour | Leaderboards, round scores and the rating. No hole-by-hole, no odds |
| Korn Ferry Tour | Leaderboards, round scores and hole-by-hole from 2007. No odds |

Data is public ESPN data loaded and checked by BirdieAPI. It is historical and next-morning, not a live feed.

## Connecting

- **MCP:** `https://mcp.birdieapi.com/mcp` (Streamable HTTP). Claude Code: `claude mcp add --transport http birdieapi "https://mcp.birdieapi.com/mcp?key=YOUR_API_KEY"`.
- **REST:** `POST https://mcp.birdieapi.com/v1/<tool>` with a JSON body and header `x-api-key: YOUR_API_KEY`.
- **Free tier:** 500 credits every month, no card. Key at https://birdieapi.com/signup. Paid plans are on https://birdieapi.com/pricing.
- **Response envelope:** every REST response is wrapped as `{"data": {...}}`. Unwrap `data` before reading fields.

## When to Use Each Tool

| Task | Tool | Credits |
|------|------|---------|
| Find tournament ids for a season, winners, courses, majors | `list_tournaments` | 1 |
| What is on this week and next, defending champion | `get_schedule` | 1 |
| Find a player id from a name | `search_players` | 1 |
| Full results of one tournament | `get_leaderboard` | 2 |
| How each hole of a course played | `get_course` | 2 |
| One player's hole-by-hole card | `get_scorecard` | 2 |
| Who is playing best, on one rating | `get_ratings` | 2 |
| Player overview, career totals, last ten results | `get_player` | 5 |
| Player's tournament-by-tournament rounds and strokes vs field | `get_player_results` | 5 |
| Player's season: par 3/4/5 splits, birdies, driving, greens | `get_player_stats` | 5 |
| Player's record at one event or course across years | `get_course_history` | 5 |
| Two players in every tournament both played | `get_head_to_head` | 5 |
| Season leaders in one stat | `get_leaders` | 5 |
| Major winner prices by sportsbook, opening and latest | `get_winner_odds` | 5 |

## The league switch

Most tools take `league`: `golf` (the default, the PGA Tour), `lpga`, `liv`, `dpwt`, `kornferry`.

- `get_scorecard` takes only `golf` or `kornferry`.
- `get_winner_odds` has no `league` argument. It holds the four men's majors only.
- The `sg_par3`, `sg_par4`, `sg_par5` stats exist for the PGA Tour and Korn Ferry Tour only. Other tours return null.
- Ratings are measured within one tour. A 2.0 on the LPGA and a 2.0 on the PGA Tour are not on one scale.
- Player ids are ESPN's and are shared across tours, so a player's results on two tours join on one id.

## Identifiers and seasons

- `tournament_id`, `player_id` and `course_id` are strings. Never guess one: get it from `list_tournaments`, `get_schedule`, `search_players` or `get_leaderboard`.
- `season` is a calendar year (a September 2025 event is season 2025). Exceptions from the site: the 2020 U.S. Open and the November 2020 Masters are season 2021; Korn Ferry 2020 and 2021 are one combined season stored as 2020.
- Paged tools (`list_tournaments`, `get_player_results`) return `next_offset`. Pass it as `offset` for the next page.

## Tool Selection Guide

| You Need | Use This | Not This |
|----------|----------|----------|
| "What is on this week?" | `get_schedule` | `list_tournaments` (a whole season) |
| "Who won the 2024 PGA Championship?" | `list_tournaments` with `season` and `major` | `get_leaderboard` (2 credits for a winner you can read in a row) |
| "Full results of the Masters" | `get_leaderboard` | `get_player_results` per player |
| "Find Rory McIlroy's id" | `search_players` | `get_player` (needs the id) |
| "How has Scheffler played this year?" | `get_player_stats` with `season` | `get_player` (career overview) |
| "Best par-5 scorers of 2025" | `get_leaders` with `stat` `sg_par5` | `get_player_stats` per golfer |
| "Which holes at Augusta were hardest?" | `get_course` | `get_scorecard` |
| "Scheffler's round 1 hole by hole" | `get_scorecard` | `get_course` |
| "How does he do at Pebble Beach?" | `get_course_history` | `get_player_results` filtered by hand |
| "Scheffler versus McIlroy" | `get_head_to_head` | two `get_player_results` calls |
| "Who is best right now?" | `get_ratings` | `get_leaders` (a season stat) |
| "What was he priced at for the Masters?" | `get_winner_odds` | nothing else has prices |

## Calling Patterns

Example calls in the skills are written as the tool name followed by its JSON arguments. Over MCP pass the arguments object. Over REST send it as the body:

```
search_players {"query": "scheffler"}
get_ratings {"limit": 5}
get_winner_odds {"tournament_id": "401580344", "limit": 5}
```

```bash
curl -s -X POST https://mcp.birdieapi.com/v1/search_players \
  -H "x-api-key: $BIRDIEAPI_API_KEY" -H "content-type: application/json" \
  -d '{"query": "scheffler"}'
```

Real response, unwrapped from `{"data": ...}` and trimmed:

```
players[0]: player_id "9478", name "Scottie Scheffler", country "USA", tournaments 167, wins 23, first_season 2014, last_season 2026
```

Chain the ids: `search_players` gives `player_id`, `list_tournaments` gives `tournament_id`, and the 2-credit and 5-credit tools take those.

## Errors and empty results

- A missing key or a spent balance returns an error rather than data. Tell the user which, and point to https://birdieapi.com/pricing for the credit plans.
- An empty list for a season usually means the league has no data there (for example the LPGA between 2013 and 2019). Check the league page before assuming a bug.
- A null `sg_par3`, `sg_par4` or `sg_par5` means the tour is not the PGA Tour or Korn Ferry Tour.
- Do not retry a failed call in a loop. Each attempt can spend credits.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Resolve a name to an id | 1 | `search_players` |
| One tournament leaderboard | 2 | whole field unless `limit` is set |
| One player card | 2 | `get_scorecard` |
| One player's season | 5 | `get_player_stats` |
| One major's winner market, 200 golfers | 5 | `limit` does not change the price |
| A full 10-year course-history table for 40 golfers | 200 | 5 per golfer; warn first |

Free tier: 500 credits is about 100 five-credit calls a month. Tell the user the running total on any multi-call plan.

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_strokes_gained`, `get_sg_categories` | `get_ratings`, `get_player_results` (`vs_field`, `adj_vs_field`) and `get_leaders` with `sg_par3/4/5`. There is no shot-level data, so no off-the-tee, approach or putting split |
| `get_live_scores`, `get_live_leaderboard` | Not available. Data is next-morning; Data is next-morning, so check `status` from `list_tournaments` (scheduled, live, final) before reading a leaderboard as final |
| `get_odds`, `get_matchup_odds`, `get_top_10_odds` | Only `get_winner_odds`, and only for the four men's majors |
| `get_world_ranking` | Not available. Use `get_ratings` (our own rating) |
| `get_team_standings` | Not available. LIV has individual results only |
| `get_weather`, `get_tee_times`, `get_pairings` | Not available |
| `get_field` | A field is the `players` list of `get_leaderboard` once a tournament has results |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Call it "strokes gained" | The rating is the site's own strokes-versus-field number built from scores, not the official shot-level stat | Say "strokes versus the field"; see `strokes-vs-field` |
| Pass a name as `player_id` | IDs are numeric strings | `search_players` first |
| Pull `get_course_history` for a whole field | 5 credits each | Shortlist with `get_ratings` first |
| Quote the latest winner price as the closing line | For past majors it can be up to a week before the first tee | Call it the latest pregame snapshot |
| Compare an LPGA rating to a PGA Tour rating | Each is relative to its own tour | Compare within a tour |

## BYOD

If the user brings their own round scores or odds, skip the tools and spend no credits. Minimum columns: rounds need `player`, `tournament`, `round`, `strokes`, `course`, `date`; odds need `player`, `book`, `american_price`, `timestamp`. Say when a column had to be inferred.

## What to Do Next

| What You Retrieved | Next Action | Skill |
|--------------------|-------------|-------|
| Tournament list or leaderboard | Read the result, find the course | `tournament-lookup` |
| Player id | Scout the player | `player-scouting` |
| Ratings or round-level strokes vs field | Interpret and compare | `strokes-vs-field` |
| Hole data | Par-type and hole analysis | `hole-scoring` |
| Winner prices | Compare books, movement | `odds-explorer` |
| Prices plus a model | Find edge | `edge-detection` |
