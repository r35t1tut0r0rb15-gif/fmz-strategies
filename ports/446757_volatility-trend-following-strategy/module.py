"""Bollinger-band (20, 1) signals ratcheting an ATR trend line, 4-hour bars, long only: closes above the upper band raise the line to low - ATR(14), closes under the lower band lower it to high + ATR; the
line turning up goes long, turning down closes.
Port of FMZ strategy #446757 "Volatility Trend Following Strategy" (Volatility Trend Strategy (Julien_Eche)).

FMZ source id: 446757

Source
    https://www.fmz.com/strategy/446757 (PineScript v5, FMZ last modified 2024-04-01 11:07:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-190), BB 20 / 1; ATR 14; filter on; 20 % of equity
    Signal = close > upper ? 1 : close < lower ? -1 : 0;  Signal 1: Line = max(low - atr, Line[1]);  Signal -1: Line = min(high + atr, Line[1]);  0: Line = Line[1]
    Trend = Line rising ? 1 : Line falling ? -1 : Trend[1];  Trend flips up -> entry Buy;  flips down -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line and trend follow the script's history: a comparison with the previous line is false
      while it is na, so the first band signal sets the line. Long only. The 20 % of equity size is
      sizing. Pine's stdev is the population deviation. FREQ = "4h" from the backtest header (UTC-aligned
      4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band-driven ATR trend-line flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 20 % of equity size stored.
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

NAME = "fmz_446757_band_atr_trend_line_flip_long"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "dev": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "dev": 1.0, "atr_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    sma, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up_b = (sma + sd * float(p["dev"])).to_numpy()
    lo_b = (sma - sd * float(p["dev"])).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    trend = np.full(m, np.nan)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            prev = line[i - 1] if i > 0 else np.nan
            sig = 1 if cv[i] > up_b[i] else (-1 if cv[i] < lo_b[i] else 0)
            if sig == 1:
                v = lv[i] - atr[i]
                line[i] = prev if v < prev else v
            elif sig == -1:
                v = hv[i] + atr[i]
                line[i] = prev if v > prev else v
            else:
                line[i] = prev
            t = trend[i - 1] if i > 0 else np.nan
            if line[i] > prev:
                t = 1.0
            if line[i] < prev:
                t = -1.0
            trend[i] = t
    t1 = np.concatenate(([np.nan], trend[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((t1 == -1) & (trend == 1), index=ix), pd.Series((t1 == 1) & (trend == -1), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
