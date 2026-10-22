"""First touch of an EMA 5 from above, 2-hour bars, short only: a bar whose low touches the EMA 5 while closing above it, after a bar fully above it, goes short; the stop at the previous high and the
target three times the previous bar's high-open distance under its open.
Port of FMZ strategy #443231 "突破EMA滑动止损三角策略Elevated-Touch-Short-Triangle-Strategy" (SE-EMA-SL-TP-Viz (Short Entry EMA Strategy with Visual SL and TP)).

FMZ source id: 443231

Source
    https://www.fmz.com/strategy/443231 (PineScript v5, FMZ last modified 2024-03-01 11:02:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-144), EMA 5; R:R 3 (from the previous bar's open and high)
    close > ema and low <= ema and low[1] > ema[1] and close[1] > ema[1] -> entry Short, exit(stop = high[1], limit = open[1] - 3 (high[1] - open[1]))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels come from the previous bar and are fixed on the signal bar: sl_stop = high[1] / close
      - 1 and tp_stop = 1 - (open[1] - 3 (high[1] - open[1])) / close of the signal bar, shifted one bar
      inside stops() and re-based on the fill; a level on the wrong side of the close gives no order. A
      new signal while short moves the script's levels, which the port does not follow (as #439608).
      Short only. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from bar data.
    2 generic: PASS, first EMA touch from above.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_443231_ema5_first_touch_prev_bar_bracket_short"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_period": [5, 10],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"ema_period": 5, "rr": 3.0}


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


def _fractions(bars_df, p):
    o, h, c = bars_df["open"], bars_df["high"], bars_df["close"]
    o1, h1 = o.shift(1), h.shift(1)
    sl = (h1 / c - 1).where(h1 > c)
    tp_level = o1 - float(p["rr"]) * (h1 - o1)
    tp = (1 - tp_level / c).where(tp_level < c)
    return sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    sig = ((c > e) & (lo <= e) & (lo.shift(1) > e.shift(1)) & (c.shift(1) > e.shift(1))).to_numpy()
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    se = np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == -1 and i >= entry_i:
            x = ov[entry_i]
            if (not np.isnan(s_) and hv[i] >= x * (1 + s_)) or (not np.isnan(t_) and lv[i] <= x * (1 - t_)):
                pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
