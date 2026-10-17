"""Gimelfarb's bull and bear balance (HPotter), broker days: the bull-minus-bear balance of each bar (a case table of
open, close, high, low and the previous close) at or above +level holds a long, below -level holds a short; the
source's 15-unit level becomes a fraction of the ATR.
Port of FMZ strategy #430899 "Bull and Bear Balance Strategy" (Bull And Bear Balance Strategy).

FMZ source id: 430899

Source
    https://www.fmz.com/strategy/430899 (PineScript v2, FMZ last modified 2023-11-02 17:12:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 163-209), SellLevel -15, BuyLevel 15 (price units)
    value (bear power) and value2 (bull power): nested iff on close vs open, close[1] vs open and the bar's range
    nBBB = value2 - value;  nBBB < -15 -> -1;  nBBB >= 15 -> 1;  else pos[1]
    pos == 1 -> entry long;  pos == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels are price units (15 USD on BTC); they become level_atr x the Wilder ATR
      14 of the bar (15 USD is about 0.015 ATR on daily BTC).
    * The case tables are ported line for line, close[1] compared with the current open as written.
      "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_430899_bull_bear_balance"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level_atr": [0.015, 0.25],
    "atr_len": [14, 28],
}
DEFAULT_PARAMS = {"level_atr": 0.015, "atr_len": 14}


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


def _balance(o, h, lo, c, c1):
    """value2 - value of the source, bar by bar (c1 = close[1]; nan comparisons are false)."""
    if c < o:
        v = max(c - o, h - lo) if c1 > o else h - lo
        v2 = max(h - c1, c - lo) if c1 < o else max(h - o, c - lo)
    elif c > o:
        v = max(c1 - lo, h - c) if c1 > o else max(o - lo, h - c)
        v2 = h - lo if c1 > o else max(o - c1, h - lo)
    elif h - c > c - lo:
        v = max(c1 - o, h - lo) if c1 > o else h - lo
        v2 = max(h - c1, c - lo) if c1 < o else h - o
    elif h - c < c - lo:
        v = (max(c - lo, h - c) if c > o else o - lo)
        v2 = h - lo if c1 > o else max(o - c, h - lo)
    else:
        v = max(c1 - o, h - c) if c > o else (max(o - lo, h - c) if c1 < o else h - lo)
        v2 = max(h - o, c - lo) if c1 > o else (max(o - c, h - lo) if c1 < o else h - lo)
    return v2 - v


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1s = c.shift(1)
    tr = pd.concat([h - lo, (h - c1s).abs(), (lo - c1s).abs()], axis=1).max(axis=1)
    lvl = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["level_atr"])).to_numpy()
    ov, hv, lv, cv, c1 = (x.to_numpy(dtype=float) for x in (o, h, lo, c, c1s))
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        b = _balance(ov[i], hv[i], lv[i], cv[i], c1[i])
        if b < -lvl[i]:
            pos = -1
        elif b >= lvl[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
