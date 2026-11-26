---
name: golf-course-history
description: "Use when the user asks how a golfer has done at a course or event before, in fan or analyst wording: 'Cantlay at Torrey', 'does Schauffele like Riviera', 'is he a course horse', 'any good here?', 'his old finishes at Sawgrass', 'has he ever won at Bay Hill', 'cuts made at Pebble', 'what has he shot here'. Use this whenever a player is paired with a venue or event, or 'this course' is the subject. Load it for short fragments and follow-ups too, even with no name given, instead of answering from memory or going straight to the raw tools. Reports finishes and strokes versus the field at that event or course across years, then sets them against current form, because course fit is small. Not for a tournament preview (see golf-tournament-preview), current form or par-3 and par-5 scoring (see golf-strokes-vs-field), finish odds (see golf-finish-simulation) or one hole's difficulty."
metadata:
  version: 2.2.0
  author: SportsDataHQ
---

# Golf course history

Course history is the most overused number in golf talk. This skill reports a player's record at an event or course accurately, with rounds counted, and keeps it in its place beside recent form.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the BirdieAPI MCP server (`https://mcp.birdieapi.com/mcp`). Call them; never fill in a number from memory.
- Player ids from `search_players(query)` (1 cr); ids are the same on every tour. The PGA Tour is the default; pass `league` for lpga, liv, dpwt or kornferry. PGA Tour seasons from 2014 to 2024 began the October before (the 2015 season opened in October 2014).
- Course history can be pulled by tournament (any edition's id returns every edition) or by course (every tournament played there). A tournament on more than one course records which course each round was played on.
- Courses and renovations change; say when the course or its set-up changed in the window. Coverage is thin for parts of the LPGA and DP World Tour.

## Default path (about 15 credits per player)
1. **Resolve ids.** `search_players(query)` (1 cr); the tournament id from `list_tournaments(season)` (1 cr) or `get_schedule` (1 cr).
2. **The record.** `get_course_history(player_id, tournament_id or course_id)` (5 cr): finishes, rounds and strokes versus the field by year, with a summary.
3. **Current form.** `get_player_results(player_id, season, limit: 10)` (5 cr) for the latest starts, and `get_ratings()` (2 cr) for our decay-weighted rating.
4. **The course (optional).** `get_course(tournament_id)` (2 cr): how each hole played, to say what the course asks for.

## How to weigh it
Course fit is real but small. Recent form (our rating, recent adjusted strokes versus the field) explains more of the next result than the record at one course. Give history as context, with rounds: for example "top 10 in 4 of 6 starts here, +1.8 strokes versus the field per round over 22 rounds". Under 3 starts or about 12 rounds, say the history is too thin to mean anything. Do not put history ahead of form in the report.

## Output template
```
<Player> at <event or course> | starts <n>, rounds <n>, <first year>-<last year>
Finishes: <year: finish> ... | best <x> | cuts made <a>/<b>
Strokes vs field per round here: <v> over <rounds> (his season level: <v>)
Current form: our rating <v> over <rounds> | last 5 starts <finishes>
Read: history is <thin / consistent>; form says <...> (form first)
Data: search_players, get_course_history, get_player_results, get_ratings | <tour>, <season>
```

## Rules
- Always show the player's own season level beside the course number; a good course record from a generally good player says little.
- Name changes to the course or to the field when they matter.
- No winner prices from this skill; for a major's prices see golf-tournament-preview.
- Every number names its tool (the Data line, plus inline where it could be doubted) and every rate shows its sample size.
- If a tool returns too little, say "not enough data" and stop; do not estimate or borrow another sample.
- Odds and prices are information about the market only: no picks, leans, stakes, payouts or sportsbook links.
- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.

## Example prompts
- "How has Scheffler done at Augusta?"
- "Does Rory like Riviera?"
- "Course history for everyone in the top 10 at the Players"
