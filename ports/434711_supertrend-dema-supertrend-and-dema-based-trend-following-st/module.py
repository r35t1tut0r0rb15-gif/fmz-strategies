"""Supertrend 10 / 3 flips on the side of an EMA 200, 1-hour bars: a flip up with the close above the EMA goes long, a flip
down with the close below it goes short; a position is closed at the next flip or when the close crosses to the other
side of the EMA.
Port of FMZ strategy #434711 "基于SuperTrend和DEMA的趋势跟踪策略SuperTrend-and-DEMA-Based-Trend-Following-Strategy" (Krish's Supertrend Strategy).

FMZ source id: 434711

Source
    https://www.fmz.com/strategy/434711 (PineScript v5, FMZ last modified 2023-12-08 16:42:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 161-211), Supertrend ATR 10 (Wilder) x 3 on hl2; "DEMA" = EMA 200
    buySignal = trend flips to 1;  buySignal and close > ema200 -> entry long;  sellSignal and close < ema200 -> entry short
    change(trend) or close < ema200 -> close long;  change(trend) or close > ema200 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Supertrend is this script's (KivancOzbilgic form). The closes act on the position held on
      the bar; an entry on the same bar wins. strategy.entry reverses: REVERSAL INTENDED. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands and an average side.
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

NAME = "fmz_434711_supertrend_ema200_flips"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "ema_len": [200, 100],
}
DEFAULT_PARAMS = {"atr_len": 10, "mult": 3.0, "ema_len": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _trend(bars_df, n, mlt):
    """KivancOzbilgic Supertrend trend (1 up, -1 down) on hl2 with a Wilder ATR."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn = src - mlt * atr, src + mlt * atr
    trend = np.ones(m, dtype=np.int8)
    for i in range(m):
        up1 = up[i - 1] if i > 0 and not np.isnan(up[i - 1]) else up[i]
        dn1 = dn[i - 1] if i > 0 and not np.isnan(dn[i - 1]) else dn[i]
        cp = cv[i - 1] if i > 0 else np.nan
        if cp > up1:
            up[i] = max(up[i], up1)
        if cp < dn1:
            dn[i] = min(dn[i], dn1)
        t1 = trend[i - 1] if i > 0 else 1
        trend[i] = 1 if (t1 == -1 and cv[i] > dn1) else (-1 if (t1 == 1 and cv[i] < up1) else t1)
    return trend


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    tr_ = _trend(bars_df, int(p["atr_len"]), float(p["mult"]))
    t1 = np.concatenate(([tr_[0]], tr_[:-1]))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    chg = tr_ != t1
    lc = (tr_ == 1) & (t1 == -1) & (cv > ema)
    sc = (tr_ == -1) & (t1 == 1) & (cv < ema)
    xl, xs = chg | (cv < ema), chg | (cv > ema)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if lc[i]:
            new = 1
        if sc[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
