import json
import os
from datetime import datetime, timezone
from pathlib import Path
import random

# Paths
ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "config.json"
OUT_DIR = ROOT / "out"
OUT_DIR.mkdir(exist_ok=True)

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def fake_search_deals(cfg):
    """
    For now, this is a stub that fabricates a few 'deals' so you can see the end-to-end flow.
    Later, we’ll swap this with real API calls.
    """
    deals = []
    for dest in cfg["destinations"]:
        # Pretend we found up to 3 flight+resort combos per destination
        for i in range(random.randint(1, 3)):
            base_price = random.randint(420, 780)  # CAD per person (mock)
            total = base_price * cfg["party_size"]
            resort_stars = random.choice([4.0, 4.5, 5.0])
            deals.append({
                "origin": cfg["origins"][0],
                "destination": dest,
                "depart": cfg["depart_date"],
                "return": cfg["return_date"],
                "resort": f"Resort {dest}-{i+1}",
                "stars": resort_stars,
                "per_person_cad": base_price,
                "total_cad": total
            })
    # Basic filters
    filtered = [
        d for d in deals
        if d["per_person_cad"] <= cfg["price_cap_per_person_cad"]
        and d["stars"] >= cfg["min_resort_stars"]
    ]
    # Sort cheapest first
    filtered.sort(key=lambda d: d["per_person_cad"])
    return filtered

def render_markdown(cfg, results):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = []
    lines.append(f"# Travel Agent Results\n")
    lines.append(f"**Generated:** {ts}")
    lines.append("")
    lines.append("**Filters:**")
    lines.append(f"- Origin(s): {', '.join(cfg['origins'])}")
    lines.append(f"- Destinations: {', '.join(cfg['destinations'])}")
    lines.append(f"- Dates: {cfg['depart_date']} → {cfg['return_date']}")
    lines.append(f"- Party size: {cfg['party_size']}")
    lines.append(f"- Max price (CAD per person): {cfg['price_cap_per_person_cad']}")
    lines.append(f"- Min resort stars: {cfg['min_resort_stars']}")
    lines.append("")

    if not results:
        lines.append("> No deals matched your filters this run.")
        return "\n".join(lines)

    lines.append("## Matching deals (mock data)")
    lines.append("")
    lines.append("| Origin | Destination | Depart | Return | Resort | Stars | Price/Person (CAD) | Total (CAD) |")
    lines.append("|---|---|---|---|---|---:|---:|---:|")
    for d in results:
        lines.append(
            f"| {d['origin']} | {d['destination']} | {d['depart']} | {d['return']} | {d['resort']} | {d['stars']} | {d['per_person_cad']} | {d['total_cad']} |"
        )

    return "\n".join(lines)

def main():
    cfg = load_config()
    results = fake_search_deals(cfg)
    md = render_markdown(cfg, results)

    # Write a timestamped report file
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outfile = OUT_DIR / f"travel-agent-report-{stamp}.md"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(md)

    # Print a short console summary
    print(f"Found {len(results)} deals that match filters.")
    if results:
        best = results[0]
        print(
            f"Cheapest mock deal: {best['destination']} at ${best['per_person_cad']} CAD/person "
            f"({best['stars']}★ {best['resort']})."
        )
    print(f"Report saved to: {outfile}")

if __name__ == "__main__":
    main()
