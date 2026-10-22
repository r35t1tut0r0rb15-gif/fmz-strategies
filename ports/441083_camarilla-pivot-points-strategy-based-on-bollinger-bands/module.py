"""Camarilla levels of the previous day, 1-hour bars: the close above the previous day's L1 goes long, otherwise (the close under H1) short, as the script names them; reversing.
Port of FMZ strategy #441083 "Camarilla Pivot Points Strategy Based on Bollinger Bands" (CPP V2).

FMZ source id: 441083

Source
    https://www.fmz.com/strategy/441083 (PineScript v4, FMZ last modified 2024-02-05 14:23:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-165), resolution D; width 1 (unused); sell from R1, buy from S1; reverse off
    H1 = xClose + 0.0916 (xHigh - xLow), L1 = xClose - 0.0916 (xHigh - xLow) from security(D);  S = H1 (BuyFrom S1), B = L1 (SellFrom R1)
    pos = close > B ? 1 : close < S ? -1 : pos[1];  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar: xHigh, xLow and
      xClose are the previous broker day's high, low and close, built from the module's own bars. The
      inputs map "S1" to H1 and "R1" to L1, as written, so the close above L1 reads long and the close at
      or under L1 (below H1) reads short. The state starts at 0 (flat). REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed days.
    2 generic: PASS, Camarilla levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily levels on the broker day (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441083_camarilla_l1_prev_day_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level_k": [0.0916, 0.183],
}
DEFAULT_PARAMS = {"level_k": 0.0916, "reverse": False}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    dh = h.groupby(day).max().shift(1).reindex(day)          # last completed day
    dl = lo.groupby(day).min().shift(1).reindex(day)
    dc = c.groupby(day).last().shift(1).reindex(day)
    rng = pd.Series((dh - dl).to_numpy(), index=c.index)
    xc = pd.Series(dc.to_numpy(), index=c.index)
    k = float(p["level_k"])
    s_lv = xc + k * rng      # "S1" -> H1
    b_lv = xc - k * rng      # "R1" -> L1
    up, dn = (c > b_lv).to_numpy(), (c < s_lv).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
