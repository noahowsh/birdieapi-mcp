#!/usr/bin/env python3
"""Golf major leaderboard and outright winner odds. Usage: python3 golf_major_leaderboard_and_odds.py [--season 2025] [--major Masters] [--top 10]. Costs 8 credits (list_tournaments 1 + get_leaderboard 2 + get_winner_odds 5)."""
import json
import os
import sys
import urllib.error
import urllib.request
import argparse

BRAND = "BirdieAPI"
KEY_ENV = "BIRDIEAPI_API_KEY"
BASE_URL = "https://mcp.birdieapi.com/v1"
SIGNUP_URL = "https://birdieapi.com/signup"
LAST_REMAINING = None


class ApiError(Exception):
    pass


def require_key():
    key = os.environ.get(KEY_ENV, "").strip()
    if not key:
        sys.exit(
            f"Set {KEY_ENV} first:\n"
            f"  export {KEY_ENV}=your_key\n"
            f"Get a free key (500 credits every month, no card): {SIGNUP_URL}"
        )
    return key


def call(key, tool, args=None):
    """POST /v1/<tool> with a JSON body and return the parsed response."""
    global LAST_REMAINING
    req = urllib.request.Request(
        f"{BASE_URL}/{tool}",
        data=json.dumps(args or {}).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "User-Agent": "birdieapi.com-examples/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            LAST_REMAINING = resp.headers.get("X-Credits-Remaining", LAST_REMAINING)
            return json.load(resp)
    except urllib.error.HTTPError as err:
        raise ApiError(describe(err, tool)) from None
    except urllib.error.URLError as err:
        raise ApiError(f"Network error calling {tool}: {err.reason}") from None


def describe(err, tool):
    try:
        body = json.loads(err.read().decode() or "{}")
    except ValueError:
        body = {}
    message = body.get("message") or body.get("error") or err.reason
    if err.code == 401:
        return f"401 unauthorized. Check {KEY_ENV}. {message}"
    if err.code == 402:
        upgrade = body.get("upgrade_url") or SIGNUP_URL
        return f"402 out of credits. {message} Upgrade or wait for the monthly reset: {upgrade}"
    return f"HTTP {err.code} from {tool}: {message}"


def fmt(value, digits=None):
    if value is None:
        return "-"
    if digits is not None and isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return str(value)


def pct(value, digits=1):
    return "-" if value is None else f"{value * 100:.{digits}f}%"


def table(headers, rows):
    rows = [["-" if c is None else str(c) for c in r] for r in rows]
    widths = [max([len(h)] + [len(r[i]) for r in rows]) for i, h in enumerate(headers)]
    line = lambda cells: "  ".join(c.ljust(w) for c, w in zip(cells, widths)).rstrip()
    print(line(headers))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(line(r))


def finish():
    if LAST_REMAINING is not None:
        print(f"\nCredits remaining: {LAST_REMAINING}")

def to_par(n):
    if n is None:
        return "-"
    return "E" if n == 0 else f"{n:+d}"


def main():
    ap = argparse.ArgumentParser(description="A major's final leaderboard next to its pre-tournament winner odds.")
    ap.add_argument("--season", type=int, default=2025)
    ap.add_argument("--major", default="Masters", help="part of the tournament name (default: Masters)")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    key = require_key()

    majors = call(key, "list_tournaments", {"season": args.season, "major": True, "limit": 4}).get("tournaments") or []
    if not majors:
        sys.exit(f"No majors found for {args.season}.")
    event = next((t for t in majors if args.major.lower() in (t.get("name") or "").lower()), majors[0])
    print(f"{event['name']} {event['season']}, {event.get('start_date')} to {event.get('end_date')}, "
          f"winner {event.get('winner_name')} ({to_par(event.get('winning_to_par'))})")

    board = call(key, "get_leaderboard", {"tournament_id": event["tournament_id"], "limit": args.top})
    print("\nFinal leaderboard")
    table(["Pos", "Player", "Country", "To par", "Strokes", "Earnings"],
          [[p.get("position_display"), p.get("name"), p.get("country"), to_par(p.get("to_par")),
            p.get("total_strokes"), p.get("earnings")] for p in board.get("players") or []])

    odds = call(key, "get_winner_odds", {"tournament_id": event["tournament_id"], "limit": args.top})
    priced = (odds.get("tournaments") or [{}])[0].get("golfers") or []
    print("\nOutright winner market before round 1 (median implied probability across books)")
    if priced:
        table(["Golfer", "Opening", "Latest"],
              [[g.get("player_name"), pct(g.get("median_implied_prob_opening")),
                pct(g.get("median_implied_prob_latest"))] for g in priced])
    else:
        print("No winner odds stored for this tournament.")
    finish()


if __name__ == "__main__":
    try:
        main()
    except ApiError as err:
        sys.exit(f"Error: {err}")
