# BirdieAPI skills

Sixteen free Claude skills that turn Claude into a golf analyst on top of the [BirdieAPI](https://birdieapi.com) tools: PGA Tour, LPGA, LIV, DP World Tour and Korn Ferry Tour results, hole-by-hole scorecards, courses, a strokes-versus-field rating, and the winner prices of the four men's majors.

Each skill is a folder with a `SKILL.md`: when to use it, which tools it calls and what they cost, the method (formulas, pitfalls, sample-size warnings), a worked example from real responses and an output format. Point Claude at this folder, or copy the folders you want into your skills directory.

## Setup

1. Clone the repository: `git clone https://github.com/noahowsh/birdieapi-mcp.git`
2. Connect the data (optional; the method skills also work on your own files):
   `claude mcp add --transport http birdieapi "https://mcp.birdieapi.com/mcp?key=YOUR_API_KEY"`
3. Get a key at https://birdieapi.com/signup. The free tier is 500 credits every month, no card. Plans are on https://birdieapi.com/pricing.
4. Ask a question. Start with `dispatch` if you are not sure which skill fits.

## Catalog

| Skill | Category | What it does |
|-------|----------|--------------|
| [`tournament-lookup`](tournament-lookup/SKILL.md) | Data Exploration | Find tournaments, winners, schedules and full leaderboards on every tour |
| [`player-scouting`](player-scouting/SKILL.md) | Data Exploration | Player ids, career and season lines, recent rounds and head-to-head |
| [`odds-explorer`](odds-explorer/SKILL.md) | Data Exploration | Compare major winner prices across books and read how they moved |
| [`tournament-preview`](tournament-preview/SKILL.md) | Data Exploration | Course, form, course record and market in one pre-tournament read |
| [`strokes-vs-field`](strokes-vs-field/SKILL.md) | Golf Analytics | Rate and rank golfers on strokes versus the field, adjusted for field strength |
| [`hole-scoring`](hole-scoring/SKILL.md) | Golf Analytics | Par 3/4/5 splits, birdie and bogey rates, hole difficulty and scorecards |
| [`course-fit`](course-fit/SKILL.md) | Golf Analytics | A player's record at one event or course, shrunk toward general form |
| [`outright-model`](outright-model/SKILL.md) | Golf Analytics | Simulate a tournament from ratings and compare with the devigged market |
| [`feature-engineering`](feature-engineering/SKILL.md) | Methodology | Leak-free golf features: as-of ratings, rolling form, course history |
| [`walk-forward-validation`](walk-forward-validation/SKILL.md) | Methodology | Time-ordered, tournament-grouped testing with a market baseline |
| [`probability-calibration`](probability-calibration/SKILL.md) | Methodology | Reliability checks for made-cut, top-10 and winner probabilities |
| [`odds-analysis`](odds-analysis/SKILL.md) | Methodology | Implied probability, overround and devigging for a 100-runner outright |
| [`edge-detection`](edge-detection/SKILL.md) | Betting | EV, joint Kelly on mutually exclusive winners and sample-size reality |
| [`backtesting`](backtesting/SKILL.md) | Betting | Test rules on past majors with bootstrap intervals; bet log template |
| [`dispatch`](dispatch/SKILL.md) | Workflow | Routes a golf request to the right 2-3 skills |
| [`birdieapi-tool`](birdieapi-tool/SKILL.md) | Infrastructure | All 14 BirdieAPI tools, credits, the league switch and the data envelope |

## What the data is, and is not

- Historical and next-morning data from public ESPN sources, loaded and checked by BirdieAPI. Not a live feed.
- The rating is the site's own **strokes versus the field** number, built from scores and adjusted for field strength. It is not the official shot-level strokes gained statistic, and there are no shot-level categories (off the tee, approach, putting).
- Odds are the pre-tournament winner prices of the four men's majors only, from 2021. No other tournaments, no round or matchup or top-10 markets, no each-way terms. The latest price for a past major can be up to a week before the first tee time, so it is not a closing line.
- Hole-by-hole scores exist for the PGA Tour (since 2001) and the Korn Ferry Tour. The LPGA, LIV and the DP World Tour have round scores only.

The betting skills frame every edge as an estimate. Outright markets have long losing runs and a small number of majors in the archive, so a few seasons of results say little about whether a strategy works.

Coverage by season: https://birdieapi.com/data
