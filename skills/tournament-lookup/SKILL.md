---
name: tournament-lookup
description: "Finds golf tournaments and reads their results: season schedules, winners and winning scores, majors, what is on this week, defending champions, full leaderboards with cuts, rounds, earnings and playoffs, and the courses used. Use when the user asks who won, what a leaderboard looked like, where a tournament is played, or what is coming up on the PGA Tour, LPGA, LIV, DP World Tour or Korn Ferry Tour. Do not use for one player's career -- see player-scouting. Do not use for how a course played hole by hole -- see hole-scoring. Do not use for winner prices -- see odds-explorer."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Tournament Lookup

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `list_tournaments` (1 credit) and `get_schedule` (1 credit) find ids. `get_leaderboard` (2 credits) reads the result.

You are an expert at navigating a golf season. Your goal is to get the user from a loose question ("who won the Open in 2023", "what is on next week") to the exact tournament id and a clean, correct read of the result.

## When to Use

- Listing a season's tournaments, winners, purses, courses and field sizes
- Finding every major in a season, or the latest completed events
- What is being played now and next, and who is defending
- A full leaderboard: finishing position (T5), cut, withdrew, score to par, strokes, each round, earnings, season points, playoff
- Which course or courses a tournament used, and the cut line

## When NOT to Use

- A player's career, season or results list -- see `player-scouting`
- How individual holes played, or a player's hole-by-hole card -- see `hole-scoring`
- Pre-tournament winner prices -- see `odds-explorer`
- Ranking players by form -- see `strokes-vs-field`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `list_tournaments` | A season's tournaments (ascending) or the latest (descending), filter by `status` and `major` | 1 |
| `get_schedule` | Tournaments in play or starting in the next `days` (default 30), with courses and defending champion | 1 |
| `get_leaderboard` | Every player in a tournament in finishing order, with rounds and strokes versus the field | 2 |
| `get_course` | Par and yards per hole and how each hole played (use after you have the id) | 2 |

All four take `league` (`golf`, `lpga`, `liv`, `dpwt`, `kornferry`); the default is `golf`.

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_tournament`, `get_event` | `list_tournaments` (the row has winner, purse, cut, courses); `get_leaderboard` for the field |
| `get_live_leaderboard` | Not available; data is next-morning |
| `get_tee_times`, `get_pairings`, `get_weather` | Not available |
| `get_team_results` | LIV has individual results only; team scores are not in the data |
| `search_tournaments` | `list_tournaments` with `season`, `status`, `major` |

## How It Works

**Step 1: Resolve the tournament id.** Ids are strings like `"401580344"`. Never guess one.

```
list_tournaments {"season": 2024, "major": true}
```

Each row has `tournament_id`, `name`, `start_date`, `status`, `major`, `purse`, `field_size`, `cut_round`, `cut_score`, `cut_count`, `winner_name`, `winning_to_par`, `winning_strokes` and `courses[]` (with `course_id`, `par`, `yards`, `host`).

For "what is on now", use the schedule instead:

```
get_schedule {"days": 14}
```

Rows carry `status` (`live` or `scheduled`) and `defending_champion`.

**Step 2: Read the leaderboard.**

```
get_leaderboard {"tournament_id": "401580344", "limit": 5}
```

Real response shape (trimmed, 2024 Masters):

```
tournament: Masters Tournament, field_size 89, cut_count 50, winner Scottie Scheffler (-11, 277)
players[0]: position 1, status finished, to_par -11, total_strokes 277, earnings 3600000, cup_points 750
  rounds: R1 66 (vs_field 7.43), R2 72 (3.08), R3 71 (3.3), R4 68 (4.48)
```

`vs_field` on a round is the field's average that round minus the player's score. Positive is better. See `strokes-vs-field`.

**Step 3: Interpret the status.** `finished` made the cut and played the weekend; check `status` for cut, withdrawn and disqualified. A player who missed the cut has two rounds only, so do not compare his total strokes to a finisher's.

**Step 4: Handle multi-course events.** Some events use more than one course. `courses[]` lists them and each leaderboard round carries a `course_id`. Pass `course_id` to `get_course` so the right setup is used.

**Step 5: Playoffs and ties.** `tied` marks shared positions (T5). A playoff, if any, is returned with the leaderboard and flagged on the tournament row. Do not add playoff holes to the 72-hole total.

## Reading Season and League Rules

- Seasons are calendar years. Exceptions: the 2020 U.S. Open and November 2020 Masters are season 2021; Korn Ferry 2020 and 2021 are one combined season stored as 2020.
- LPGA, DP World Tour, LIV and Korn Ferry coverage has gaps in some seasons (for example LPGA 2013-2019 and DP World Tour 2019). If a season returns nothing, check the league page on birdieapi.com before assuming an error.
- Match play and team events have no stroke-play holes.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| One season's schedule and winners | 1 | `limit` default 60 |
| A leaderboard | 2 | add `limit` to cap the field |
| A season of leaderboards (about 45 events) | about 90 | warn first |
| Schedule | 1 | |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Answer "who won" from memory | The data may differ, and the user wants a sourced answer | Call `list_tournaments` |
| Treat `winning_to_par` as comparable across events | Par and setup differ | Use `strokes-vs-field` |
| Read a missed-cut player's strokes as a full result | Two rounds only | Check `status` |
| Pull a leaderboard for every event to find a player | 2 credits each | Use `get_player_results` |
| Read a `scheduled` event's leaderboard | There are no results yet | Check `status` first |

## Output Format

```
2024 Masters Tournament (Augusta National Golf Club, par 72, 7,555 yards)
Winner: Scottie Scheffler, -11 (277). Field 89, cut at 50.

1   Scottie Scheffler     -11  66 72 71 68   $3,600,000
2   Ludvig Aberg           -7  73 69 70 69   $2,160,000
T3  Tommy Fleetwood        -4  72 71 72 69   $1,040,000
...
Note: rounds shown are strokes; strokes versus the field is in the data.
```

Lead with the answer (winner, score, margin), then the table.

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A player of interest | Career and form | `player-scouting` |
| A tough or unusual course | Hole-by-hole difficulty | `hole-scoring` |
| A major coming up | Preview with form and prices | `tournament-preview` |
| Rounds with strong `vs_field` | Rate the performance | `strokes-vs-field` |
