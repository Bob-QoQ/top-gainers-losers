---
title: Top Gainers / Losers
description: |
  Identify the top gaining and losing tokens over the past 24 hours using the Binance public API.
  Filter by quote asset (USDT, BTC, ETH, BNB) and minimum volume to surface the biggest market movers.
metadata:
  author: Bob-QoQ
  version: "1.0"
license: MIT
---

# Top Gainers / Losers

Identify the top gaining and losing tokens over the past 24 hours using the Binance public API. This skill enables AI agents to fetch rolling 24-hour price change statistics for all trading pairs, filter by quote asset, and rank by percentage change to surface the biggest movers in the market.

## API Base URL

```
https://api.binance.com/api/v3
```

No authentication required. All endpoints below are public.

---

## Endpoints

### 1. 24-Hour Ticker Stats (All Symbols)

Returns rolling 24-hour price change statistics for every listed trading pair. Use this as the data source for computing gainers and losers.

```
GET https://api.binance.com/api/v3/ticker/24hr
```

**Query parameters:**

| Parameter | Type   | Required | Description                                                                               |
|-----------|--------|----------|-------------------------------------------------------------------------------------------|
| `symbol`  | string | No       | Restrict to a single trading pair (e.g., `BTCUSDT`). Omit to get all pairs.              |
| `symbols` | string | No       | JSON array of symbols as URL-encoded string (e.g., `["BTCUSDT","ETHUSDT"]`). Max 100.    |
| `type`    | string | No       | `FULL` (default) or `MINI`. `MINI` returns a reduced field set (symbol, open/close/high/low, volume). |

**Response fields (`FULL` type):**

| Field                | Type   | Description                                          |
|----------------------|--------|------------------------------------------------------|
| `symbol`             | string | Trading pair symbol (e.g., `SOLUSDT`)                |
| `priceChange`        | string | Absolute price change over 24h                       |
| `priceChangePercent` | string | Percentage price change over 24h (key ranking field) |
| `weightedAvgPrice`   | string | Volume-weighted average price over 24h               |
| `prevClosePrice`     | string | Previous closing price                               |
| `lastPrice`          | string | Most recent trade price                              |
| `openPrice`          | string | Price at start of 24h rolling window                 |
| `highPrice`          | string | 24h high price                                       |
| `lowPrice`           | string | 24h low price                                        |
| `volume`             | string | Total base asset volume traded                       |
| `quoteVolume`        | string | Total quote asset volume traded (USD if USDT-paired) |
| `openTime`           | number | Unix ms — start of 24h window                        |
| `closeTime`          | number | Unix ms — end of 24h window                          |
| `count`              | number | Number of trades in 24h                              |

**Example request (all symbols):**

```http
GET https://api.binance.com/api/v3/ticker/24hr
```

**Example response (two items, trimmed from full array):**

```json
[
  {
    "symbol": "NEOBTC",
    "priceChange": "0.00000084",
    "priceChangePercent": "2.223",
    "weightedAvgPrice": "0.00003833",
    "prevClosePrice": "0.00003740",
    "lastPrice": "0.00003862",
    "openPrice": "0.00003778",
    "highPrice": "0.00003897",
    "lowPrice": "0.00003778",
    "volume": "12886.56000000",
    "quoteVolume": "0.49399261",
    "openTime": 1773731959776,
    "closeTime": 1773818359776,
    "count": 892
  },
  {
    "symbol": "ETHBTC",
    "priceChange": "-0.00002000",
    "priceChangePercent": "-0.064",
    "weightedAvgPrice": "0.03139989",
    "prevClosePrice": "0.03140000",
    "lastPrice": "0.03137000",
    "openPrice": "0.03139000",
    "highPrice": "0.03166000",
    "lowPrice": "0.03112000",
    "volume": "14264.35390000",
    "quoteVolume": "447.89920128",
    "openTime": 1773731962364,
    "closeTime": 1773818362364,
    "count": 47072
  }
]
```

---

### 2. Single Symbol Stats

Fetch 24h stats for a single known pair.

```
GET https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT
```

**Example response:**

```json
{
  "symbol": "BTCUSDT",
  "priceChange": "-2150.50000000",
  "priceChangePercent": "-2.641",
  "weightedAvgPrice": "80421.83000000",
  "prevClosePrice": "81432.00000000",
  "lastPrice": "79281.50000000",
  "openPrice": "81432.00000000",
  "highPrice": "82100.00000000",
  "lowPrice": "78900.00000000",
  "volume": "21340.87500000",
  "quoteVolume": "1716023456.25000000",
  "openTime": 1773731962000,
  "closeTime": 1773818362000,
  "count": 4102341
}
```

---

## Filtering and Ranking Strategy

### Step-by-step: Top N Gainers from USDT pairs

```
1. GET https://api.binance.com/api/v3/ticker/24hr
   (returns ~2400+ objects — weight cost: 80)

2. Filter by quote asset:
   keep items where symbol.endsWith("USDT")

3. (Optional) Filter by minimum volume to exclude illiquid tokens:
   keep items where parseFloat(quoteVolume) > 1_000_000

4. Parse and sort by priceChangePercent descending:
   items.sort((a, b) => parseFloat(b.priceChangePercent) - parseFloat(a.priceChangePercent))

5. Take first N items for top gainers, last N items for top losers.

6. Return for each: symbol, lastPrice, priceChangePercent, priceChange, quoteVolume
```

### Quote asset filter reference

| Quote asset | Symbol suffix | Use case                          |
|-------------|---------------|-----------------------------------|
| USDT        | `USDT`        | USD-denominated pairs (most common) |
| BTC         | `BTC`         | BTC-denominated pairs             |
| ETH         | `ETH`         | ETH-denominated pairs             |
| BNB         | `BNB`         | BNB-denominated pairs             |
| BUSD        | `BUSD`        | Legacy BUSD pairs                 |

Filter by checking if `symbol.endsWith("<QUOTE_ASSET>")`.

### Minimum volume filter (recommended)

Low-volume tokens with tiny float can show extreme % moves (e.g., +5000%) that are noise. A minimum `quoteVolume` threshold removes these:

| Market context | Recommended min `quoteVolume` (USDT) |
|----------------|--------------------------------------|
| Strict / liquid only | 5,000,000 |
| Moderate        | 1,000,000 |
| Include small caps | 100,000 |

---

## Example Agent Workflows

### Get top 10 USDT gainers (liquid only)

```
1. GET https://api.binance.com/api/v3/ticker/24hr
2. Filter: symbol.endsWith("USDT")
3. Filter: parseFloat(quoteVolume) >= 1_000_000
4. Sort by parseFloat(priceChangePercent) descending
5. Return top 10: symbol, lastPrice, priceChangePercent, quoteVolume
```

**Example output:**

```
#1  XYZUSDT   +34.72%   $0.00431   Vol: $8.2M
#2  ABCUSDT   +28.15%   $1.245     Vol: $22.1M
#3  FOOУСDT   +21.88%   $0.0821    Vol: $5.4M
...
```

### Get top 10 USDT losers

```
1. Same as above (steps 1–3)
4. Sort by parseFloat(priceChangePercent) ascending
5. Return top 10 (most negative first)
```

### Get combined movers report (gainers + losers)

```
1. GET https://api.binance.com/api/v3/ticker/24hr
2. Filter: endsWith("USDT") AND quoteVolume >= 1_000_000
3. Sort descending → top 5 gainers
4. Sort ascending → top 5 losers
5. Return both lists in one response
```

### Find tokens near their 24h high (momentum signal)

```
1. GET https://api.binance.com/api/v3/ticker/24hr
2. Filter: endsWith("USDT")
3. For each: proximity = (lastPrice - highPrice) / highPrice * 100
4. Filter: proximity >= -2  (within 2% of 24h high)
5. Filter: priceChangePercent > 5  (also up on the day)
6. Sort by priceChangePercent descending
7. Return symbol, lastPrice, highPrice, priceChangePercent
```

### Detect unusual volume spikes

```
1. GET https://api.binance.com/api/v3/ticker/24hr
2. Filter: endsWith("USDT")
3. Rank by quoteVolume descending to find highest-volume movers
4. Cross-reference with priceChangePercent to separate buy-driven vs sell-driven volume
```

---

## Rate Limits

| Endpoint                         | Weight (single symbol) | Weight (all symbols) |
|----------------------------------|------------------------|----------------------|
| `GET /ticker/24hr`               | 2                      | 80                   |

**Global limits:**

| Type            | Limit                  |
|-----------------|------------------------|
| Request weight  | 6,000 per minute       |
| Raw requests    | 61,000 per 5 minutes   |

Rate limit headers in every response:
- `X-MBX-USED-WEIGHT-1M` — weight consumed this minute

**Best practice:** Cache the full `GET /ticker/24hr` response for 30–60 seconds. The data refreshes every ~1 second server-side, but polling faster than once per minute provides diminishing returns and burns weight budget fast.

---

## Usage Notes

### All numeric values are strings
`priceChangePercent`, `lastPrice`, `volume`, and `quoteVolume` are all decimal strings. Always parse with `parseFloat()` before comparison or arithmetic.

### Negative percentages are valid strings
`"-12.345"` is a valid `priceChangePercent` value. Sort works correctly after `parseFloat()` conversion.

### Symbol format
Binance symbols concatenate base + quote with no separator: `BTCUSDT` = BTC priced in USDT. Extract the base asset by stripping the known quote suffix (e.g., remove `"USDT"` from the end).

### Market hours
Crypto markets run 24/7. The 24h window is rolling (not midnight-to-midnight).

---

## Error Handling

| HTTP Status | Code     | Meaning                                             |
|-------------|----------|-----------------------------------------------------|
| `200`       | —        | Success                                             |
| `400`       | `-1121`  | Invalid symbol — check spelling and availability    |
| `429`       | —        | Rate limited — back off, retry after `Retry-After`  |
| `418`       | —        | IP banned after repeated 429 violations             |
| `500`       | —        | Binance internal error — retry with exponential backoff |
