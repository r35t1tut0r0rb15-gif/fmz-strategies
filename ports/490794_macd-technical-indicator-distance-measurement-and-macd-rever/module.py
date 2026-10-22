"""MACD 12 / 26 / 9 signal crossings, broker days: the cross up closes any short and goes long, the cross down closes any long and goes short.
Port of FMZ strategy #490794 "技术指标距离测量与MACD反转混合量化交易策略-Technical-Indicator-Distance-Measurement-and-MACD-Reversal-Hybrid-Quantitative-Trading-Strategy" (Bysq-Distance Reversal Entry - BTCUSDT (v6)).

FMZ source id: 490794

Source
    https://www.fmz.com/strategy/490794 (PineScript v6, FMZ last modified 2025-04-16 15:19:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-237), MACD 12 / 26 / 9; feature-distance filter (OR-ed with the plain crossing); 10 % of equity
    (distToBullish < distToBearish and crossover(macd, signal)) or crossover(macd, signal) -> close Sell, entry Buy;  mirror -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The distance signals are OR-ed with the plain MACD crossings, so the crossings alone decide (the two
      centroids differ only in the RSI slot). Each signal reverses (REVERSAL INTENDED). Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD signal crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_490794_macd_signal_cross_reversal"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
