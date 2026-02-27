# Final version of the function, output should be html file:
# Usage: build_dashboard_html("^GSPC", period="1y", out_html="GSPC_dash.html")

from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def normalize_canadian_ticker(ticker: str) -> str:
    """
    TSX-focused normalization.

    - If ticker starts with '^', treat as index and do not modify.
    - If no suffix provided, assume TSX and append '.TO'.
    - Otherwise return as provided.
    """
    t = ticker.strip().upper()

    if t.startswith("^"):
        return t  # allow index symbols like ^GSPTSE

    if "." not in t:
        return f"{t}.TO"

    return t


def max_drawdown(series: pd.Series) -> float:
    """Return max drawdown as a negative fraction (e.g., -0.35)."""
    # Guard: ensure numeric series and no NaNs
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        warnings.warn("Max drawdown could not be computed (empty return series).", RuntimeWarning)
        return float("nan")

    cumulative = (1 + s).cumprod()
    peak = cumulative.cummax()
    dd = (cumulative / peak) - 1
    out = float(dd.min())

    if not np.isfinite(out):
        warnings.warn("Max drawdown computed to a non-finite value.", RuntimeWarning)
        return float("nan")

    return out


def compute_metrics(df: pd.DataFrame) -> dict:
    """
    Expects columns: Date, Close, Volume
    Adds returns & computes summary metrics.
    """
    required = {"Date", "Close", "Volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"compute_metrics missing required columns: {sorted(missing)}")

    d = df.copy()
    d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
    d["Close"] = pd.to_numeric(d["Close"], errors="coerce")
    d = d.dropna(subset=["Date", "Close"])

    d["Return"] = d["Close"].pct_change()
    d = d.dropna(subset=["Return"])

    # Default outputs (in case something cannot be computed)
    total_return = float("nan")
    cagr = float("nan")
    vol = float("nan")
    mdd = float("nan")

    if len(d) < 2:
        warnings.warn(
            "Not enough data points to compute return-based metrics (need at least 2).",
            RuntimeWarning,
        )
        start = d["Date"].iloc[0].date().isoformat() if len(d) >= 1 else "N/A"
        end = d["Date"].iloc[-1].date().isoformat() if len(d) >= 1 else "N/A"
        return {
            "Start": start,
            "End": end,
            "Total Return": total_return,
            "CAGR": cagr,
            "Annualized Volatility": vol,
            "Max Drawdown": mdd,
        }

    # Total return
    try:
        total_return = (d["Close"].iloc[-1] / d["Close"].iloc[0]) - 1
        if not np.isfinite(total_return):
            warnings.warn("Total Return computed to a non-finite value.", RuntimeWarning)
            total_return = float("nan")
    except Exception as e:
        warnings.warn(f"Total Return could not be computed: {e}", RuntimeWarning)
        total_return = float("nan")

    # CAGR
    try:
        days = (d["Date"].iloc[-1] - d["Date"].iloc[0]).days
        years = days / 365.25
        if years <= 0:
            warnings.warn("CAGR could not be computed (non-positive time span).", RuntimeWarning)
            cagr = float("nan")
        elif np.isfinite(total_return):
            cagr = (1 + total_return) ** (1 / years) - 1
            if not np.isfinite(cagr):
                warnings.warn("CAGR computed to a non-finite value.", RuntimeWarning)
                cagr = float("nan")
        else:
            warnings.warn("CAGR skipped because Total Return is not finite.", RuntimeWarning)
            cagr = float("nan")
    except Exception as e:
        warnings.warn(f"CAGR could not be computed: {e}", RuntimeWarning)
        cagr = float("nan")

    # Volatility (annualized) from daily returns
    try:
        vol = d["Return"].std() * np.sqrt(252)
        if not np.isfinite(vol):
            warnings.warn("Annualized Volatility computed to a non-finite value.", RuntimeWarning)
            vol = float("nan")
    except Exception as e:
        warnings.warn(f"Annualized Volatility could not be computed: {e}", RuntimeWarning)
        vol = float("nan")

    # Max drawdown from daily returns
    mdd = max_drawdown(d["Return"])

    return {
        "Start": d["Date"].iloc[0].date().isoformat(),
        "End": d["Date"].iloc[-1].date().isoformat(),
        "Total Return": float(total_return) if np.isfinite(total_return) else float("nan"),
        "CAGR": float(cagr) if np.isfinite(cagr) else float("nan"),
        "Annualized Volatility": float(vol) if np.isfinite(vol) else float("nan"),
        "Max Drawdown": float(mdd) if np.isfinite(mdd) else float("nan"),
    }


def build_dashboard_html(ticker: str, period: str, out_html: str) -> str:
    t = normalize_canadian_ticker(ticker)

    hist = yf.Ticker(t).history(period=period)

    if hist is None or hist.empty:
        raise ValueError(f"No price data returned for ticker: {t}")

    df = hist.reset_index()[["Date", "Close", "Volume"]].copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

    df = df.dropna(subset=["Date", "Close", "Volume"])
    if df.empty:
        raise ValueError(f"Price data returned for {t}, but could not be parsed into numeric Date/Close/Volume.")

    # Indicators
    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    df["Return"] = df["Close"].pct_change()
    df["Vol30"] = df["Return"].rolling(30).std() * np.sqrt(252)

    metrics = compute_metrics(df[["Date", "Close", "Volume"]])

    # Build figure: 4 rows (VISUALS UNCHANGED)
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=("Close Price (with 50/200D MA)", "Volume", "Daily Returns", "Rolling Volatility (30D, annualized)")
    )

    # Price + MAs
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], name="MA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA200"], name="MA200"), row=1, col=1)

    # Volume
    fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume"), row=2, col=1)

    # Returns
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Return"], name="Daily Return"), row=3, col=1)

    # Volatility
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Vol30"], name="Vol30"), row=4, col=1)

    # ---- Y-Axis Labels (VISUALS UNCHANGED) ----
    fig.update_yaxes(title_text="Price (CAD)", row=1, col=1, title_font=dict(size=15))
    fig.update_yaxes(title_text="Volume (Shares)", row=2, col=1, title_font=dict(size=15))
    fig.update_yaxes(title_text="Daily Return", row=3, col=1, title_font=dict(size=15))
    fig.update_yaxes(title_text="Volatility (Annualized)", row=4, col=1, title_font=dict(size=15))

    # Metrics annotation (same layout; show N/A if metric missing)
    def pct(x):
        return "N/A" if (x is None or not np.isfinite(x)) else f"{x*100:.2f}%"

    summary_lines = [
        f"Ticker: {t}",
        f"Range: {metrics['Start']} → {metrics['End']}",
        f"Total Return: {pct(metrics['Total Return'])}",
        f"CAGR: {pct(metrics['CAGR'])}",
        f"Ann. Volatility: {pct(metrics['Annualized Volatility'])}",
        f"Max Drawdown: {pct(metrics['Max Drawdown'])}",
    ]
    summary = "<br>".join(summary_lines)

    fig.update_layout(
        title=f"Canadian Equity Dashboard — {t} ({period})",
        template="presentation",
        height=1000,
        margin=dict(t=90, b=40, l=80, r=30),
        annotations=list(fig.layout.annotations) + [
            dict(
                x=0.01, y=1.14, xref="paper", yref="paper",
                showarrow=False, align="left",
                text=summary, font=dict(size=12)
            )
        ]
    )

    fig.write_html(out_html, include_plotlyjs="cdn")
    return out_html
