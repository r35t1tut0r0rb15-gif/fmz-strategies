"""WaveTrend cross (MarketCipher B), broker days: WT1 crossing above its 3-bar average goes long, crossing
below goes short (always in the market after the first cross).
Port of FMZ strategy #428100 "Clear Trend Tracking Strategy" (MarketCipher B).

FMZ source id: 428100

Source
    https://www.fmz.com/strategy/428100 (PineScript v3, FMZ last modified 2023-09-28 16:07:12).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 203-245), channel 9, average 12
    esa = ema(hlc3, 9); d = ema(|hlc3 - esa|, 9); wt1 = ema((hlc3 - esa) / (0.015 d), 12); wt2 = sma(wt1, 3)
    crossover(wt1, wt2) -> entry long (close short); crossover(wt2, wt1) -> entry short (close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stochastic RSI, divergences, RSI+MFI area (its VWMA option off) and alerts are drawn only;
      no order uses them.
    * The equity-based order size is sizing. The closes coincide with the opposite entries:
      REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based order size stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the drawn-only VWMA option is off.
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428100_wavetrend_cross"
FAMILY = "wavetrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n1": [9, 10],
    "n2": [12, 21],
}
DEFAULT_PARAMS = {"n1": 9, "n2": 12}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ap = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d)).ewm(span=int(p["n2"]), adjust=False).mean()
    wt2 = wt1.rolling(3).mean()
    up = ((wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))).to_numpy()
    dn = ((wt2 > wt1) & (wt2.shift(1) <= wt1.shift(1))).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
