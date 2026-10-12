---
name: tournament-preview
description: "Builds a pre-tournament preview for a golf event: the course and its setup, the field's best players on rating and recent form, course record for the contenders, par-type strengths that suit the holes, and for the four men's majors the winner prices side by side. Use when the user asks for a preview of the Masters, PGA Championship, U.S. Open, Open Championship or any PGA Tour, LPGA, DP World Tour or Korn Ferry event, who the contenders are, or what to watch. Do not use for a single lookup -- see tournament-lookup or player-scouting. Do not use for devigging or stake sizing -- see odds-analysis and edge-detection."
metadata:
  version: 1.0.0
  author: BirdieAPI
---

# Tournament Preview

> **Default data tool:** BirdieAPI (`birdieapi-tool`).
> A preview is a compound skill that loads several tools. Budget about 40 to 60 credits. State the plan and the cost before pulling.

You are an expert golf analyst writing a preview. Your goal is a one-page read of who is playing well, who has a record here, what the course rewards, and (for majors) what the market thinks, with every claim sourced to a call and every caveat stated.

## When to Use

- "Preview this week's event."
- "Who are the contenders at the PGA Championship?"
- "Does the course suit a long hitter?" (the data supports par-type and hole-level reads, not driving distance by shot)

## When NOT to Use

- One fact (who won, a player's id) -- see `tournament-lookup`, `player-scouting`
- Win probabilities -- see `outright-model`
- Edge and staking -- see `edge-detection`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_schedule` | The event, dates, course, defending champion | 1 |
| `list_tournaments` | A prior edition's `tournament_id`, and cut data | 1 |
| `get_course` | The course as set up in a prior edition (par, yards, how each hole played) | 2 |
| `get_ratings` | Who is playing best, with `as_of` for a past preview | 2 |
| `get_course_history` | Contenders' record at the event | 5 each |
| `get_player_stats` | Par-type splits and ball-striking lines for a contender | 5 each |
| `get_head_to_head` | Two contenders against each other | 5 |
| `get_winner_odds` | Majors only: prices by book | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_field`, `get_entry_list` | Not available for an upcoming event; use the priced golfers (majors) or ask the user |
| `get_tee_times`, `get_pairings`, `get_weather` | Not available; say so |
| `get_preview`, `get_picks` | Compose it from the calls above |
| `get_odds` for non-majors | Not available; ask for the user's lines |

## How It Works

**Step 1: Identify the event and the course.**

```
get_schedule {"days": 14}
```

Rows give `tournament_id`, `start_date`, `status`, `courses[]` and `defending_champion`. For a past preview, use `list_tournaments` with the season.

**Step 2: Describe the course from the last edition.** The current week's setup is not published before play, so use the most recent edition on the same course.

```
get_course {"tournament_id": "401580344"}
```

Real response (2024 Masters): Augusta National, par 72, 7,555 yards, 298 rounds, scoring average 73.91. Hole 11 (par 4, 520 yards) ranked 1 in difficulty with a bogey rate of 0.2852; hole 13 (par 5, 545 yards) played to 4.758 with a birdie rate of 0.3624. Summarise: the hardest five holes, the number of par 5s that played under par, and the spread between the easiest and hardest. See `hole-scoring`.

**Step 3: Who is playing well.**

```
get_ratings {"as_of": "2024-04-04", "limit": 30}
```

Use `as_of` the day before play for a past preview so nothing after the event leaks in. For a live preview omit `as_of`. Real top of the list for the 2024 Masters:

```
1  Scottie Scheffler  2.88 (119 weighted rounds)
2  Jon Rahm           2.58 (114)
3  Xander Schauffele  2.48 (115)
4  Rory McIlroy       2.41 (91)
5  Patrick Cantlay    2.19 (101)
```

**Step 4: Course record for the top 6 to 10.**

```
get_course_history {"player_id": "9478", "tournament_id": "401580344"}
```

Seven starts, two wins, five top tens, average finish 7.9, +2.78 strokes versus the field per round at the event for Scheffler. Apply `course-fit` shrinkage before reading it as anything beyond form.

**Step 5: Par-type fit.** For two or three contenders, pull `get_player_stats` for the last full season and compare `sg_par3`, `sg_par4` and `sg_par5` with what the course rewards. These are score-based hole-type splits, not shot data.

**Step 6: Market (majors only).**

```
get_winner_odds {"tournament_id": "401580344", "limit": 10}
```

Put rating rank beside the latest pregame price. Real DraftKings latest prices against the ratings above:

```
Scheffler  +400   (20.0% raw)    rating 2.88
Rahm       +1200  (7.7% raw)     rating 2.58
Schauffele +2000  (4.8% raw)     rating 2.48
McIlroy    +1000  (9.1% raw)     rating 2.41
Cantlay    +2800  (3.4% raw)     rating 2.19
```

Raw implied probabilities include margin; devig before saying what the market believes (`odds-analysis`). A rating gap that the price does not reflect is a question to investigate, not a bet.

**Step 7: Head-to-head, if the user cares.** `get_head_to_head` for the two shortlisted contenders on the same season.

**Step 8: Write it up.** Short sections: Course, Form, Course record, Market, Risks. End with what the data cannot see: weather, injuries, withdrawals, wave draws, tee times.

## Credit Usage

| Operation | Credits | Notes |
|-----------|---------|-------|
| Event + prior-edition course | 4 | `get_schedule`, `get_course`, `list_tournaments` |
| Ratings | 2 | |
| Course history, 6 players | 30 | |
| Winner prices (majors) | 5 | |
| Par-type splits, 3 players | 15 | |
| Full preview | about 56 | |

On the free tier (500 credits a month) that is about nine previews.

## Anti-patterns

| What Claude Might Do | Why It's Wrong | Do This Instead |
|---------------------|---------------|-----------------|
| Name a "field" for an upcoming event | Not in the data | Say it is the priced golfers or the user's list |
| Use today's rating for a past preview | Leakage | `as_of` before round 1 |
| Say "suits his driving" | No driving by shot, only season lines and hole splits | State exactly what the splits show |
| Read a 4-start course record as destiny | Tiny sample | Show rounds and shrink |
| Give a pick | The data cannot see weather or injuries | Present contenders with risks |
| Quote odds for a non-major | Not held | Ask for the user's own lines |

## Output Format

```
2024 Masters preview (Augusta National, par 72, 7,555 yards)
Course: hole 11 hardest (bogey rate 28.5%), holes 2 and 13 (par 5s) play under par; round scoring average 73.91 in 2024.
Form (rating as of 4 Apr 2024): Scheffler 2.88, Rahm 2.58, Schauffele 2.48, McIlroy 2.41.
Course record (strokes versus the field per round): Scheffler +2.78 over 7 starts (2 wins).
Market (DraftKings latest): Scheffler +400, McIlroy +1000, Rahm +1200. Raw, not devigged.
Not in the data: weather, tee times, injuries, the confirmed field.
```

## What to Do Next

| What You Found | Next Action | Skill |
|----------------|-------------|-------|
| A contender list | Convert to probabilities | `outright-model` |
| A price gap | Devig and compare | `odds-analysis`, `edge-detection` |
| A course question | Hole-level detail | `hole-scoring` |
