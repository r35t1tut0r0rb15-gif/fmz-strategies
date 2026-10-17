"""Fast stochastic %K extremes, broker days: %K (5) below 5 goes long and above 90 closes the long; above 95 goes short
and below 10 closes the short.
Port of FMZ strategy #488889 "5分钟K线KDJ指标动态响应交易策略-5-Minute-KDJ-Indicator-Dynamic-Response-Trading-Strategy" (Demo GPT - KDJ Strategy).

FMZ source id: 488889

Source
    https://www.fmz.com/strategy/488889 (PineScript v6, FMZ last modified 2025-03-31 16:26:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 202-237), stochastic 5, smoothing 1 / 1
    k = stoch(close, high, low, 5);  k < 5 -> entry long;  k > 90 -> close long;  k > 95 -> entry short;  k < 10 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Source order on each bar: long entry, long close, short entry, short close; a close acts on the position held
      at the bar's start (as #430850), so a k > 95 bar closes a long and reverses to short. REVERSAL INTENDED.
    * The title's "5-minute" is a label; the slippage in strategy() is a cost. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an oscillator only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the full-equity quantity quoted in original_sizing.txt.
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

NAME = "fmz_488889_fast_stoch_k_extremes"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 14],
    "entry_band": [5, 15],
}
DEFAULT_PARAMS = {"length": 5, "entry_band": 5, "long_exit": 90, "short_exit": 10}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).where(hh != ll).to_numpy(dtype=float)
    band = float(p["entry_band"])
    m = len(k)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if k[i] < band:
            pos = 1
        if k[i] > p["long_exit"] and start == 1 and pos == 1:
            pos = 0
        if k[i] > 100 - band:
            pos = -1
        if k[i] < p["short_exit"] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
