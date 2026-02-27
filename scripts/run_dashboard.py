import sys
from pathlib import Path
import argparse

# Ensure project root is on PYTHONPATH so `src` can be imported reliably
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dashboard import build_dashboard_html


def main():
    p = argparse.ArgumentParser(description="Canadian Equity Dashboard (TSX-focused)")
    p.add_argument("--ticker", required=True, help="e.g., RY or RY.TO (RY defaults to .TO)")
    p.add_argument("--period", default="5y", help="yfinance period string (e.g., 1y, 5y, max)")
    p.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: outputs/<ticker>_<period>.html)",
    )
    args = p.parse_args()

    outdir = Path("outputs")
    outdir.mkdir(parents=True, exist_ok=True)

    if args.out is None:
        safe_ticker = args.ticker.replace(".", "_").upper()
        safe_period = args.period.replace("/", "_")
        out_path = outdir / f"{safe_ticker}_{safe_period}.html"
    else:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)

    saved = build_dashboard_html(ticker=args.ticker, period=args.period, out_html=str(out_path))
    print(f"Saved dashboard to: {saved}")


if __name__ == "__main__":
    main()
