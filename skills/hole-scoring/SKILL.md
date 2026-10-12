---
name: hole-scoring
description: "Analyses golf scoring at hole level: par 3, par 4 and par 5 averages and strokes-versus-field splits (sg_par3, sg_par4, sg_par5), birdie and bogey rates, how each hole of a course played, and one player's hole-by-hole scorecard. Use when the user asks who is best on par 5s, which holes play hardest, how a course was set up, what a player shot on each hole, or what kind of scorer a golfer is. Do not use for tournament-wide results -- see tournament-lookup. Do not use for the official shot-level strokes gained categories -- they are not in the data. Do not use for a player's record at a course across years -- see course-fit."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Hole Scoring

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> `get_player_stats` (5 credits) has the par-type splits. `get_course` (2) has how each hole played. `get_scorecard` (2) has one player's holes. `get_leaders` (5) ranks a season.

You are an expert in how golf is scored hole by hole. Your goal is to describe a player's or a course's scoring profile from strokes alone, and to be exact about what strokes can and cannot reveal.

## What is in the data

- Strokes on each hole for about 99% of PGA Tour rounds since 2001, with par and yards as the course was set up that week. Korn Ferry Tour has hole-by-hole from 2007.
- **Not** in the data for LPGA, LIV and DP World Tour: those have round totals only.
- No shot locations, no shot lengths, no categories. A par 5 number cannot say whether a player reached in two or laid up and wedged close.
- `sg_par3`, `sg_par4`, `sg_par5` are strokes versus the field on that hole type, field-strength adjusted, PGA Tour and Korn Ferry Tour only. Score-based, not shot data. The three add up to the round's strokes versus the field.

## When to Use

- "Who is the best par-5 scorer in 2025?"
- "Which holes at Augusta played hardest?"
- "Show Scheffler's Thursday round hole by hole."
- Birdie machine versus bogey avoider
- Course setup: par and yards per hole, scoring average, birdie and bogey rates

## When NOT to Use

- Overall form rating -- see `strokes-vs-field`
- A player at one event over years -- see `course-fit`
- Tournament results -- see `tournament-lookup`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_player_stats` | A season's hole scoring: birdies and bogeys per round, par 3/4/5 averages, `sg_par*` | 5 |
| `get_leaders` | Season leaders on `par3_average`, `par4_average`, `par5_average`, `sg_par3`, `sg_par4`, `sg_par5`, `birdies_per_round`, `bogey_avoidance` | 5 |
| `get_course` | Per hole: par, yards, scoring average, to par, birdie, par, bogey and double rates, difficulty rank | 2 |
| `get_scorecard` | One player's holes for every round: strokes, par, yards, result, out and in | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_hole_stats`, `get_hole` | `get_course` returns every hole |
| `get_shot_data`, `get_shot_tracking` | Not available |
| `get_strokes_gained_putting` | Not available; `putts_per_gir` is a stat line (PGA Tour, from 2011) |
| Scorecards for LPGA, LIV, DPWT | `get_scorecard` accepts `golf` and `kornferry` only |

## How It Works

**Step 1: A player's profile.**

```
get_player_stats {"player_id": "9478", "season": 2025}
```

Real response (trimmed), Scottie Scheffler 2025, 84 rounds with holes:

```
birdies_per_round 4.762   eagles_per_round 0.202   bogeys_or_worse_per_round 1.917   par_rate 0.6177
par3_average 2.983   par4_average 3.889   par5_average 4.428
sg_par3 0.576   sg_par4 2.32   sg_par5 0.957
```

Read it: the three splits sum to 3.853, which matches his `adj_vs_field` of 3.86 in the same response, and the par-4 split carries about 60% of it. Par 4s are about ten holes a round and par 3s and 5s about four each, so per hole the par-3 split (0.58 over four holes) is the weakest and par 4 and par 5 are close (about 0.23 and 0.24 a hole). That is arithmetic on his splits, not shot data.

**Step 2: Rank a season on a hole type.**

```
get_leaders {"stat": "sg_par5", "season": 2025, "limit": 3}
```

Real response: Scheffler 0.957 (84 rounds), Schauffele 0.88 (64), McIlroy 0.807 (58). Default minimum is 40 rounds. Par 3 and par 5 numbers rest on fewer holes per round, so they move more round to round. Use a full season, and treat gaps under about 0.1 as ties.

**Step 3: How a course played.**

```
get_course {"tournament_id": "401580344"}
```

Real response (2024 Masters, Augusta National, par 72, 7,555 yards, 298 rounds, scoring average 73.91). For the 11th: par 4, 520 yards, scoring average 4.386, bogey rate 0.2852, double or worse 0.0738, `difficulty_rank` 1. For the 13th: par 5, 545 yards, scoring average 4.758, birdie 0.3624, `difficulty_rank` 16. For tournaments on more than one course, pass `course_id`.

Course difficulty: sort holes by `to_par`, take the top and bottom five, and split by par type. Do not compare scoring averages across different weeks without setting them against the field.

**Step 4: One player's hole-by-hole.**

```
get_scorecard {"tournament_id": "401580344", "player_id": "9478"}
```

Real response (round 1): 66, out 34, in 32, `field_avg` 73.43, `vs_field` 7.43. Each hole has `par`, `yards`, `strokes`, `result` (par, birdie, bogey). Round 1: birdies on 2 (par 5), 6, 12, 13, 15 and 16. Summarise by par type:

```python
import collections
agg = collections.defaultdict(lambda: [0, 0])   # par -> [strokes, holes]
for r in card["rounds"]:
    for h in r["holes"]:
        agg[h["par"]][0] += h["strokes"]; agg[h["par"]][1] += 1
avg_by_par = {p: s / n for p, (s, n) in agg.items()}
```

**Step 5: Scorer type.** Birdies per round measures aggression; `bogey_avoidance` measures mistakes. Two golfers at the same rating can differ in both. For setups with penal rough or firm greens the bogey-avoider tends to hold up better; say this as a hypothesis for `course-fit` to test, not a rule.

## Pitfalls

| Pitfall | Why it bites |
|---------|--------------|
| Calling `sg_par5` an approach or driving stat | It only says the player scored better than the field on par 5s |
| Using one tournament's par-3 average | Four holes a round, 16 holes total: very noisy |
| Comparing hole averages across course setups | Yards, pins and weather change |
| Dividing `sg_par*` by holes and quoting as per-shot | They are per round totals |
| Expecting hole data for LPGA, LIV, DPWT | Round scores only |
| Using `get_scorecard` on a match-play event | No stroke-play holes |

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Player season profile | 5 | |
| Season leaders, one stat | 5 | |
| Course hole table | 2 | |
| One player's tournament card | 2 | all four rounds |
| Profile + course + card | 9 | a typical "how does he fit this course" check |

## Output Format

```
Scottie Scheffler, 2025 PGA Tour (84 rounds)
Strokes versus the field by hole type (score-based): par 3 +0.58, par 4 +2.32, par 5 +0.96 per round.
Birdies per round 4.76, bogeys or worse 1.92. Par 4 scoring average 3.889.
No shot data: these show where strokes were saved, not how.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A course with scoreable par 5s | Does the player's par-5 split fit? | `course-fit` |
| A scoring profile | Overall form | `strokes-vs-field` |
| Want features for a model | Build inputs | `feature-engineering` |
