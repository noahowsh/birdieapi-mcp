# BirdieAPI: golf skills

Golf analysis skills on BirdieAPI: game previews, player and team research, and the community's standard metrics, with every number pulled live from the BirdieAPI MCP server.

## Skills

- `golf-course-history`: Use when the user asks how a golfer has done at a course or event before, in fan or analyst wording.
- `golf-finish-simulation`: Use when the user wants golf win or finish chances from a simulation, in fan or analyst wording.
- `golf-leaderboard-story`: Use when the user wants the story of a golf tournament that has been played or is under way, in fan or analyst wording.
- `golf-strokes-vs-field`: Use when the user asks how a golfer is playing or how golfers compare on scoring, in fan or analyst wording.
- `golf-tournament-preview`: Use when the user wants to get ready for a golf event, in fan or analyst wording.

## Data it sends

The skills call the BirdieAPI MCP server at `mcp.birdieapi.com`. Each call sends the tool name and its inputs (teams, players, dates, seasons) with your BirdieAPI API key, and returns data. Nothing from your files or conversation is sent beyond what a tool call needs. Calls use credits on your BirdieAPI account; a free key at https://birdieapi.com/signup includes monthly credits.

Privacy policy: https://birdieapi.com/privacy

## Install

```
/plugin marketplace add sports-data-hq/sportsdatahq-skills
/plugin install golf-data@sportsdatahq
```

More: https://birdieapi.com/skills. Licence: MIT (see LICENSE).
