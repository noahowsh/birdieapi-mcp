# BirdieAPI examples

Runnable examples for the [BirdieAPI](https://birdieapi.com). Python uses only the standard library (`urllib` and `json`). Node uses the built-in `fetch` (Node 18 or newer). No packages to install.

PGA, LPGA, LIV, DP World Tour and Korn Ferry golf data API. Every tool is a REST call: `POST https://mcp.birdieapi.com/v1/<tool_name>` with a JSON body and an `x-api-key` header. The same tools are available over MCP at `https://mcp.birdieapi.com/mcp`.

## Get a key

1. Sign up at https://birdieapi.com/signup. The free plan gives 500 credits every month, no card.
2. Copy a key from https://birdieapi.com/dashboard/keys.
3. Export it. The scripts read it from the environment and never print it.

```bash
export BIRDIEAPI_API_KEY=your_key
```

## What is here

| File | What it does | Tools | Credits |
| --- | --- | --- | --- |
| `python/quickstart.py` | Upcoming schedule plus one headline call, printed as small tables | `get_schedule`, `get_ratings` | about 3 |
| `python/golf_major_leaderboard_and_odds.py` | One major, before and after. The final leaderboard (finish, score, strokes, earnings) next to the outright winner market from before round 1, with opening and latest median implied probability. Defaults to the 2025 Masters. | `list_tournaments`, `get_leaderboard`, `get_winner_odds` | about 8 |
| `node/quickstart.mjs` | Same as the Python quickstart, for Node | `get_schedule`, `get_ratings` | about 3 |

## Run

```bash
python3 python/quickstart.py
python3 python/golf_major_leaderboard_and_odds.py
node node/quickstart.mjs
```

The use-case script takes optional arguments. For example:

```bash
python3 golf_major_leaderboard_and_odds.py --season 2024 --major PGA
```

Run any script with `--help` (Python) to see its options.

## Credits and errors

- Every call costs credits, priced per tool. The cost is shown next to each call in the script output, and the response header `X-Credits-Remaining` is printed at the end.
- To see what a call would cost without running it, send `"estimate_only": true` on the tools that accept it (see the tool schema).
- When you are out of credits the API returns HTTP 402 with `{"error": "insufficient_credits", "message": "...", "upgrade_url": "..."}`. The scripts print that message and the upgrade link.
- HTTP 401 means the key is missing or wrong. The scripts print a hint to check `BIRDIEAPI_API_KEY`.
- The PGA Tour is the default. Pass `"league"` in the request body for `lpga`, `liv`, `dpwt` or `kornferry`.
- The tool list with input schemas is public: `curl https://mcp.birdieapi.com/v1/tools`.

## More

- Docs and example responses for every tool: https://birdieapi.com/docs
- Full reference in one file: https://birdieapi.com/llms-full.txt
- Free key: https://birdieapi.com/signup
