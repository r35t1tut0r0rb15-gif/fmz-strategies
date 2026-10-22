"""Close crossings over the EMA 34, hourly bars, long only, one trade at a time by flag: the cross goes long with a stop at the previous bar's low and a 10 R target, the stop moving to the entry close after a close 3 R up; a bar reaching either level sends a close.
Port of FMZ strategy #489638 "EMA-34-动态止损交叉策略趋势跟踪与风险管理的智能结合-EMA-34-Dynamic-Stop-Loss-Crossover-Strategy-Intelligent-Combination-of-Trend-Following-and-Risk-Management" (EMA 34 Crossover with Break Even Stop Loss).

FMZ source id: 489638

Source
    https://www.fmz.com/strategy/489638 (PineScript v5, FMZ last modified 2025-04-07 11:39:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 185-228), EMA 34; stop low[1]; target 10 R; break-even at 3 R (close-tested); 100 % of equity
    crossover(close, ema34) and not inTrade -> entry := close, stop := low[1], target := entry + 10 R, entry Long, inTrade
    inTrade and close >= entry + 3 R -> stop := entry;  inTrade and low <= stop -> close Long;  inTrade and high >= target -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are tested against the bar's low / high but sent as closes (exit signals filled at the next
      open, no stop module); the inTrade flag, levels and break-even move are followed in a loop, as
      written (an exit on the entry's own bar clears the flag while the order still fills). Long only.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; level touches sent as closes.
    2 generic: PASS, EMA crossings with a candle-low stop, R target and break-even move.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489638_close_ema34_cross_prevlow_stop_10r_breakeven_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [34, 20],
    "rr": [10.0, 3.0],
}
DEFAULT_PARAMS = {"ema_length": 34, "rr": 10.0, "be_r": 3.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    cross = ((c > e) & (c.shift(1) <= e.shift(1))).to_numpy()
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    l1 = lo.shift(1).to_numpy()
    rr, br = float(p["rr"]), float(p["be_r"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_t = False
    ep = sl = tp = risk = np.nan
    for i in range(m):
        if cross[i] and not in_t:
            ep, sl = cv[i], l1[i]
            risk = ep - sl
            tp = ep + risk * rr
            le[i], in_t = True, True
        if in_t and cv[i] >= ep + risk * br:
            sl = ep
        if in_t:
            hit = False
            if lv[i] <= sl:
                hit = True
            if hv[i] >= tp:
                hit = True
            if hit:
                lx[i], in_t = True, False
    false = pd.Series(False, index=c.index)
    le_s = pd.Series(le, index=c.index)
    return le_s, pd.Series(lx, index=c.index) & ~le_s, false, false.copy()


def portfolio_kwargs(**params):
    return {}
