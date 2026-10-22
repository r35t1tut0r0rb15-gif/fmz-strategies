"""Classic supertrend states, 1-hour bars: while the supertrend (ATR 10 x 3 on hl2) is up the script enters long, while down short ("enter first trade ASAP"); reversing.
Port of FMZ strategy #440798 "SuperTrend Strategy" (Supertrend Strategy).

FMZ source id: 440798

Source
    https://www.fmz.com/strategy/440798 (PineScript v4, FMZ last modified 2024-02-02 11:11:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 243-331), ATR 10 (Wilder), multiplier 3, source hl2; enter ASAP on, wait off; stop / take profit off; time-frame session empty
    up = hl2 - 3 atr, up := close[1] > up[1] ? max(up, up[1]) : up;  dn mirrored;  trend := trend == -1 and close > dn[1] ? 1 : trend == 1 and close < up[1] ? -1 : trend
    trend == 1 -> entry Long (every bar);  trend == -1 -> entry Short;  (stop / target and the session close are off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are level signals on the trend state; an entry while already in that direction does
      nothing. The empty session string makes time() non-na on every bar, so trades are always allowed.
      The bands use nz(..) starts as written. strategy.entry reverses: REVERSAL INTENDED. The cash size
      and capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, supertrend state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash size and capital are sizing.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (empty session string).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440798_classic_supertrend_state"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [10, 20],
    "multiplier": [3.0, 2.0],
}
DEFAULT_PARAMS = {"periods": 10, "multiplier": 3.0}


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


def _trend(bars_df, n, k):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, n).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tr_o = np.ones(m, dtype=np.int8)
    up_p = dn_p = np.nan
    t = 1
    for i in range(m):
        up = src[i] - k * atr[i]
        dn = src[i] + k * atr[i]
        up1 = up if np.isnan(up_p) else up_p
        dn1 = dn if np.isnan(dn_p) else dn_p
        if i > 0 and cv[i - 1] > up1:
            up = max(up, up1) if not np.isnan(up) else up
        if i > 0 and cv[i - 1] < dn1:
            dn = min(dn, dn1) if not np.isnan(dn) else dn
        if t == -1 and cv[i] > dn1:
            t = 1
        elif t == 1 and cv[i] < up1:
            t = -1
        tr_o[i] = t if not np.isnan(atr[i]) else 0
        up_p, dn_p = up, dn
    return tr_o


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = _trend(bars_df, int(p["periods"]), float(p["multiplier"]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(t == 1, index=ix), false, pd.Series(t == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
