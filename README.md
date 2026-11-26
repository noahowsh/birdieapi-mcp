# BirdieAPI MCP server

[![MCP Registry](https://img.shields.io/badge/MCP%20Registry-listed-0b7285?style=flat-square)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.noahowsh/birdieapi)

**The golf data API.** PGA Tour leaderboards with finishing positions, earnings and points, round scores and hole-by-hole scorecards, courses with par and yardage per hole, player and course history, our own strokes-versus-field rating, par-3/4/5 scoring splits and the winner prices of the four men's majors by sportsbook. The LPGA, LIV, the DP World Tour and the Korn Ferry Tour use the same tools. REST API and MCP server. 500 free credits every month, no card.

Website: https://birdieapi.com?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp · Docs: https://birdieapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp · Get a key: https://birdieapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp

```
You:    "How did Scottie Scheffler score on each hole of the 2025 Masters?"
Claude: [calls get_scorecard]

You:    "Which players have the best record at Pebble Beach since 2010?"
Claude: [calls get_course_history]

You:    "What did sportsbooks price Scottie Scheffler to win the 2025 Masters?"
Claude: [calls get_winner_odds]
```


## Run it locally (stdio)

Most clients connect to `https://mcp.birdieapi.com/mcp` directly. For a client that launches a local process instead:

```bash
git clone https://github.com/sports-data-hq/birdieapi-mcp.git && cd birdieapi-mcp && npm install
BIRDIEAPI_API_KEY=your_key node index.js
```

```json
{ "mcpServers": { "birdieapi": { "command": "node", "args": ["/path/to/birdieapi-mcp/index.js"], "env": { "BIRDIEAPI_API_KEY": "your_key" } } } }
```

It forwards to the hosted server with your key, so every tool and credit cost is the same.

## Try it now, no key

- **A free season of golf data:** the last completed season as CSV (games, standings, player season totals and our ratings). [Download the zip](https://github.com/sports-data-hq/birdieapi-mcp/releases/download/season-pack/birdieapi-season-pack.zip) or browse [what's in it](data/README.md).
- **Open it in Colab:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sports-data-hq/birdieapi-mcp/blob/main/notebooks/birdieapi-season-pack.ipynb) loads the pack and answers three questions in a minute.
- **Ask Claude without a key:** install the skills below; `season-pack-offline` answers from the pack until you connect.

**With a free key it does far more:** every earlier season, today's games, play-by-play, lineups, odds and player props with their history and movement, and every skill below running on live data. [Get a free key](https://birdieapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-try-now): 500 credits a month, no card.

## Skills

5 Claude skills for golf ship in this repo, plus 15 analytics skills for models, backtests, calibration and comparing a model with the market. Every number in an answer comes from a live BirdieAPI tool call, and odds are information only: no stakes, no picks.

Claude Code:

```
/plugin marketplace add sports-data-hq/birdieapi-mcp
/plugin install golf-data@birdieapi
/plugin install sports-analytics-core@birdieapi
```

Codex: `codex plugin marketplace add sports-data-hq/birdieapi-mcp`. Any agent that reads skills: `npx skills add sports-data-hq/birdieapi-mcp`.

| Skill | What it does |
|---|---|
| `golf-course-history` | A player's finishes and strokes versus the field at an event or course, set against current form |
| `golf-finish-simulation` | Simulated finish chances (win, top 5, top 10, made cut) from strokes-versus-field ratings |
| `golf-leaderboard-story` | The story of a tournament, round by round and hole by hole, with strokes versus the field |
| `golf-strokes-vs-field` | Strokes versus the field per round, raw and adjusted for field strength, and by hole type |
| `golf-tournament-preview` | Tournament preview: course, form, course history, ratings and the winner market for the majors |

The analytics skills: `backtesting`, `data-pipeline`, `elo-engineering`, `feature-engineering`, `market-vs-model`, `model-building`, `nl-to-query`, `odds-market-analysis`, `prediction-tracker`, `probability-calibration`, `season-pack-offline`, `sports-data-preflight`, `sports-skill-router`, `visualization`, `walk-forward-validation`.

Real answers on live data, with the credits each used: [example answers](https://github.com/sports-data-hq/sportsdatahq-skills/tree/main/docs/examples/golf).

All nine sports' skills live in [sports-data-hq/sportsdatahq-skills](https://github.com/sports-data-hq/sportsdatahq-skills). The copies here are synced from there, so please open issues and pull requests there.

## Python

The official Python client is on PyPI: [birdieapi](https://pypi.org/project/birdieapi/).

```bash
pip install birdieapi
export BIRDIEAPI_API_KEY=sk_live_...
```

```python
from birdieapi import Client

client = Client()

events = client.list_tournaments(status="final", limit=3)["tournaments"]
for e in events:
    print(e["tournament_id"], e["name"], e["winner_name"], e["winning_to_par"])
```

Typed errors for a bad key, no credits left, not found and rate limits, automatic retries, and `to_dataframe` for pandas.

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

## Examples

Runnable Python (standard library only) and Node 18+ (no dependencies) examples live in [`examples/`](examples/):

- [`examples/python/quickstart.py`](examples/python/quickstart.py) and [`examples/node/quickstart.mjs`](examples/node/quickstart.mjs): schedule plus a headline call.
- [`examples/python/golf_major_leaderboard_and_odds.py`](examples/python/golf_major_leaderboard_and_odds.py): One major, before and after.

```bash
export BIRDIEAPI_API_KEY=your_key
python3 examples/python/quickstart.py
node examples/node/quickstart.mjs
```

See [`examples/README.md`](examples/README.md) for details. Get a free key (500 credits a month, no card) at https://birdieapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp.

## Use it in

- **Claude, ChatGPT, Cursor, VS Code, Gemini CLI, Grok, Perplexity, Le Chat:** add `https://mcp.birdieapi.com/mcp` as a remote MCP server. Step-by-step for each: https://birdieapi.com/mcp?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- **Gemini CLI:** `gemini extensions install https://github.com/sports-data-hq/birdieapi-mcp`
- **Cursor:** the [SportsDataHQ plugins for Cursor](https://github.com/sports-data-hq/sportsdatahq-cursor-plugins)
- **Google Sheets:** `=SDHQ("birdieapi","list_tournaments")` fills a live table: https://sportsdatahq.com/sheets?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- **REST:** `POST https://mcp.birdieapi.com/v1/<tool>` with an `x-api-key` header: https://birdieapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp

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
| `get_leaders` | Season leaders for any stat we compute or keep |
| `get_winner_odds` | The four majors' winner prices by sportsbook before the first round: opening and latest, with implied probability |

Leagues: golf (default, PGA Tour), lpga, liv, dpwt, kornferry (pass `league` to any tool; omit it for the PGA Tour).

## Data

- PGA Tour leaderboards, rounds and hole-by-hole scores since 2001
- The Korn Ferry Tour (hole by hole since 2007), and round scores for the LPGA, LIV and the DP World Tour, in the same tools
- Courses with par and yardage per hole and how each hole played; player course history; head to head
- Our strokes-versus-field rating, field-strength adjusted, and par-3/4/5 scoring splits (averages, plus strokes versus the field by hole type for the PGA Tour and Korn Ferry Tour); score-based, not shot-level strokes gained
- Major winner odds (`get_winner_odds`): outright winner prices of the four men's majors by sportsbook, opening and latest before the first round, every major from 2021 plus the 2020 U.S. Open (a past major's latest price can be up to a week before the first tee time), refreshed daily while an upcoming major's market is open and every six hours in tournament week
- No round, matchup, top-10 or other-tournament prices, and no prices for the other tours

Coverage by season, read live from the database: https://birdieapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp

## Pricing

500 free credits every month, no card. Plans: Starter $19/mo (10,000 credits), Pro $49/mo (30,000), Scale $149/mo (125,000), Business $299/mo (300,000). Wallet top-ups from $5, never expire. https://birdieapi.com/pricing?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp

## Useful pages

- Docs: https://birdieapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp (every endpoint, with a real response)
- Data atlas, coverage by season: https://birdieapi.com/data?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- Golf majors odds board (winner prices by sportsbook): https://birdieapi.com/odds?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- Major winner odds data: https://birdieapi.com/data/major-winner-odds?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- Hole-by-hole data: https://birdieapi.com/data/pga-tour-hole-by-hole-data?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- Guides (Python, JavaScript and cURL): https://birdieapi.com/guides?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- Glossary (strokes versus the field, field strength, par-type splits): https://birdieapi.com/glossary?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- Pricing: https://birdieapi.com/pricing?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp
- For bettors and modellers: https://birdieapi.com/for/bettors?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp

## Attribution

Ratings are ours. Not affiliated with the PGA Tour, LPGA, LIV Golf, DP World Tour or Korn Ferry Tour.

## License

MIT for the contents of this repository. Data terms as above.

## Use with Codex

The SportsDataHQ skills marketplace also works in Codex (it reads `.agents/plugins/marketplace.json`):

```bash
codex plugin marketplace add sports-data-hq/sportsdatahq-skills
```

Install `golf-data`, which bundles the golf skills and the BirdieAPI MCP server.

## Use with Gemini CLI

```bash
export BIRDIEAPI_API_KEY=your_key
gemini extensions install https://github.com/sports-data-hq/birdieapi-mcp
```

The extension adds the BirdieAPI MCP server (https://mcp.birdieapi.com/mcp) and sends the key in the `x-api-key` header. Get a free key (500 credits a month) at https://birdieapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=birdieapi-mcp.
