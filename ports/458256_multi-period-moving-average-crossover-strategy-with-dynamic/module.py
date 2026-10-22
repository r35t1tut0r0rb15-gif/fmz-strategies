"""SMA 10 / 200 crossings in rising volatility, 1-hour bars: the cross up with the ATR 14 over its 14-bar mean goes long with a stop just under the SMA 200 and a 7.5-point target, the mirror goes short; reversing.
Port of FMZ strategy #458256 "Multi Period Moving Average Crossover Strategy with Dynamic Volatility Filter" (SMA Crossover Strategy with Volatility Filter).

FMZ source id: 458256

Source
    https://www.fmz.com/strategy/458256 (PineScript v5, FMZ last modified 2024-07-31 12:03:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-190), SMA 10 / 200 (and a separate SMA 200, the same line); ATR 14 vs SMA 14 of it x 1.0; stop SMA 200 x 0.999 / x 1.001; target close +- 7.5 (price units)
    crossover(sma10, sma200) and atr > sma(atr, 14) -> entry Long + exit(stop = sma200 x 0.999, limit = close + 7.5)
    crossunder and atr > sma(atr, 14) -> entry Short + exit(stop = sma200 x 1.001, limit = close - 7.5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once on the signal bar. The stop is that bar's SMA 200 level, sent as a
      fraction of the fill open (the signal bar's level shifted into the fill bar); a level already at or
      through the fill open is marketable and is sent as a bar-close exit on the fill bar (one bar late).
      The 7.5 is a price amount, ported as a fraction of 42000 (0.000179 of the fill). Cross-ups and
      cross-downs alternate, so each entry opens a new position. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, SMA crossings with a volatility filter and an SMA-anchored stop.
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

NAME = "fmz_458256_sma10_200_cross_atr_filter_sma200_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [10, 20],
    "tp_frac": [0.000179, 0.01],
}
DEFAULT_PARAMS = {"short_len": 10, "long_len": 200, "tp_frac": 0.000179, "atr_len": 14, "atr_mult": 1.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _parts(bars_df, p):
    c = bars_df["close"]
    a, b = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    atr = _atr(bars_df, p["atr_len"])
    vol = atr > float(p["atr_mult"]) * atr.rolling(int(p["atr_len"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & vol
    se = (a < b) & (a.shift(1) >= b.shift(1)) & vol
    return le, se, (b * 0.999).where(le), (b * 1.001).where(se)   # stop levels on the signal bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lv_l, lv_s = _parts(bars_df, p)
    o = bars_df["open"]
    lx = (lv_l.shift(1) >= o) & ~se          # stop at or through the fill open: closed at the next open
    sx = (lv_s.shift(1) <= o) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, lv_l, lv_s = _parts(bars_df, p)
    o = bars_df["open"]
    f_l = 1 - lv_l.shift(1) / o                # the signal bar's level, read at the fill
    f_s = lv_s.shift(1) / o - 1
    sl = f_l.where(f_l.notna(), f_s)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
