"""Follow line (always in): a close above the upper Bollinger band (21, 1 sd) raises a trend line to
low - ATR(5), a close below the lower band lowers it to high + ATR(5); the line's turn from
falling to rising goes long, from rising to falling goes short.
Port of FMZ strategy #426778 "Range Breakout Momentum Tracking Strategy".

Source
    https://www.fmz.com/strategy/426778 (PineScript v5, FMZ last modified 2023-09-14 15:10:46).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 239-292), BB 21 x 1, ATR filter on, ATR 5
    BBSignal = close > upper ? 1 : close < lower ? -1 : 0
    1:  TL = low - atr(5), kept at TL[1] if lower;  -1: TL = high + atr(5), kept at TL[1] if higher
    0:  TL = TL[1]
    iTrend = TL > TL[1] ? 1 : TL < TL[1] ? -1 : iTrend[1]
    iTrend[1] == -1 and iTrend == 1 -> entry long;  iTrend[1] == 1 and iTrend == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.atr(5) is called inside the two if-blocks, so each call site's RMA advances only on the
      bars where its block runs (Pine's per-call-site history): the ATR used above the band is an
      RMA (SMA-seeded) over the true ranges of the bars that closed above the band, and likewise
      below. FMZ's runtime may differ (decision owed).
    * The range filter and Hull suite only plot. stdev is Pine's population deviation.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426778_follow_line"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_period": [14, 21],
    "bb_dev": [1.0, 1.5],
    "atr_period": [5, 10],
}
DEFAULT_PARAMS = {"bb_period": 21, "bb_dev": 1.0, "atr_period": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _site_atr(tr, run, n):
    """RMA (SMA seed) of tr over only the bars where run is true; NaN elsewhere."""
    out = np.full(len(tr), np.nan)
    hist, prev = [], np.nan
    for i in range(len(tr)):
        if not run[i]:
            continue
        hist.append(tr[i])
        if np.isnan(prev):
            window = hist[-n:]
            prev = np.mean(window) if len(window) == n and not np.isnan(window).any() else np.nan
        else:
            prev = (prev * (n - 1) + tr[i]) / n
        out[i] = prev
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_period"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    sig = np.where(c > basis + sd * p["bb_dev"], 1, np.where(c < basis - sd * p["bb_dev"], -1, 0))
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1).to_numpy()  # tr(true)
    k = int(p["atr_period"])
    atr_up, atr_dn = _site_atr(tr, sig == 1, k), _site_atr(tr, sig == -1, k)
    hv, lv = h.to_numpy(dtype=float), l.to_numpy(dtype=float)
    m = len(sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tl_p = it_p = np.nan
    for i in range(m):
        if sig[i] == 1:
            tl = lv[i] - atr_up[i]
            if tl < tl_p:
                tl = tl_p
        elif sig[i] == -1:
            tl = hv[i] + atr_dn[i]
            if tl > tl_p:
                tl = tl_p
        else:
            tl = tl_p
        it = 1.0 if tl > tl_p else (-1.0 if tl < tl_p else it_p)
        le[i] = it_p == -1 and it == 1
        se[i] = it_p == 1 and it == -1
        tl_p, it_p = tl, it
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
