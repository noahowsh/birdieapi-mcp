# BirdieAPI season pack

The last completed season of golf as CSV, free to use under the [BirdieAPI Sample Data Licence](../DATA-LICENSE.md). Use it in anything you build, credit BirdieAPI, and don't republish the files themselves.

**Download:** the latest `birdieapi-season-pack.zip` from this repository's [season-pack release](https://github.com/sports-data-hq/birdieapi-mcp/releases/tag/season-pack). `preview/` holds the first 100 rows of a few files.

Seasons: 2025, 2026. Season naming: the tour season year. Competitions, by their API id: dpwt, kornferry, liv, lpga, pga. No odds, props or play-by-play: those, every earlier season and live data are on the API, free to start at https://birdieapi.com/signup?utm_source=github&utm_medium=pack&utm_campaign=birdieapi-pack.

## Files

| File | Rows |
|---|---|
| `birdieapi-dpwt-2026-players.csv` | 809 |
| `birdieapi-dpwt-2026-results.csv` | 4,829 |
| `birdieapi-dpwt-2026-tournaments.csv` | 35 |
| `birdieapi-kornferry-2026-players.csv` | 371 |
| `birdieapi-kornferry-2026-results.csv` | 3,615 |
| `birdieapi-kornferry-2026-tournaments.csv` | 25 |
| `birdieapi-liv-2026-players.csv` | 66 |
| `birdieapi-liv-2026-results.csv` | 693 |
| `birdieapi-liv-2026-tournaments.csv` | 12 |
| `birdieapi-lpga-2025-players.csv` | 475 |
| `birdieapi-lpga-2025-results.csv` | 3,582 |
| `birdieapi-lpga-2025-tournaments.csv` | 33 |
| `birdieapi-pga-2025-players.csv` | 788 |
| `birdieapi-pga-2025-results.csv` | 5,750 |
| `birdieapi-pga-2025-tournaments.csv` | 48 |

## Columns

- **players**: `league`, `season`, `player`, `country`, `events`, `cuts_made`, `wins`, `top_tens`, `earnings`, `cup_points`, `rounds`, `scoring_average`, `strokes_vs_field_per_round`, `adj_strokes_vs_field_per_round`, `rating_end_of_season`
- **results**: `league`, `season`, `tournament`, `date`, `position`, `position_display`, `player`, `country`, `status`, `to_par`, `total_strokes`, `rounds_played`, `earnings`, `cup_points`
- **tournaments**: `league`, `season`, `name`, `start_date`, `end_date`, `major`, `scoring_system`, `rounds_scheduled`, `cut_score`, `purse`, `field_size`, `course`, `winner`, `playoff`

Credit line for anything you publish: **Data: BirdieAPI (birdieapi.com)**
