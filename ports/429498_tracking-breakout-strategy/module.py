"""Donchian breakout after an opposite touch, 4-hour bars: from flat, a new 20-bar high above the EMA 200 after the
price last touched the low band goes long (mirror short); the stop sits 0.5 % beyond the opposite band and the
target at 1.5 times that risk.
Port of FMZ strategy #429498 "Tracking Breakout Strategy".

FMZ source id: 429498

Source
    https://www.fmz.com/strategy/429498 (PineScript v4, FMZ last modified 2023-10-17 16:36:49).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 197-254), Donchian 20, EMA 200, risk / reward 1.5, pullback 0.995 / 1.005
    flags: high >= upper -> previousishigh; low <= lower -> previousislow; both reset while in a position
    long = previousislow and high >= upper and close > ema200 and flat -> entry long, stop = lower x 0.995, target = close + 1.5 x (close - stop)
    short = previousishigh and low <= lower and close < ema200 and flat -> entry short, stop = upper x 1.005, target = close - 1.5 x (stop - close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest / lowest include the current bar. The bracket is fixed at entry from the signal bar (as
      fractions of its close, shifted one bar inside stops(), re-based on the fill).
    * "Flat" and the flag reset follow the house bracket on bars (the loop marks the position closed once
      a bar's high / low reaches the stop or target from the fill price). Opposite entries cannot occur.
    * The strategy() line is commented out. The date range is dropped. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 4-hour bars: mark coarse_bar_stop. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, channel levels and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() cash quantity stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429498_donchian_after_opposite_touch"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "riskreward": [1.5, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "ema_input": 200, "riskreward": 1.5, "pullback_long": 0.995,
                  "pullback_short": 1.005}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _levels(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    upper, lower = h.rolling(n).max(), lo.rolling(n).min()
    ema = c.ewm(span=int(p["ema_input"]), adjust=False).mean()
    touch_hi = (h >= upper).to_numpy()
    touch_lo = (lo <= lower).to_numpy()
    long_c = ((h >= upper) & (c > ema)).to_numpy()
    short_c = ((lo <= lower) & (c < ema)).to_numpy()
    sl_l = (c - lower * p["pullback_long"]) / c
    sl_s = (upper * p["pullback_short"] - c) / c
    tp_l = (1 - lower * p["pullback_long"] / c) * p["riskreward"]
    tp_s = (1 - c / (upper * p["pullback_short"])) * p["riskreward"]
    return touch_hi, touch_lo, long_c, short_c, sl_l.to_numpy(), sl_s.to_numpy(), tp_l.to_numpy(), tp_s.to_numpy()


def _run(bars_df, p):
    th, tl, lc, sc, sl_l, sl_s, tp_l, tp_s = _levels(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    prev_hi = prev_lo = False
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if th[i]:
            prev_hi = True
        if tl[i]:
            prev_lo = True
        if pos != 0:
            prev_hi = prev_lo = False
        if pos == 0 and prev_lo and lc[i] and sl_l[i] > 0:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl_l[i], tp_l[i]
            sl_arr[i], tp_arr[i] = s_, t_
        if pos == 0 and prev_hi and sc[i] and sl_s[i] > 0:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl_s[i], tp_s[i]
            sl_arr[i], tp_arr[i] = s_, t_
    return le, se, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
