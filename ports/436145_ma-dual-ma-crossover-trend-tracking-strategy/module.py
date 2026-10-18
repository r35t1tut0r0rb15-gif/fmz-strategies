"""EMA 14 / 21 of the open, 1-hour bars: the fast average rising to or over the slow one goes long, falling under it goes short (reversing; the "invert" input flips it); each trade has a
tick-sized stop and target re-expressed as ATR multiples. The trailing stop needs an offset and has none, so it is inactive.
Port of FMZ strategy #436145 "双MA交叉趋势追踪策略Dual-MA-Crossover-Trend-Tracking-Strategy" (Strategy Code Example (Dual MA)).

FMZ source id: 436145

Source
    https://www.fmz.com/strategy/436145 (PineScript v2, FMZ last modified 2023-12-21 16:10:22).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 156-206), EMA 14 / 21 of the open; target 1000, stop 200, trail points 200, trail offset 0 (all in ticks)
    aboveBelow = fast >= slow;  tradeDirection = invert ? not aboveBelow : aboveBelow;  enterLong = not tradeDirection[1] and tradeDirection;  exitLong = the reverse change;  enterShort = exitLong;  exit(profit = 1000, loss = 200, trail_points = 200, trail_offset = na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are the CHANGES of the state; the explicit closes coincide with the reversal.
      Criterion 2: the tick amounts (1000 / 200 ticks) are re-expressed as sl_stop = k_atr x ATR / close
      and tp_stop = 5 x sl_stop of the signal bar, shifted one bar inside stops() (re-based on the
      fill); 0.07 is the reading (a 20 USD stop on BTC against a 1-hour ATR near 300), 1.0 a volatility-sized
      stop. trail_points without a trail_offset does not start a trailing stop, so it is not ported.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-hour bars: not
      coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick amounts -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436145_ema_open_state_change_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "invert": [False, True],
    "k_atr": [0.07, 1.0],
}
DEFAULT_PARAMS = {"invert": False, "k_atr": 0.07, "fast": 14, "slow": 21, "tp_ratio": 5.0, "atr_len": 14}


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
    o = bars_df["open"]
    fast = o.ewm(span=int(p["fast"]), adjust=False).mean()
    slow = o.ewm(span=int(p["slow"]), adjust=False).mean()
    above = (fast >= slow)
    direction = ~above if p["invert"] else above
    prev = direction.shift(1, fill_value=False)
    le = (~prev & direction).astype(bool)
    se = (prev & ~direction).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f * float(p["tp_ratio"])}


def portfolio_kwargs(**params):
    return {}
