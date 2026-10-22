"""Closes above the upper Bollinger band (20, 2) on a green Heikin-Ashi bar with RSI 14 over 50, 6-hour bars, long only: entered from flat; a red Heikin-Ashi bar or RSI at 70 or more closes.
Port of FMZ strategy #482472 "多指标动量突破结合平滑K线交易策略-Multi-Indicator-Momentum-Breakout-with-Smoothed-Candlestick-Trading-Strategy" (Bollinger Bands + RSI + Heikin Ashi Breakout).

FMZ source id: 482472

Source
    https://www.fmz.com/strategy/482472 (PineScript v6, FMZ last modified 2025-02-18 15:38:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-205), BB 20 x 2; RSI 14, overbought 70; Heikin-Ashi open seeded (open + close) / 2
    haClose = ohlc4;  haOpen = na(haOpen[1]) ? (open + close) / 2 : (haOpen[1] + haClose[1]) / 2
    haClose > haOpen and close > upperBB and rsi > 50 -> entry Long;  haClose < haOpen or rsi >= 70 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * An entry and a close can both be true on one bar (a green bar with RSI at 70 or more): the entry
      comes first, so from flat the entry stands and the close does not act on it; when a long is held into
      the bar the entry is ignored and the close acts (as #441963): a loop. Long only. No sizing code.
      FREQ = "6h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts with Heikin-Ashi colour and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_482472_bb20_upper_break_ha_green_rsi50_ha_red_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 50],
    "bb_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_mult": 2.0, "rsi_length": 14, "rsi_overbought": 70}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_length"])
    upper = c.rolling(n).mean() + float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    hc = ((o + h + lo + c) / 4).to_numpy(dtype=float)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    ho = np.full(m, np.nan)
    for i in range(m):
        ho[i] = (ov[i] + cv[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    r = _rsi(c, int(p["rsi_length"]))
    green = pd.Series(hc > ho, index=c.index)
    red = pd.Series(hc < ho, index=c.index)
    lc = (green & (c > upper) & (r > 50)).to_numpy()
    xc = (red | (r >= float(p["rsi_overbought"]))).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xc[i]:
            lx[i], pos = True, 0                  # the close acts on the long held into the bar
        elif pos == 0 and lc[i]:
            le[i], pos = True, 1
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
