# Alibaba Top Ranking scraper in Python: hot-selling, trending and best-reviewed products as JSON

Export Alibaba.com's own **Top ranking** lists (hot selling by orders, most popular by views, best reviewed) for any category as JSON or CSV with Python: rank, niche, price range, MOQ, orders, units sold, views, ranking score, supplier country and Gold Supplier years. This repo calls the [Alibaba Top Ranking Scraper](https://apify.com/rel8ble/alibaba-top-ranking-scraper) actor on Apify and turns the result into a **low-MOQ sourcing shortlist**.

> I built this actor; it's a paid tool on Apify ($1.00 per 1,000 ranked products, no start fee). Apify's free $5 monthly credit covers about 5,000 products.

No browser, no login, no cookies: the actor reads the ranking pages over plain HTTP. The default input (5 featured Consumer Electronics niches, 100 products) finished in 6.1 seconds on Apify on 23 Nov 2026.

## Quick start (Python)

```bash
pip install -r requirements.txt
export APIFY_TOKEN=<YOUR_APIFY_TOKEN>
python example.py --categories "Consumer Electronics" "Pet Supplies"
python example.py --from-json sample.json     # offline, on the included real rows
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")
run = client.actor("rel8ble/alibaba-top-ranking-scraper").call(run_input={
    "categories": ["Consumer Electronics"],
    "rankTypes": ["hot-selling"],
    "regions": ["global"],
    "maxRankingsPerCategory": 5,
})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item["rankingName"], item["rank"], item["priceText"], item["moqText"], item["soldText"])
```

## Node

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/alibaba-top-ranking-scraper').call({
    categories: ['Jewelry, Eyewear, Watches & Accessories > Watches'],
    rankTypes: ['hot-selling', 'most-popular'],
    regions: ['us', 'eur'],
    maxRankingsPerCategory: 0,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.length, items[0]);
```

## Input

| Field | Default | What it does |
|---|---|---|
| `categories` | `["Consumer Electronics"]` | Category names, `Parent > Child` paths, category IDs, Top ranking URLs, or `all` |
| `rankTypes` | `["hot-selling"]` | `hot-selling`, `most-popular`, `best-reviewed` |
| `regions` | `["global"]` | `global`, `us`, `eur` |
| `maxRankingsPerCategory` | 5 | Niches per input line; 0 = every ranking under the category |
| `maxProductsPerRanking` | 20 | Products per list (1-20) |
| `rankingKeywords` | - | Keep only rankings whose name contains one of these words |
| `maxResults` | 0 | Stop after this many rows (0 = no limit) |

## Output sample

A real row from the 23 Nov 2026 default run (trimmed; the actor returns 46 fields):

```json
{
  "rank": 1,
  "rankType": "hot-selling",
  "region": "global",
  "rankingName": "Mobile Phone Housings",
  "title": "For Infinix Tecno Itel Smart 20 X6840 Back Glass Battery Cover ...",
  "priceText": "$0.88-1.08",
  "priceMin": 0.88,
  "moq": 5,
  "moqText": "5 pieces",
  "orders": 170,
  "sold": 5100,
  "rankScore": 4.5,
  "supplierCountryCode": "HK",
  "goldSupplier": true,
  "goldSupplierYears": 3
}
```

`sample.json` holds all 100 rows of that run with the main fields.

## What example.py prints

On `sample.json`:

```
100 ranked products

Niche                            rows  median low price  MOQ<=10
Data Cables                        20  $          0.74       12
Graphics Cards                     20  $        762.50       20
Mobile Phone Housings              20  $          1.88       18
Photographic Lighting              20  $         21.43       18
Power Banks & Power Station        20  $          8.50       15

Shortlist: MOQ <= 10, 500+ units sold -> 30 products
  [Data Cables #16] $3.81-4.19   MOQ 10 pieces   76200 sold /  20 orders (~3810/order)  CN / 2 yrs  ...
  [Data Cables #2] $0.90        MOQ 2 pieces     2700 sold /  60 orders (~45/order)  CN / 1 yrs  ...
  [Power Banks & Power St #2] $7.68-9.20   MOQ 1 set       17200 sold / 110 orders (~156/order)  CN / 8 yrs  ...
  ...
Saved alibaba_shortlist.csv
```

Tune it with `--max-moq`, `--min-sold`, `--rank-types`, `--regions` and `--max-rankings`.

## Limits

- Each ranking is 20 products; not every niche has all three ranking types.
- Orders, sold and views are Alibaba's rounded figures ("4.8K+ sold" -> 4800). Views were present on 77 of 100 rows in the sample run.
- Prices are in the currency Alibaba shows to the request's country (USD in these runs).
- Alibaba rate-limits a single IP after a burst of pages; the actor paces itself and retries through Apify Proxy.

## Links

- Store page: https://apify.com/rel8ble/alibaba-top-ranking-scraper
- Tutorial: https://dev.to/rel8ble/finding-low-moq-best-sellers-in-alibabas-top-ranking-lists-with-python-3p66
- Next step for a shortlisted product: [Alibaba Product Details Scraper](https://apify.com/rel8ble/alibaba-product-details-scraper) ([Python repo](https://github.com/Rel8ble/alibaba-product-details-scraper-python))

Need a custom scraper or a ready dataset? Hire me on Fiverr: https://www.fiverr.com/rel8ble
