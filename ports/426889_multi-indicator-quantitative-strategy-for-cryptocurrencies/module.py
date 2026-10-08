"""Bagheri IG: go long when the 74-bar SMA from 37 bars back sits inside the bar, the smoothed ROC
is negative, the open is under the 43-bar Donchian low from 90 bars back, bear power (low - EMA
61) has made a trough and the smoothed balance of power is rising; the mirror goes short. Each
entry carries a fixed target and stop.
Port of FMZ strategy #426889 "Multi Indicator Quantitative Strategy for Cryptocurrencies".

Source
    https://www.fmz.com/strategy/426889 (PineScript v4, FMZ last modified 2023-09-15 11:58:36).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 138-249), TP 3000 / SL 3443 ticks, ROC 185 / EMA 49,
Donchian 43 offset 90, bears-power EMA 61, BoP rma 15, SMA 74 shift 37
    ma = ema(close, 49); sroc = nz(ma[185]) == 0 ? 100 : mom == 0 ? 0 : 100 (ma - ma[185]) / ma[185]
    long  = sma74[37] inside the bar and sroc < 0 and open < lowest(43)[90]
            and bp[1] < bp and bp[1] < bp[2] and sbop[1] < sbop
    short = mirrors (sroc > 0, open > highest(43)[90], bp peak, sbop falling)
    exit(profit = 3000, loss = 3443) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * While ma[185] is na, nz() makes sroc 100, so the short-side ROC test holds (as written).
    * The balance of power is na on a zero-range bar; the rma restarts from an SMA seed after an
      na, as Pine's rma does.
    * Criterion 2: the tick bracket (tuned on ETH) becomes tp_atr x ATR(14) at the signal bar,
      the stop 3443 / 3000 of it, applied to the fill.
    * Entries do not depend on the position (same-side signals while held are refused by Pine
      and the engine alike): no mirroring. REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426889_bagheri_ig"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "4min"  # backtest header period: 4m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)
SL_RATIO = 3443 / 3000  # the source's stop / target

GRID = {
    "tp_atr": [2.0, 5.0, 10.0],
}
DEFAULT_PARAMS = {"tp_atr": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _rma_pine(x, n):
    """Pine rma: SMA seed whenever the previous value is na, then the Wilder recursion."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        prev = out[i - 1] if i > 0 else np.nan
        if np.isnan(prev):
            w = v[max(0, i - n + 1):i + 1]
            out[i] = w.mean() if len(w) == n and not np.isnan(w).any() else np.nan
        else:
            out[i] = (prev * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _signals(bars_df):
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ma = c.ewm(span=49, adjust=False).mean()
    ma185 = ma.shift(185)
    sroc = pd.Series(np.where(ma185.fillna(0.0) == 0, 100.0,
                              np.where((ma - ma185) == 0, 0.0, 100 * (ma - ma185) / ma185)), index=c.index)
    dc_up, dc_lw = h.rolling(43).max().shift(90), l.rolling(43).min().shift(90)
    bp = l - c.ewm(span=61, adjust=False).mean()
    sbop = _rma_pine((c - o) / (h - l), 15)
    sma_sh = c.rolling(74).mean().shift(37)
    inside = (sma_sh > l) & (sma_sh < h)
    bp1 = bp.shift(1)
    le = inside & (sroc < 0) & (o < dc_lw) & (bp1 < bp) & (bp1 < bp.shift(2)) & (sbop.shift(1) < sbop)
    se = inside & (sroc > 0) & (o > dc_up) & (bp1 > bp) & (bp1 > bp.shift(2)) & (sbop.shift(1) > sbop)
    return le, se


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    le, se = _signals(bars_df)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df)
    f = (p["tp_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(le | se)
    return {"tp_stop": f.shift(1), "sl_stop": (SL_RATIO * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
