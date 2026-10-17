"""EMA 10 / 20 crosses in the EMA 50 trend with an EMA 10 close exit, broker days: EMA 10 crossing above EMA 20 with
the close above EMA 50 goes long; the mirror goes short; a close below EMA 10 (after the last bullish cross) closes
the long, a close above it (after the last bearish cross) closes the short.
Port of FMZ strategy #491892 "EMA双重交叉动态止损量化策略-EMA-Dual-Crossover-Dynamic-Stop-Loss-Quantitative-Strategy" (EMA Crossover Strategy).

FMZ source id: 491892

Source
    https://www.fmz.com/strategy/491892 (PineScript v5, FMZ last modified 2025-04-24 16:59:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 119-166), EMA 10 / 20 / 50
    bullish = crossover(ema10, ema20) and close > ema50;  bearish = crossunder(ema10, ema20) and close < ema50
    isBullish / isBearish = which of the two happened last
    entry long on bullish, short on bearish (strategy.entry reverses)
    close "Long" when isBullish and close < ema10;  close "Short" when isBearish and close > ema10

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are written after the entries: a close acts on the position held at the bar's start, so it does
      not undo a reversal and does not cancel an entry made on the same bar (as #430850).
    * Every signal bar is an entry (a same-side signal while held is ignored by Pine and the engine alike).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_491892_ema_10_20_cross_ema50_trend"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "trend": [50, 100],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20, "trend": 50}


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
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    et = c.ewm(span=int(p["trend"]), adjust=False).mean()
    bull = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (c > et)).to_numpy()
    bear = ((ef < es) & (ef.shift(1) >= es.shift(1)) & (c < et)).to_numpy()
    below, above = (c < ef).to_numpy(), (c > ef).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, is_bull, is_bear = 0, False, False
    for i in range(m):
        start = pos
        if bull[i]:
            is_bull, is_bear = True, False
        if bear[i]:
            is_bull, is_bear = False, True
        if bull[i]:
            pos = 1
        if bear[i]:
            pos = -1
        if start == 1 and pos == 1 and is_bull and below[i]:
            pos = 0
        if start == -1 and pos == -1 and is_bear and above[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
