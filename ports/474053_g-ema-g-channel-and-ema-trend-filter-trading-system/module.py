"""G-Channel state against the EMA 200, hourly bars: while the last channel signal was a cross up through the lower line and the close is under the EMA 200 it goes long; while it was a cross down through the upper line (or none yet) and the close is over the EMA it goes short; reversing.
Port of FMZ strategy #474053 "G通道与EMA趋势过滤交易系统-G-Channel-and-EMA-Trend-Filter-Trading-System" (G-Channel with EMA Strategy).

FMZ source id: 474053

Source
    https://www.fmz.com/strategy/474053 (PineScript v5, FMZ last modified 2024-12-05 16:27:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-131), G-Channel length 100; EMA 200
    a := max(src, nz(a[1])) - (nz(a[1]) - nz(b[1])) / 100;  b := min(src, nz(b[1])) + (nz(a[1]) - nz(b[1])) / 100;  bullish = barssince(crossunder(close, a)) <= barssince(crossover(close, b));  bullish and close < ema200 -> entry Buy;  not bullish and close > ema200 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel is a recursion (a loop) from nz seeds of 0, as written (the lower line starts at 0
      and climbs). barssince is na before the first cross, and a comparison with na is false, so
      "not bullish" holds until both crosses have happened. Entries repeat while the tests hold
      (ignored while held). There is no exit: positions end at the opposite entry. REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, G-Channel state with a counter-trend EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_474053_g_channel100_state_ema200_counter_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "ema_len": [200, 100],
}
DEFAULT_PARAMS = {"length": 100, "ema_len": 200}


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


def _barssince(cond):
    k = cond.to_numpy()
    out = np.full(len(k), np.nan)
    last = -1
    for i in range(len(k)):
        if k[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    n = float(p["length"])
    av, bv = np.zeros(len(cv)), np.zeros(len(cv))
    a1 = b1 = 0.0
    for i in range(len(cv)):
        a = max(cv[i], a1) - (a1 - b1) / n
        b = min(cv[i], b1) + (a1 - b1) / n
        av[i], bv[i] = a, b
        a1, b1 = a, b
    ix = bars_df.index
    a, b = pd.Series(av, index=ix), pd.Series(bv, index=ix)
    up = (c > b) & (c.shift(1) <= b.shift(1))
    dn = (c < a) & (c.shift(1) >= a.shift(1))
    bull = pd.Series(_barssince(dn) <= _barssince(up), index=ix)   # na compares false
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = bull & (c < e)
    se = ~bull & (c > e)
    false = pd.Series(False, index=ix)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
