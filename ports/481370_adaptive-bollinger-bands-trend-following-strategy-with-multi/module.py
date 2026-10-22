"""Bollinger 14 / 1.5 reversal candles with an EMA 80 slope filter, 2-hour bars: a red candle after a green close above the upper band, with the EMA falling, goes short; a green candle after a close below the lower band, with the EMA rising, goes long; a close 300 points against the entry price, or the 10th bar in a position, closes; reversing. The basis-armed trailing stop is not ported (pending).
Port of FMZ strategy #481370 "Adaptive-Bollinger-Bands-Trend-Following-Strategy-with-Multi-Level-Risk-Management-自适应布林带趋势跟踪策略与多层风险管理系统" (AI Bollinger Bands Strategy with SL, TP, and Bars Till Close).

FMZ source id: 481370

Source
    https://www.fmz.com/strategy/481370 (PineScript v5, FMZ last modified 2025-02-10 15:14:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-187), BB 14 / 1.5; EMA 80 slope; trailing stop on; SL 300 $ on; TP off; bars till close 10
    close[1] > upper[1] and close[1] > open[1] and close < open and ema < ema[1] -> entry Sell;  close[1] < lower[1] and close > open and ema > ema[1] -> entry Buy
    long and close >= basis -> exit(stop = low) (short mirror);  close <= avg - 300 -> close Buy (short mirror);  bars in position >= 10 -> close Buy and Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing stop is re-sent from the current bar's low (high) on bars past the basis, so its level
      moves; it is kept pending (as #438034, mark trailing_stop_pending). The 300-$ stop is a bar-close test
      on the entry price (a price amount, ported as a fraction of 42000 of it: 7.14e-03), and the bar count
      runs from the first bar in a position and does not restart on a reversal, as written; a loop follows
      both. On a bar with both entries the later buy call wins (#437773); a close acts only on the held
      position and leaves a same-bar reversal standing. REVERSAL INTENDED. No sizing code. FREQ = "2h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving trailing stop described (pending).
    2 generic: PASS, band reversal candles with an EMA slope filter, point stop and time exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 300 / 1000 $ inputs stored (TP off).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_481370_bb14_reversal_candle_ema80_slope_point_stop_bars10_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars_till_close": [10, 5],
    "sl_frac": [7.14286e-03, 0.02],
}
DEFAULT_PARAMS = {"bars_till_close": 10, "sl_frac": 7.14286e-03, "bb_length": 14, "bb_std": 1.5, "ema_length": 80}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_std"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    sc = ((c.shift(1) > up.shift(1)) & (c.shift(1) > o.shift(1)) & (c < o) & (e < e.shift(1))).to_numpy()
    lc = ((c.shift(1) < dn.shift(1)) & (c > o) & (e > e.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    f = float(p["sl_frac"])
    limit = int(p["bars_till_close"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, avg, bars_in = 0, 0, np.nan, -1
    for i in range(m):
        if nxt != pos:
            avg = ov[i] if nxt != 0 else np.nan
        pos = nxt
        want = 0
        if sc[i] and pos != -1:
            want = -1
        if lc[i] and pos != 1:
            want = 1
        if want == 1:
            le[i], nxt = True, 1
        elif want == -1:
            se[i], nxt = True, -1
        bars_in = (0 if bars_in < 0 else bars_in + 1) if pos != 0 else -1
        stop_hit = (pos == 1 and cv[i] <= avg * (1 - f)) or (pos == -1 and cv[i] >= avg * (1 + f))
        timed = bars_in >= limit
        if pos == 1 and not se[i] and (stop_hit or timed):
            lx[i], nxt = True, 0
        elif pos == -1 and not le[i] and (stop_hit or timed):
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
