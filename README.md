# BirdieAPI MCP server

**The golf data API.** PGA Tour leaderboards with finishing positions, earnings and points, round scores and hole-by-hole scorecards, courses with par and yardage per hole, player and course history, our own strokes-versus-field rating, par-3/4/5 scoring splits and the winner prices of the four men's majors by sportsbook. The LPGA, LIV, the DP World Tour and the Korn Ferry Tour use the same tools. REST API and MCP server. 500 free credits, no card.

Website: https://birdieapi.com · Docs: https://birdieapi.com/docs · Get a key: https://birdieapi.com/signup

```
You:    "How did Scottie Scheffler score on each hole of the 2025 Masters?"
Claude: [calls get_scorecard]

You:    "Which players have the best record at Pebble Beach since 2010?"
Claude: [calls get_course_history]

You:    "What did sportsbooks price Scottie Scheffler to win the 2025 Masters?"
Claude: [calls get_winner_odds]
```

## Quick start

This is a hosted (remote) MCP server over Streamable HTTP. There is nothing to install.

**Claude Code**

```bash
claude mcp add --transport http birdieapi "https://mcp.birdieapi.com/mcp?key=YOUR_API_KEY"
```

**Claude Desktop, Cursor and other clients**

```json
{
  "mcpServers": {
    "birdieapi": {
      "url": "https://mcp.birdieapi.com/mcp?key=YOUR_API_KEY"
    }
  }
}
```

The key can also be sent as an `x-api-key` header or `Authorization: Bearer`. Connecting and listing tools works without a key; calling a tool needs one.

**REST**

```bash
curl -X POST https://mcp.birdieapi.com/v1/list_tournaments -H "x-api-key: YOUR_API_KEY"
```

Every tool is `POST /v1/{tool}` with a JSON body.

## Tools (14)

| Tool | What it returns |
|------|-----------------|
| `list_tournaments` | A season's tournaments with dates, winner, purse and courses |
| `search_players` | Find players by name |
| `get_schedule` | Tournaments this week and coming up, with the host course |
| `get_leaderboard` | A tournament's full leaderboard: position, rounds, total, earnings and points |
| `get_scorecard` | A player's hole-by-hole scorecard for a tournament, with par and yardage |
| `get_course` | A course as set up for a tournament: par and yards per hole and how each hole played |
| `get_ratings` | Our strokes-versus-field rating: every active player, field-strength adjusted |
| `get_player` | Profile, rating, season lines and recent finishes |
| `get_player_results` | A player's tournaments and rounds by season, with strokes versus the field |
| `get_player_stats` | A player's season stats: scoring, birdies, par-3/4/5 scoring, driving, greens, putting |
| `get_course_history` | A player's record at one tournament or course, every year |
| `get_head_to_head` | Two players' finishes and rounds in every tournament they both played |
| `get_leaders` | Season leaders for any stat we compute or ESPN keeps |
| `get_winner_odds` | The four majors' winner prices by sportsbook before the first round: opening and latest, with implied probability |

Leagues: golf (default, PGA Tour), lpga, liv, dpwt, kornferry (pass `league` to any tool; omit it for the PGA Tour).

## Data

- PGA Tour leaderboards, rounds and hole-by-hole scores since 2001
- LPGA, LIV, the DP World Tour and the Korn Ferry Tour (hole by hole since 2007) in the same tools
- Courses with par and yardage per hole and how each hole played; player course history; head to head
- Our strokes-versus-field rating, field-strength adjusted, and par-3/4/5 scoring splits (averages, plus strokes versus the field by hole type for the PGA Tour and Korn Ferry Tour); score-based, not shot-level strokes gained
- Major winner odds (`get_winner_odds`): outright winner prices of the four men's majors by sportsbook, opening and latest before the first round, every major from 2021 plus the 2020 U.S. Open (The Odds API archive; a past major's latest price can be up to a week before the first tee time), refreshed daily while an upcoming major's market is open and every six hours in tournament week
- No round, matchup, top-10 or other-tournament prices, and no prices for the other tours

Coverage by season, read live from the database: https://birdieapi.com/docs

## Pricing

500 free credits on signup, no card. Plans: Starter $19/mo (10,000 credits), Pro $49/mo (30,000), Scale $149/mo (125,000). Wallet top-ups from $5, never expire. https://birdieapi.com/pricing

## Attribution

Golf data from public ESPN data; major winner prices from The Odds API. Ratings are ours. Not affiliated with the PGA Tour, LPGA, LIV Golf, DP World Tour or Korn Ferry Tour.

## License

MIT for the contents of this repository. Data terms as above.
