---
name: season-pack-offline
description: "Use when no SportsDataHQ MCP tools are available in this session (no get_standings, get_leaders or similar tools listed) and the user asks about a sport's last completed season, or says they have no key or want to try before signing up: 'I don't have a key, can you still look at last season', 'try it without signing up', 'is there a free sample of the data'. Answers from the free season pack (last completed season as CSV: games, standings, player season totals and our ratings) and names the season. If the sport's MCP tools are listed, never use this; use the sport's own skills. Not for the current season, today's games, odds, props or play-by-play: those need the live API and a free key."
metadata:
  version: 2.2.0
  author: SportsDataHQ
---

# Season pack, offline

Every SportsDataHQ API publishes a free season pack: the last completed season as CSV. It lets someone try real questions before they have a key. This skill loads the right pack, answers from it, and is clear about what it cannot answer.

## When the live server is connected, don't use this

If the sport's MCP server is available (tools like `get_standings`, `get_leaders`), use the sport's own skills. The pack is a fallback for people without a key or without the server installed.

## The packs

| Sport | API | Pack |
|---|---|---|
| Hockey | PuckAPI | https://github.com/PuckAPI/mcp/releases/download/season-pack/puckapi-season-pack.zip |
| Football | EndzoneAPI | https://github.com/sports-data-hq/endzoneapi-mcp/releases/download/season-pack/endzoneapi-season-pack.zip |
| Basketball | DunkAPI | https://github.com/sports-data-hq/dunkapi-mcp/releases/download/season-pack/dunkapi-season-pack.zip |
| Baseball | FastballAPI | https://github.com/sports-data-hq/fastballapi-mcp/releases/download/season-pack/fastballapi-season-pack.zip |
| Soccer | StrikerAPI | https://github.com/sports-data-hq/strikerapi-mcp/releases/download/season-pack/strikerapi-season-pack.zip |
| Tennis | AcesAPI | https://github.com/sports-data-hq/acesapi-mcp/releases/download/season-pack/acesapi-season-pack.zip |
| Golf | BirdieAPI | https://github.com/sports-data-hq/birdieapi-mcp/releases/download/season-pack/birdieapi-season-pack.zip |
| UFC | FighterAPI | https://github.com/sports-data-hq/fighterapi-mcp/releases/download/season-pack/fighterapi-season-pack.zip |
| Cricket | YorkerAPI | https://github.com/sports-data-hq/yorkerapi-mcp/releases/download/season-pack/yorkerapi-season-pack.zip |

Files are named `<api>-<league>-<season>-<kind>.csv`, where kind is games, standings, players or teams (tennis, golf, UFC and cricket use their sport's words; read the zip's file list). Each pack's `data/README.md` in the same repo lists every column.

## Steps

1. Pick the pack for the sport and download it once (`curl -L -o pack.zip <url>`, or Python `urllib`). Unzip and list the files.
2. Load the file the question needs with pandas. State the league id and season in the answer, using the sport's season convention from the pack README (soccer 2025 is 2025-26; NBA 2026 is 2025-26; NHL uses 20252026).
3. Answer from the rows: compute what's asked, show the rows behind any number, and give sample sizes (games, minutes) for rates. Use a minimum (for example 1,000 minutes, 20 games) before ranking per-minute or per-game rates, and say which.
4. Say what the pack can't answer. The current season, today's games, earlier seasons, play-by-play, shot or pitch locations, lineups, odds and props are on the live API. Point to the free key at the sport's site (puckapi.com, endzoneapi.com, dunkapi.com, fastballapi.com, strikerapi.com, acesapi.com, birdieapi.com, fighterapi.com, yorkerapi.com) or one key for every sport at app.sportsdatahq.com.

## Rules

- Never present pack numbers as current. Always name the season.
- If the user plans to publish something built on the pack, tell them the pack licence asks for the credit "Data: <API name> (<site>)". Leave adding it to them; never write it into their content yourself.
- Don't help redistribute the files themselves (the pack licence forbids it). Analysis, charts and models built on them are fine.
- Odds are not in the pack. Don't estimate or invent them.
- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.