"""Green bars undercutting the last big red candle's low, 1-hour bars, long only: after a red bar with a range of 20 price units or more (0.000476 of the close at BTC 42000), a green bar whose low is under that red bar's low buys. The exit re-sent every bar from the current close is not ported (pending), so the port has no exit.
Port of FMZ strategy #458026 "Big Red Candle Breakout Buy Strategy" (Red Candle Breakout Buy Strategy).

FMZ source id: 458026

Source
    https://www.fmz.com/strategy/458026 (PineScript v5, FMZ last modified 2024-07-29 13:31:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-202), big red candle range 20 points; stop 20 / target 50 points from the current close (every bar); quantity 1, +1 per 150 % open profit; capital 24000
    high - low >= 20 and close < open -> red low = low;  detected and low < red low and close > open -> entry Buy (qty)
    every bar: exit(stop = close - 20, limit = close + 50)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 20-point range is a price amount, read against BTC near 42000 (#440456) as 20 / 42000 of the
      close. The bracket is re-sent on every bar from that bar's close, so its levels move with the
      price; stops() cannot express this: it is not ported and the module gets the mark
      trailing_stop_pending (as #438034); without it the port has no exit (one long held from the
      first signal), as #451391. The quantity growth is sizing. Long only. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-bar bracket pending (mark).
    2 generic: PASS, big-red-candle undercut reversals.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity rule and capital stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458026_big_red_candle_low_undercut_long"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "range_frac": [0.000476, 0.01],
}
DEFAULT_PARAMS = {"range_frac": 0.000476}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    big = ((h - lo) >= float(p["range_frac"]) * c) & (c < o)
    bv, lv = big.to_numpy(), lo.to_numpy(dtype=float)
    green = (c > o).to_numpy()
    m = len(lv)
    le = np.zeros(m, dtype=bool)
    red_low = np.nan
    for i in range(m):
        if bv[i]:
            red_low = lv[i]
        le[i] = not np.isnan(red_low) and lv[i] < red_low and green[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
