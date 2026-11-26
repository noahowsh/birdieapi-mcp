---
name: golf-tournament-preview
description: "Use when the user wants to get ready for a golf event, in fan or analyst wording: 'what's on this week', 'who should I watch at the Memorial', 'Masters primer', 'how strong is the field', 'LIV event preview', 'who are the contenders at the Open', 'DP World Tour preview', 'storylines for the PGA'. Use this whenever an upcoming golf event is the subject. Load it for short fragments and follow-ups too, even with no name given, instead of answering from memory or going straight to the raw tools. Produces a report: what's on, the strongest players by our strokes-versus-field rating, a one-line course-history note for the top names, and winner prices for the four men's majors. Not for how one named player has done at a course or event (see golf-course-history), simulated finish odds (see golf-finish-simulation), a recap (see golf-leaderboard-story), general form (see golf-strokes-vs-field) or modeling (see model-building)."
metadata:
  version: 2.1.0
  author: SportsDataHQ
---

# Golf tournament preview

A tournament preview from live BirdieAPI calls. The PGA Tour is the default; pass `league` for lpga, liv, dpwt or kornferry. It answers the questions a golf analyst asks first: how strong is the field, who is playing best by strokes gained against the field, what does this course reward, and how much does course history really add.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the BirdieAPI MCP server (`https://mcp.birdieapi.com/mcp`). Call them; never recall a ranking or result.
- Strokes versus the field (vs_field) = the field's average score that round minus the player's: positive is better. `adj_vs_field` also accounts for how strong the field was. Our rating is that number decay-weighted over recent rounds; 2.0 means two strokes a round better than an average player in the same fields.
- Seasons are tour season years; PGA Tour seasons from 2014 to 2024 began the October before. Winner prices exist only for the four men's majors; for other events say no prices are held.
- Coverage is thin for parts of the LPGA and DP World Tour history, and hole-by-hole strokes are held for the PGA Tour and Korn Ferry Tour only; say so when it matters.
- Weather is not in the data. Say so; do not guess wind or rain.

## Default path (about 35 credits with four names)
1. **What's on.** `get_schedule(days, league)` (1 cr): tournaments, courses, dates, purse, `field_size` (null until the field is out), cut rule and the defending champion. Note the tournament id and course id.
2. **Who's playing best.** `get_ratings(limit: 50, league)` (2 cr): top players by our rating with `weighted_rounds` and `rated_after` (the date of the last round in the rating). This is who is playing best, not the field.
3. **How the course played.** `get_course(tournament_id)` (2 cr): for a scheduled event the course has no rounds yet, so pass the last edition's tournament id (from `list_tournaments(season)`, 1 cr) to get par, yards, scoring average and each hole's birdie and bogey rates and difficulty rank.
4. **Last edition and field.** `get_leaderboard(tournament_id of the last edition, limit: 20)` (2 cr): winner, winning score, field size, cut line and each round's vs_field.
5. **Course or event history for 3 to 5 names.** `get_course_history(player_id, tournament_id or course_id)` (5 cr each): finishes, rounds and vs_field at this event or course across every year, with a summary.
6. **Fit for the course (optional).** `get_player_stats(player_id, season)` (5 cr): birdies and bogeys per round, par 3/4/5 scoring and, on the PGA and Korn Ferry Tours, vs_field by hole type (`sg_par3`, `sg_par4`, `sg_par5`; score based, not shot data).
7. **Prices (majors only).** `get_winner_odds(tournament_id)` (5 cr): opening and latest winner prices by book and the implied probability.

## Method
- **Rating reliability:** `weighted_rounds` is the sample. Under 20 is excluded by default; 20 to 60 is thin; 100 or more is stable. A single round varies by roughly 2.5 to 3 strokes, so the standard error of a rating is about 2.8 / sqrt(weighted_rounds): about 0.28 at 100 rounds. Two ratings closer than twice that are not separable.
- **Rust and recency:** days between `rated_after` and the first round. Over 60 days says the rating is stale or the player has been off; say which.
- **Rating gap to strokes:** over four rounds a rating gap of d strokes a round is 4d strokes. A tournament score has a standard deviation near 5.6 strokes for one player and 7.9 for the difference of two, so a 1.0-per-round edge (4 strokes) is about half a standard deviation: a modest favourite, never a lock.
- **Field strength:** mean rating of the 20 highest-rated entrants, and how many entrants have a rating of 1.5 or better. Compare with last year's field by running `get_ratings(as_of: <last year's start date>)`. Without a published field, say the field is not out and show last year's field strength and the top ratings as "if they enter".
- **Course profile:** par, yards, scoring average relative to par (negative is easy), birdie rate and bogey rate by hole type, and the hardest and easiest holes. A scoring average of 3 under par per round signals a birdie-fest where par-5 and wedge scoring matter; over par rewards bogey avoidance.
- **Course fit:** a player's `sg_par3/4/5` and birdie and bogey rates against the course's par-3, par-4 and par-5 difficulty, and the par-5 share of birdies. This is a fit story from scoring, not shot-level driving data.
- **Course history:** use the summary's `starts`, `average_finish` and `vs_field`. History is context, not an adjustment to the rating. Under 3 starts is an anecdote; 5 or more starts with vs_field consistently above the player's own rating is worth a line. Compare history vs_field with the rating, not with zero.
- **Prices (majors):** implied probability from the tool; no-margin = p / sum of p over every golfer listed for that book (ask for `limit: 200`). Report open, latest, move, and the gap to the rating-based ordering in words. Information only.

## Output template
```
<Tournament> | <course, par, yards> | <dates> | defending: <name> | field <n or "not out"> | cut: <rule>
Field strength: top-20 mean rating <x> (<n> players 1.5+), vs last year <y>
Form (our rating, strokes vs field per round): top 10 with weighted rounds and last-round date
Course: <scoring average vs par over n rounds>, hardest holes <list>, par 3/4/5 difficulty
Names to watch: <player: rating, rounds, course history (starts, wins, avg finish, vs_field), fit note>
Prices (majors only): <player: latest, no-margin %, moved from opening>
What to watch: 2-3 bullets from the numbers
Data: get_schedule, get_ratings, get_course, get_course_history[, get_winner_odds] | <tour>, <season>
```

## Worked example (live calls, Nov 25, 2026)
Hero World Challenge, Dec 3 to 6, 2026, Albany GC (Bahamas), par 72, 7,449 yards; defending champion Hideki Matsuyama; `field_size` is null, so the field is not out.
- Form (`get_ratings`, as of Nov 23): Scheffler 3.31 (133 weighted rounds), McIlroy 2.39, Fleetwood 2.19, Schauffele 2.18, Henley 2.02, Cantlay 2.02. Most were last rated after Aug 30, 87 days ago, so the list is stale and not a field. With about 120 to 130 rounds the rating error is near 0.25, so McIlroy to Cantlay are not separable.
- Course (last edition, `get_course` on the 2025 id): 80 rounds, scoring average 68.93, about 3.1 under par; toughest holes the 193-yard par-3 2nd and the par-4 16th. It plays as a birdie course.
- Last edition (`get_leaderboard`): 20-player field, no cut, Matsuyama won at 22 under in a playoff.
- History (`get_course_history` for Matsuyama): 1 start, 1 win, vs_field +2.43 per round (rounds 68, 66, 68, 64). One start is an anecdote; compare +2.43 with his own rating, not with zero.
- No prices: this is not one of the four men's majors.

## Not enough data
- Under 20 weighted rounds: unrated; under 60: "thin".
- Under 3 starts at the event or course: anecdote, no fit claim.
- Field not out (`field_size` null) or an invitational with no cut: say so; do not name a field. The top ratings are shown as "if they enter".
- No rounds yet on a scheduled event's course: use the last edition; if there was none, give par and yards only.
- LPGA, DP World Tour or LIV: round scores only, no hole-by-hole; no `sg_par` splits.
- A player off the tour data (new, amateur): say no rating.

## When the field isn't out

If the tournament is weeks away or its field isn't published, don't stop to ask. Preview what is known: the course (`get_course` on the last edition), last year's leaderboard there, and the leading players by rating with their history at the event, and say plainly that the field isn't confirmed. If the event already finished, give its result story instead.

## Rules
- Ratings need rounds: show how many. Under about 20 recent rounds, say the rating is unstable.
- Prices are information about the market only: no pick, stake or bet. Never name a book.
- Complete before writing: every step in the default path is called for both sides before the preview is written. If a call fails or returns nothing, say which section is missing rather than writing around it.
- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Rate limit: a "rate limit exceeded" reply is not a credit refusal. Wait a few seconds and retry that call once, one call at a time; if it still fails, name the section that is missing.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
