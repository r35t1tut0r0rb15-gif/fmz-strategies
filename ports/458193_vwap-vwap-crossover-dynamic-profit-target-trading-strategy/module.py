"""Hourly bars: the close crossing over a 14-bar rolling VWAP of the typical price goes long, crossing under goes short; a long closes once a close reaches 3 % above its fill price, a short once a close reaches 3 % below; reversing.
Port of FMZ strategy #458193 "VWAP交叉动态利润目标交易策略-VWAP-Crossover-Dynamic-Profit-Target-Trading-Strategy" (VWAP Crossover Strategy with Profit Targets).

FMZ source id: 458193

Source
    https://www.fmz.com/strategy/458193 (PineScript v4, FMZ last modified 2024-07-30 17:01:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 172-215), VWAP period 14 (rolling sums of hlc3 x volume and volume); target 3 % from position_avg_price
    vwapValue = sum(hlc3 * volume, 14) / sum(volume, 14);  crossover(close, vwapValue) -> entry Long;  crossunder -> entry Short
    position_size > 0 and close >= position_avg_price * 1.03 -> close Long;  position_size < 0 and close <= position_avg_price * 0.97 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The targets are close tests against the fill price (the open of the fill bar), sent at the close
      and filled at the next open, followed in the signals. They act only on a position the bar's
      entries leave unchanged; an opposite entry reverses. After a target close the strategy waits for the
      next crossing. Pine v4. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based targets from the fill.
    2 generic: PASS, rolling-VWAP crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458193_rolling_vwap14_cross_3pct_close_target_1h_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [14, 28],
    "target": [0.03, 0.05],
}
DEFAULT_PARAMS = {"period": 14, "target": 0.03}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["period"])
    vw = ((h + lo + c) / 3 * v).rolling(n).sum() / v.rolling(n).sum()
    buy = ((c > vw) & (c.shift(1) <= vw.shift(1))).to_numpy()
    sell = ((c < vw) & (c.shift(1) >= vw.shift(1))).to_numpy()
    on, cn = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    t = float(p["target"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, cur, fp = 0, 0, np.nan
    for i in range(m):
        if tgt != cur:                    # the previous bar's order fills at this open
            cur = tgt
            fp = on[i] if cur != 0 else np.nan
        new = cur
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == cur:
            if cur == 1 and cn[i] >= fp * (1 + t):
                new = 0
            elif cur == -1 and cn[i] <= fp * (1 - t):
                new = 0
        if new != cur and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif cur == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
