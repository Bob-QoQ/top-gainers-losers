# Top Gainers / Losers

Identify the top gaining and losing tokens over the past 24 hours using Binance ticker data.

## Quick Start

```bash
pip install -r requirements.txt
python main.py --help
```

```
usage: main.py [-h] [--quote QUOTE] [--min-vol MIN_VOL] [--limit LIMIT]
               {gainers,losers,movers} ...

Find top gainers/losers using Binance 24h ticker data.

positional arguments:
  {gainers,losers,movers}
    gainers             Top gainers by 24h % change
    losers              Top losers by 24h % change
    movers              Combined gainers and losers report

options:
  --quote QUOTE         Quote asset filter (default: USDT)
  --min-vol MIN_VOL     Minimum 24h quote volume in USD (default: 1000000)
  --limit LIMIT         Number of results (default: 10)
```

## Example Output

```
Market Movers Report — USDT pairs, min vol $1.00M

Top 10 Gainers
#    Symbol            Change          Price       Volume
----------------------------------------------------------
1    ENJUSDT          +54.95%     0.02955000      $13.29M
2    ANKRUSDT         +28.98%     0.00592000      $19.58M
3    CHRUSDT          +16.77%     0.01880000       $2.53M
4    POLYXUSDT        +16.32%     0.04990000      $21.91M
5    STOUSDT          +12.82%     0.07920000       $4.43M
6    CTSIUSDT         +12.32%     0.02872000       $1.91M
7    HOTUSDT          +11.26%     0.00048400       $3.91M
8    VANRYUSDT         +9.68%     0.00641400      $16.64M
9    WUSDT             +7.87%     0.01920000      $10.11M
10   AUCTIONUSDT       +7.20%         5.2100       $6.17M
```

**Data source:** [Binance Public API](https://api.binance.com) — free, no auth required.
