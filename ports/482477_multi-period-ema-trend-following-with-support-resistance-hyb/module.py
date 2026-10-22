"""Breakouts of the previous 9-bar high / low or an EMA 20 / 50 trend state wider than one ATR 14, hourly bars: either long condition goes long from flat or short, either short condition goes short from flat or long; a stop 10 ATR from the latest close is re-sent every bar (pending); reversing.
Port of FMZ strategy #482477 "Multi Period EMA Trend Following with Support Resistance Hybrid Trading System" (Multi-Strategy Trader v1).

FMZ source id: 482477

Source
    https://www.fmz.com/strategy/482477 (PineScript v6, FMZ last modified 2025-02-18 15:52:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-159), support / resistance lookback 9; ATR 14; stop 10 ATR; EMA 20 / 50
    close > highest(high, 9)[1] or (|ema20 - ema50| > atr and ema20 > ema50 and close > ema20) -> entry Long if position <= 0;  mirror -> entry Short if position >= 0
    position > 0 -> exit Long (stop = close - 10 atr);  position < 0 -> exit Short (stop = close + 10 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * When both conditions are true from flat, both entries are sent and the later (short) wins (as
      #437773); held long, only the short is sent, and held short only the long: a loop. The stop is re-sent
      on every bar from that bar's close: stops() cannot express a level re-set every bar, so it is
      described here and kept pending (as #438034, mark trailing_stop_pending); positions end at the
      opposite entry until then. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar ATR stop described (pending).
    2 generic: PASS, range breakouts or EMA trend state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_482477_hh9_break_or_ema20_50_atr_trend_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sup_res_lookback": [9, 20],
    "atr_period": [14, 28],
}
DEFAULT_PARAMS = {"sup_res_lookback": 9, "atr_period": 14}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["sup_res_lookback"])
    hh, ll = h.rolling(n).max().shift(1), lo.rolling(n).min().shift(1)
    atr = _atr(bars_df, int(p["atr_period"]))
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    trend = (e20 - e50).abs() > atr
    ls = ((c > hh) | (trend & (e20 > e50) & (c > e20))).to_numpy()
    ss = ((c < ll) | (trend & (e20 < e50) & (c < e20))).to_numpy()
    m = len(ls)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        go_l = ls[i] and pos <= 0
        go_s = ss[i] and pos >= 0
        if go_s:
            se[i], pos = True, -1                 # the later call wins a bar with both entries
        elif go_l:
            le[i], pos = True, 1
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
