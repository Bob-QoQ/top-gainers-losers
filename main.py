"""
Top Gainers / Losers — CLI
Fetches 24h price change stats from Binance and ranks tokens by percentage move.
"""

import argparse
import sys
import requests


BASE_URL = "https://api.binance.com/api/v3"


def fetch_tickers():
    resp = requests.get(f"{BASE_URL}/ticker/24hr", timeout=30)
    resp.raise_for_status()
    return resp.json()


def fmt_price(s):
    try:
        v = float(s)
        if v >= 1000:
            return f"{v:,.2f}"
        if v >= 1:
            return f"{v:.4f}"
        return f"{v:.8f}"
    except (ValueError, TypeError):
        return str(s)


def fmt_vol(s):
    try:
        v = float(s)
        if v >= 1_000_000_000:
            return f"${v / 1_000_000_000:.2f}B"
        if v >= 1_000_000:
            return f"${v / 1_000_000:.2f}M"
        if v >= 1_000:
            return f"${v / 1_000:.1f}K"
        return f"${v:.2f}"
    except (ValueError, TypeError):
        return str(s)


def filter_tickers(tickers, quote, min_vol):
    result = []
    suffix = quote.upper()
    for t in tickers:
        sym = t.get("symbol", "")
        if not sym.endswith(suffix):
            continue
        try:
            vol = float(t.get("quoteVolume") or 0)
        except ValueError:
            vol = 0
        if vol < min_vol:
            continue
        result.append(t)
    return result


def cmd_gainers(args):
    tickers = fetch_tickers()
    tickers = filter_tickers(tickers, args.quote, args.min_vol)
    tickers.sort(key=lambda t: float(t.get("priceChangePercent") or 0), reverse=True)
    tickers = tickers[: args.limit]

    print(f"Top {args.limit} Gainers (24h) — {args.quote.upper()} pairs, min vol {fmt_vol(str(args.min_vol))}\n")
    print(f"{'#':<4} {'Symbol':<15} {'Change':>8} {'Price':>14} {'Volume':>12}")
    print("-" * 58)
    for i, t in enumerate(tickers, 1):
        pct = float(t.get("priceChangePercent") or 0)
        print(
            f"{i:<4} {t.get('symbol'):<15}"
            f" {pct:>+7.2f}%"
            f" {fmt_price(t.get('lastPrice')):>14}"
            f" {fmt_vol(t.get('quoteVolume')):>12}"
        )


def cmd_losers(args):
    tickers = fetch_tickers()
    tickers = filter_tickers(tickers, args.quote, args.min_vol)
    tickers.sort(key=lambda t: float(t.get("priceChangePercent") or 0))
    tickers = tickers[: args.limit]

    print(f"Top {args.limit} Losers (24h) — {args.quote.upper()} pairs, min vol {fmt_vol(str(args.min_vol))}\n")
    print(f"{'#':<4} {'Symbol':<15} {'Change':>8} {'Price':>14} {'Volume':>12}")
    print("-" * 58)
    for i, t in enumerate(tickers, 1):
        pct = float(t.get("priceChangePercent") or 0)
        print(
            f"{i:<4} {t.get('symbol'):<15}"
            f" {pct:>+7.2f}%"
            f" {fmt_price(t.get('lastPrice')):>14}"
            f" {fmt_vol(t.get('quoteVolume')):>12}"
        )


def cmd_movers(args):
    tickers = fetch_tickers()
    tickers = filter_tickers(tickers, args.quote, args.min_vol)

    sorted_desc = sorted(tickers, key=lambda t: float(t.get("priceChangePercent") or 0), reverse=True)
    gainers = sorted_desc[: args.limit]
    losers = sorted(tickers, key=lambda t: float(t.get("priceChangePercent") or 0))[: args.limit]

    def print_table(items, label):
        print(f"\n{label}")
        print(f"{'#':<4} {'Symbol':<15} {'Change':>8} {'Price':>14} {'Volume':>12}")
        print("-" * 58)
        for i, t in enumerate(items, 1):
            pct = float(t.get("priceChangePercent") or 0)
            print(
                f"{i:<4} {t.get('symbol'):<15}"
                f" {pct:>+7.2f}%"
                f" {fmt_price(t.get('lastPrice')):>14}"
                f" {fmt_vol(t.get('quoteVolume')):>12}"
            )

    print(f"Market Movers Report — {args.quote.upper()} pairs, min vol {fmt_vol(str(args.min_vol))}")
    print_table(gainers, f"Top {args.limit} Gainers")
    print_table(losers, f"Top {args.limit} Losers")


def main():
    parser = argparse.ArgumentParser(description="Find top gainers/losers using Binance 24h ticker data.")
    parser.add_argument("--quote", default="USDT", help="Quote asset filter (default: USDT)")
    parser.add_argument(
        "--min-vol",
        type=float,
        default=1_000_000,
        help="Minimum 24h quote volume in USD (default: 1000000)",
    )
    parser.add_argument("--limit", type=int, default=10, help="Number of results (default: 10)")

    sub = parser.add_subparsers(dest="command")

    p_gain = sub.add_parser("gainers", help="Top gainers by 24h %% change")
    p_gain.set_defaults(func=cmd_gainers)

    p_lose = sub.add_parser("losers", help="Top losers by 24h %% change")
    p_lose.set_defaults(func=cmd_losers)

    p_movers = sub.add_parser("movers", help="Combined gainers and losers report")
    p_movers.set_defaults(func=cmd_movers)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        args.func = cmd_movers

    try:
        args.func(args)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
