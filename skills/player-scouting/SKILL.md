---
name: player-scouting
description: "Looks up and scouts golfers: finds a player id, reads career totals, season lines, recent results, round-by-round strokes versus the field, and compares two players head to head across the PGA Tour, LPGA, LIV, DP World Tour and Korn Ferry Tour. Use when the user names a golfer, asks how he or she has played, wants a career or season summary, or wants two players compared. Do not use for ranking the whole tour on form -- see strokes-vs-field. Do not use for a player's record at one course -- see course-fit. Do not use for tournament results -- see tournament-lookup."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Player Scouting

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `search_players` (1 credit) resolves a name. `get_player` (5), `get_player_results` (5), `get_player_stats` (5) and `get_head_to_head` (5) read the profile.

You are an expert golf scout. Your goal is to turn a name into a clear, sourced read on a player: how good, how recent, what kind of player, and how that compares with a rival.

## When to Use

- "How has Xander Schauffele played this year?"
- Career totals: starts, wins, top tens, cuts, money, scoring average, strokes versus the field
- A season line: scoring average, birdies per round, par 3/4/5 averages, driving and greens
- Recent form round by round, raw and adjusted for field strength
- Two players compared: who has finished ahead, round by round on the same course

## When NOT to Use

- Ranking everyone on one number -- see `strokes-vs-field`
- A player at one event or course across years -- see `course-fit`
- Who won a tournament -- see `tournament-lookup`
- A player's winner price -- see `odds-explorer`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `search_players` | Name to `player_id`, with country, tournaments played, wins, first and last season | 1 |
| `get_player` | Profile, career totals, our current rating, a line per season, last ten results | 5 |
| `get_player_results` | Tournament by tournament: finish, score, earnings, each round with field average, `vs_field` and `adj_vs_field`. Newest first | 5 |
| `get_player_stats` | One season: results, hole scoring, par-type splits, ball-striking lines where kept | 5 |
| `get_head_to_head` | Every tournament both played: who finished ahead and round-by-round strokes | 5 |
| `get_scorecard` | One tournament hole by hole (see `hole-scoring`) | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_player_by_name` | `search_players` with `query` (2 characters minimum, accents optional) |
| `get_world_ranking`, `get_owgr` | Not available; use `get_ratings` |
| Season stats with no season | `season` is required on `get_player_stats`; use `get_player` for career totals |
| `get_strokes_gained_by_category` | Not available; no shot data. `sg_par3/4/5` are score-based splits by hole type |
| `get_player_odds` | `get_winner_odds` with `player_id` (majors only) |

## How It Works

**Step 1: Resolve the id.**

```
search_players {"query": "scheffler"}
```

Real response (trimmed): `player_id "9478"`, `name "Scottie Scheffler"`, `country "USA"`, `tournaments 167`, `wins 23`, `first_season 2014`, `last_season 2026`. If several players match, ask or use `first_season`/`last_season` to pick. Add `league` to search another tour; ESPN ids are shared across tours.

**Step 2: Pull the season.**

```
get_player_stats {"player_id": "9478", "season": 2025}
```

Real response (trimmed):

```
results:      starts 21, wins 6, top_tens 18, made_cut 21, average_finish 5.9,
              scoring_average 67.94, vs_field 2.78, adj_vs_field 3.86, earnings 27659552
hole_scoring: birdies_per_round 4.762, par3_average 2.983, par4_average 3.889, par5_average 4.428,
              sg_par3 0.576, sg_par4 2.32, sg_par5 0.957
ball_striking: driving_distance 308.3, driving_accuracy 65.8, greens_in_regulation 71.6, putts_per_gir 1.69
```

`vs_field` is strokes per round better than the field average; `adj_vs_field` also corrects for how strong the fields were. The `sg_par*` fields are strokes versus the field by hole type, score-based. They are not shot-level strokes gained.

**Step 3: Recent form.** For the last N tournaments with every round:

```
get_player_results {"player_id": "9478", "season": 2025, "limit": 10}
```

Each tournament has `rounds[]` with `strokes`, `field_avg`, `vs_field`, `adj_vs_field`. Average the `adj_vs_field` of the last 8 to 12 rounds for form. Weak-field events (a 20-man invitational) inflate raw `vs_field`; trust `adj_vs_field` for comparison.

**Step 4: Compare two players.**

```
get_head_to_head {"player_a": "9478", "player_b": "3470", "season": 2025}
```

Real summary: `tournaments 13, a_ahead 8, b_ahead 4, tied 1, rounds 52, a_better_rounds 31, b_better_rounds 18, a_minus_b_strokes_per_round -0.65`. Read the sign carefully: `a_minus_b_strokes_per_round` is strokes, so negative means player A scored fewer strokes per round (better). Making the cut beats missing it when deciding who finished ahead.

**Step 5: Put it in context.** Pair the profile with `get_ratings` (2 credits) to rank the player on the whole tour, and note the sample (rounds behind each number). A 13-event head-to-head is small; say so.

## What a Good Scouting Note Contains

1. Identity and tour (id, country, seasons played)
2. Level: current rating and rank, and career `vs_field`
3. Form: last 8 to 12 rounds on `adj_vs_field`, with the dates
4. Profile: par-type split, birdie rate, bogey avoidance, and driving and greens if kept (PGA Tour from 2011)
5. Caveats: sample size, missing seasons, tour changes

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Find an id | 1 | |
| Quick scout (id, season stats, last 10 results) | 11 | |
| Full scout plus rating and one rival | 23 | adds `get_player`, `get_ratings`, `get_head_to_head` |
| Scout a 10-player shortlist | 110 | tell the user first |

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Guess an id from a name | Wrong player, silent error | `search_players` |
| Call `sg_par5` "putting" or "approach" | It is a hole-type split from scores | Name it "strokes versus the field on par 5s" |
| Compare a season of raw `vs_field` across tours | Each tour's fields differ | Use `adj_vs_field`, within one tour |
| Declare a head-to-head winner on 3 meetings | Tiny sample | Show the counts and the per-round gap |
| Quote a LIV player's rating beside a PGA Tour player's | Rated against different fields | Compare form on shared events (majors) with `get_head_to_head` |

## Output Format

```
Scottie Scheffler (USA, id 9478), 2025 PGA Tour
21 starts, 6 wins, 18 top tens, no missed cuts. Scoring average 67.94.
Strokes versus the field: +2.78 a round (+3.86 adjusted for field strength).
By hole type (score-based): par 3 +0.58, par 4 +2.32, par 5 +0.96 per round.
Sample: 84 rounds.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| Strong rating | See where he ranks and why | `strokes-vs-field` |
| An event is coming | Course record | `course-fit` |
| Want a market view | Winner prices | `odds-explorer` |
| Want to model win chance | Build inputs | `outright-model` |
