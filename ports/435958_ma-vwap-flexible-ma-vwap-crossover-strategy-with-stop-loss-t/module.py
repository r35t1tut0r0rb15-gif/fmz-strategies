"""Hourly bars, long only: the SMA 9 crossing over both a rolling VWAP 14 and the SMA 21 on one bar goes long; the exit (a 1 % stop and a 2 % target from the latest buy signal's close) is only armed on a bar where the SMA 9 crosses under both lines, and then closes the long when touched.
Port of FMZ strategy #435958 "基于MA-VWAP交叉的灵活止损止盈策略Flexible-MA-VWAP-Crossover-Strategy-with-Stop-Loss-Take-Profit" (Flexible MA VWAP Crossover Strategy with SL/TP).

FMZ source id: 435958

Source
    https://www.fmz.com/strategy/435958 (PineScript v4, FMZ last modified 2023-12-20 14:06:18).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 95-136), fast SMA 9, slow SMA 21; VWAP = sma(close x volume, 14) / sma(volume, 14); SL 1 %, TP 2 %
    buy = crossover(fast, vwap) and crossover(fast, slow) -> entry Buy, stop_loss_price := close x 0.99, take_profit_price := close x 1.02
    sell = crossunder(fast, vwap) and crossunder(fast, slow) -> exit("SL/TP", "Buy", stop = stop_loss_price, limit = take_profit_price)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy.exit is sent only on a sell bar, so a long has no exit at all until the first sell
      bar; from then the stop / target (levels from the latest buy signal's close) wait until touched. The
      house stops cannot be armed later, so the port follows the levels in the signals: a level already
      passed at the arming bar closes at the next open, a later touch closes at the open after the touching
      bar (approximation; mark trailing_stop_pending). A repeated buy signal while long refreshes the levels
      for the next arming, as written. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; late-armed stop / target followed in the signals.
    2 generic: PASS, double moving-average / rolling VWAP crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the rolling VWAP sma(close x volume, 14) / sma(volume, 14); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_435958_sma9_vwap14_sma21_double_cross_armed_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [9, 5],
    "slow_length": [21, 34],
}
DEFAULT_PARAMS = {"fast_length": 9, "slow_length": 21, "vwap_length": 14, "sl": 0.01, "tp": 0.02}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    fast = c.rolling(int(p["fast_length"])).mean()
    slow = c.rolling(int(p["slow_length"])).mean()
    n = int(p["vwap_length"])
    sv = v.rolling(n).mean()
    vwap = (c * v).rolling(n).mean() / sv.where(sv != 0)
    buy = (_xo(fast, vwap) & _xo(fast, slow)).to_numpy()
    sell = (_xo(vwap, fast) & _xo(slow, fast)).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, armed, s_lvl, t_lvl, a_s, a_t, pending = 0, False, np.nan, np.nan, np.nan, np.nan, False
    for i in range(m):
        if pending:
            pending = False                                    # the entry fills at this bar's open
        elif pos == 1 and armed and (lv[i] <= a_s or hv[i] >= a_t):
            lx[i], pos, armed = True, 0, False                 # touched: out at the next open
            continue
        if buy[i]:
            s_lvl, t_lvl = cv[i] * (1 - sl), cv[i] * (1 + tp)
            if pos == 0 and i + 1 < m:
                le[i], pos, pending, armed = True, 1, True, False
        if sell[i] and pos == 1:
            armed, a_s, a_t = True, s_lvl, t_lvl
            if not pending and (cv[i] <= a_s or cv[i] >= a_t):
                lx[i], pos, armed = True, 0, False             # a level already passed fills at the next open
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
