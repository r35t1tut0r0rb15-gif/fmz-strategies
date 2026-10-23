"""An adaptive Hull MA whose period shrinks 3.141 % a bar toward 172 while ATR 14 is over ATR 46 and grows toward 233 otherwise, 15-minute bars: its slope angle reaching 17 degrees in a high-volatility state goes long, reaching -17 degrees goes short; reversing.
Port of FMZ strategy #365902 "72s Adaptive Hull Moving Average" (72s: Adaptive Hull Moving Average+).

FMZ source id: 365902

Source
    https://www.fmz.com/strategy/365902 (PineScript v4, FMZ last modified 2022-05-26 17:17:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 99-250), charger Volatility (atr(14) > atr(46)); period 172-233, adapt 3.141 %; flat 17; minor HMA 89-121 (exits / plots only)
    dynamicLength := plugged ? max(172, dl x (1 - 0.03141)) : min(233, dl x (1 + 0.03141));  hma = wma(2 wma(close, int(dl) / 2) - wma(close, int(dl)), floor(sqrt(int(dl))))
    slope = angle of (hma[2] - hma) / close x 25 / (highest(34) - lowest(34)) x lowest(34);  buy = slope >= 17 and plugged, first bar;  sell = slope <= -17 and plugged, first bar -> entries

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "charger" takes its default, Volatility, so the RSI-of-volume branch is not selected and volume
      is not used. The HMA's period is a series (one per bar), so each WMA uses that bar's period over the
      history, as written; length / 2 is taken as an integer. The fast-exit and warning signs are alerts
      only. A study() script sending strategy orders on FMZ. REVERSAL INTENDED. No sizing code. The source
      carries the Mozilla Public License 2.0 notice. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive-period Hull MA slope turns in high volatility.
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

NAME = "fmz_365902_adaptive_hma172_233_slope17_volatility_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "flat": [17, 10],
    "min_length": [172, 100],
}
DEFAULT_PARAMS = {"flat": 17, "min_length": 172, "max_length": 233, "adapt_pct": 0.03141}


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


def _wma_at(v, i, n):
    """WMA of v over the n bars ending at i (newest weighted n); NaN if not enough history or a NaN."""
    if n < 1 or i + 1 < n:
        return np.nan
    w = np.arange(1, n + 1, dtype=float)
    seg = v[i - n + 1:i + 1]
    return float(seg @ w / w.sum())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    plugged = (_rma(tr, 14) > _rma(tr, 46)).to_numpy()
    lo_len, hi_len, ap = float(p["min_length"]), float(p["max_length"]), float(p["adapt_pct"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    inner = np.full(m, np.nan)
    hma = np.full(m, np.nan)
    dl = (lo_len + hi_len) / 2
    for i in range(m):
        dl = max(lo_len, dl * (1 - ap)) if plugged[i] else min(hi_len, dl * (1 + ap))
        n = int(dl)
        inner[i] = 2 * _wma_at(cv, i, n // 2) - _wma_at(cv, i, n)
        hma[i] = _wma_at(inner, i, int(np.floor(np.sqrt(n))))
    hm = pd.Series(hma, index=c.index)
    hh, ll = h.rolling(34).max(), lo.rolling(34).min()
    slope_range = 25 / (hh - ll) * ll
    dt = (hm.shift(2) - hm) / c * slope_range
    ang = np.round(180 * np.arccos(1 / np.sqrt(1 + dt * dt)) / np.pi)
    slope = (-ang).where(dt > 0, ang)
    flat = float(p["flat"])
    plug = pd.Series(plugged, index=c.index)
    up_sig = (slope >= flat) & plug
    dn_sig = (slope <= -flat) & plug
    buy = up_sig & ~up_sig.shift(1, fill_value=False)
    sell = dn_sig & ~dn_sig.shift(1, fill_value=False)
    false = pd.Series(False, index=c.index)
    return buy, false, sell & ~buy, false.copy()


def portfolio_kwargs(**params):
    return {}
