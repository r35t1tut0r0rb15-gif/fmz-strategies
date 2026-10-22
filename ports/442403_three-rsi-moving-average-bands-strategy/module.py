"""Colour agreement of SMA ribbons on RSI 75 and RSI 100 (of ohlc4), 1-hour bars: all ribbon colours lime (or all green) on either RSI goes long; all maroon on either then enters short (the exit order is
a short entry, as written); reversing.
Port of FMZ strategy #442403 "Three RSI Moving Average Bands Strategy" (3 RSI MA movement crypto strategy).

FMZ source id: 442403

Source
    https://www.fmz.com/strategy/442403 (PineScript v4, FMZ last modified 2024-02-21 16:18:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-271), source ohlc4; RSI 50 / 75 / 100; SMA ribbons 5 / 30 / 50 / 70 / 90 / 100 of each RSI; dates 2019-2021 (time_cond true); pyramiding 1; 100 % of equity, capital 100, commission 0.03
    colour(ma, ref) = change(ma) >= 0 and x > ref ? lime : change(ma) < 0 and x > ref ? red : change(ma) <= 0 and x < ref ? maroon : change(ma) >= 0 and x < ref ? green : gray  (x = ma30 of RSI 50 in block 0, ma05 of RSI 50 in blocks 1 and 2, as written)
    long = long1 or long2 (block 0 unused);  exit = exit1 or exit2;  long and not longOpened -> entry "long" (1);  longOpened[1] and exit -> entry "short" (0 = short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The colour helpers of the RSI 75 and RSI 100 blocks compare the RSI 50 block's 5-bar SMA with
      their reference, and two terms use the RSI 75 block's SMAs (ma701, ma901) and the RSI 50 SMA 100, as
      written. The exit is strategy.entry("short", 0): direction 0 is short, so the exit reverses into a
      short, which the next long signal reverses again. REVERSAL INTENDED. The 100 % of equity size,
      capital and commission are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI ribbon colour agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_442403_three_rsi_ribbon_colour_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_norm": [75, 50],
    "rsi_slow": [100, 150],
}
DEFAULT_PARAMS = {"rsi_norm": 75, "rsi_slow": 100, "rsi_fast": 50}

LIME, RED, MAROON, GREEN, GRAY = 1, 2, 3, 4, 0


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _colour(ma, x, ref):
    ch = ma.diff()
    out = np.full(len(ma), GRAY)
    a, b, cc, d = ((ch >= 0) & (x > ref)).to_numpy(), ((ch < 0) & (x > ref)).to_numpy(), \
        ((ch <= 0) & (x < ref)).to_numpy(), ((ch >= 0) & (x < ref)).to_numpy()
    out = np.where(a, LIME, np.where(b, RED, np.where(cc, MAROON, np.where(d, GREEN, GRAY))))
    return out


def _ribbon(r):
    return {n: r.rolling(n).mean() for n in (5, 30, 50, 70, 90, 100)}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    src = (o + h + lo + c) / 4
    r0 = _ribbon(_rsi(src, int(p["rsi_fast"])))
    r1 = _ribbon(_rsi(src, int(p["rsi_norm"])))
    r2 = _ribbon(_rsi(src, int(p["rsi_slow"])))
    x = r0[5]                                   # ma05 of the RSI 50 block, used by both helpers
    lead1 = _colour(r1[5], r1[5], r1[100])
    lead2 = _colour(r2[5], r2[5], r2[100])

    def col1(ma, ref):
        return _colour(ma, x, ref)

    long1 = ((lead1 == LIME) & (col1(r1[30], r1[100]) == LIME) & (col1(r1[50], r1[100]) == LIME)
             & (col1(r1[70], r1[100]) == LIME) & (col1(r1[90], r1[100]) == LIME)) \
        | ((lead1 == GREEN) & (col1(r1[30], r1[100]) == GREEN) & (col1(r1[50], r1[100]) == GREEN)
           & (col1(r1[70], r1[100]) == GREEN) & (col1(r1[90], r0[100]) == GREEN))
    exit1 = (lead1 == MAROON) & (col1(r1[30], r1[100]) == MAROON) & (col1(r1[50], r1[100]) == MAROON) \
        & (col1(r1[70], r1[100]) == MAROON) & (col1(r1[90], r1[100]) == MAROON)
    long2 = ((lead2 == LIME) & (col1(r2[30], r2[100]) == LIME) & (col1(r2[50], r2[100]) == LIME)
             & (col1(r2[70], r2[100]) == LIME) & (col1(r2[90], r2[100]) == LIME)) \
        | ((lead2 == GREEN) & (col1(r2[30], r2[100]) == GREEN) & (col1(r2[50], r2[100]) == GREEN)
           & (col1(r1[70], r2[100]) == GREEN) & (col1(r1[90], r2[100]) == GREEN))
    exit2 = (lead2 == MAROON) & (col1(r2[30], r2[100]) == MAROON) & (col1(r2[50], r2[100]) == MAROON) \
        & (col1(r2[70], r2[100]) == MAROON) & (col1(r2[90], r2[100]) == MAROON)
    lg, ex = long1 | long2, exit1 | exit2
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    opened = False
    for i in range(m):
        go = lg[i] and not opened
        if go:
            opened = True
        out_ = (opened if not go else False) and ex[i]
        if not go and opened and ex[i]:
            opened = False
        le[i] = go
        se[i] = out_ and not go
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
