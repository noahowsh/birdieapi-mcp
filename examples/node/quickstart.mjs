#!/usr/bin/env node
// BirdieAPI quickstart: upcoming PGA Tour events, then the strokes-versus-field player ratings. Node 18+, no dependencies. Needs BIRDIEAPI_API_KEY. Costs about 3 credits.
const BRAND = "BirdieAPI";
const KEY_ENV = "BIRDIEAPI_API_KEY";
const BASE_URL = "https://mcp.birdieapi.com/v1";
const SIGNUP_URL = "https://birdieapi.com/signup";

const key = (process.env[KEY_ENV] || "").trim();
if (!key) {
  console.error(
    `Set ${KEY_ENV} first:\n  export ${KEY_ENV}=your_key\n` +
      `Get a free key (500 credits every month, no card): ${SIGNUP_URL}`,
  );
  process.exit(1);
}

let remaining = null;

async function call(tool, args = {}) {
  let res;
  try {
    res = await fetch(`${BASE_URL}/${tool}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-api-key": key },
      body: JSON.stringify(args),
    });
  } catch (err) {
    throw new Error(`Network error calling ${tool}: ${err.cause?.code ?? err.message}`);
  }
  remaining = res.headers.get("x-credits-remaining") ?? remaining;
  const text = await res.text();
  let body = {};
  try {
    body = JSON.parse(text);
  } catch {}
  // Every response is wrapped as {"data": ...}.
  if (res.ok) return body && body.data !== undefined ? body.data : body;
  const message = body.message || body.error || res.statusText;
  if (res.status === 401) throw new Error(`401 unauthorized. Check ${KEY_ENV}. ${message}`);
  if (res.status === 402) {
    throw new Error(
      `402 out of credits. ${message} Upgrade or wait for the monthly reset: ${body.upgrade_url || SIGNUP_URL}`,
    );
  }
  throw new Error(`HTTP ${res.status} from ${tool}: ${message}`);
}

const fmt = (v, digits) => (v == null ? "-" : digits != null && typeof v === "number" ? v.toFixed(digits) : String(v));
const pct = (v, digits = 1) => (v == null ? "-" : `${(v * 100).toFixed(digits)}%`);

function table(headers, rows) {
  const cells = rows.map((r) => r.map((c) => (c == null ? "-" : String(c))));
  const widths = headers.map((h, i) => Math.max(h.length, ...cells.map((r) => r[i].length)));
  const line = (r) => r.map((c, i) => c.padEnd(widths[i])).join("  ").trimEnd();
  console.log(line(headers));
  console.log(widths.map((w) => "-".repeat(w)).join("  "));
  cells.forEach((r) => console.log(line(r)));
}

function finish() {
  if (remaining !== null) console.log(`\nCredits remaining: ${remaining}`);
}

async function main() {
  const sched = await call("get_schedule", { days: 14 });
  const events = sched.tournaments ?? [];
  console.log("Tournaments in the next 14 days (get_schedule, 1 credit)");
  if (events.length) {
    table(
      ["Start", "Tournament", "Status", "Course", "Purse"],
      events.slice(0, 8).map((t) => [t.start_date, t.name, t.status, t.courses?.[0]?.name, t.purse]),
    );
  } else {
    console.log("No tournaments in the next 14 days.");
  }

  const ratings = await call("get_ratings", { limit: 5 });
  console.log(`\nPlayer ratings, strokes per round vs the field, as of ${ratings.as_of} (get_ratings, 2 credits)`);
  table(
    ["#", "Player", "Country", "Rating", "Rounds"],
    (ratings.ratings ?? []).map((r) => [r.rank, r.name, r.country, fmt(r.rating, 2), fmt(r.weighted_rounds, 1)]),
  );
  finish();
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
