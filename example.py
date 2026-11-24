"""Alibaba Top Ranking -> sourcing shortlist.

Runs rel8ble/alibaba-top-ranking-scraper on Apify (or reads a saved JSON export with
--from-json) and prints, per niche, the ranked products that are easy to test-order:
low MOQ, real units sold, plus the products Alibaba lists in more than one ranking.

    pip install apify-client
    export APIFY_TOKEN=...            # or pass --token
    python example.py --categories "Consumer Electronics" "Pet Supplies"
    python example.py --from-json sample.json
"""
import argparse
import csv
import json
import os
from collections import defaultdict
from statistics import median


def fetch(token, categories, rank_types, regions, max_rankings):
    from apify_client import ApifyClient

    client = ApifyClient(token)
    run = client.actor("rel8ble/alibaba-top-ranking-scraper").call(run_input={
        "categories": categories,
        "rankTypes": rank_types,
        "regions": regions,
        "maxRankingsPerCategory": max_rankings,
    })
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def shortlist(rows, max_moq, min_sold):
    picks = []
    for r in rows:
        moq, sold = r.get("moq"), r.get("sold")
        if moq is None or sold is None or moq > max_moq or sold < min_sold:
            continue
        orders = r.get("orders") or 0
        picks.append({
            "niche": r["rankingName"],
            "rank": r["rank"],
            "title": r["title"][:60],
            "price": r.get("priceText"),
            "moq": r.get("moqText"),
            "sold": sold,
            "orders": orders,
            "units_per_order": round(sold / orders) if orders else None,
            "supplier": f'{r.get("supplierCountryCode") or "?"} / {r.get("goldSupplierYears") or 0} yrs',
            "other_rankings": len(r.get("otherRankings") or []),
            "url": r["url"],
        })
    return sorted(picks, key=lambda p: (p["niche"], -p["sold"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.environ.get("APIFY_TOKEN"))
    ap.add_argument("--categories", nargs="+", default=["Consumer Electronics"])
    ap.add_argument("--rank-types", nargs="+", default=["hot-selling"])
    ap.add_argument("--regions", nargs="+", default=["global"])
    ap.add_argument("--max-rankings", type=int, default=5)
    ap.add_argument("--max-moq", type=float, default=10)
    ap.add_argument("--min-sold", type=int, default=500)
    ap.add_argument("--from-json", help="read a saved dataset export instead of calling the actor")
    ap.add_argument("--csv", default="alibaba_shortlist.csv")
    a = ap.parse_args()

    if a.from_json:
        with open(a.from_json, encoding="utf-8") as f:
            rows = json.load(f)
    else:
        if not a.token:
            raise SystemExit("Set APIFY_TOKEN or pass --token (or use --from-json)")
        rows = fetch(a.token, a.categories, a.rank_types, a.regions, a.max_rankings)

    print(f"{len(rows)} ranked products")
    by_niche = defaultdict(list)
    for r in rows:
        by_niche[r["rankingName"]].append(r)
    print("\nNiche                            rows  median low price  MOQ<=10")
    for niche, items in sorted(by_niche.items()):
        lows = [r["priceMin"] for r in items if r.get("priceMin") is not None]
        easy = sum(1 for r in items if r.get("moq") is not None and r["moq"] <= 10)
        print(f"{niche[:32]:<32} {len(items):>4}  ${median(lows):>14,.2f}  {easy:>7}")

    picks = shortlist(rows, a.max_moq, a.min_sold)
    print(f"\nShortlist: MOQ <= {a.max_moq:g}, {a.min_sold}+ units sold -> {len(picks)} products")
    for p in picks:
        upo = p["units_per_order"] if p["units_per_order"] is not None else "-"
        print(f'  [{p["niche"][:22]} #{p["rank"]}] {p["price"]:<12} MOQ {p["moq"]:<10} '
              f'{p["sold"]:>6} sold / {p["orders"]:>3} orders (~{upo}/order)  {p["supplier"]}  {p["title"]}')

    multi = [r for r in rows if r.get("otherRankings")]
    print(f"\nIn more than one Top ranking: {len(multi)} of {len(rows)}")

    if picks:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(picks[0].keys()))
            w.writeheader()
            w.writerows(picks)
        print(f"Saved {a.csv}")


if __name__ == "__main__":
    main()
