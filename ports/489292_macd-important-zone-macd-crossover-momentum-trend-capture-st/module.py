"""MACD crosses near the zero line, hourly bars: a MACD 12 / 26 / 9 cross up with the MACD line within a band around
zero goes long; a cross down in the band goes short; any cross down closes a long and any cross up closes a short.
Port of FMZ strategy #489292 "重要区间MACD交叉动量趋势捕捉策略-Important-Zone-MACD-Crossover-Momentum-Trend-Capture-Strategy" (MACD Crossover Strategy).

FMZ source id: 489292

Source
    https://www.fmz.com/strategy/489292 (PineScript v5, FMZ last modified 2025-04-03 10:59:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 183-220), MACD 12 / 26 / 9, zone -0.5 .. 0.5
    zone = -0.5 <= macd <= 0.5;  cross up and zone -> entry long;  cross down and zone -> entry short
    cross down -> close long;  cross up -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the zone +-0.5 is in price units; it becomes +-zone_atr x Wilder ATR(14): on the author's hourly
      BNB_USDT (about 600, hourly ATR about 4) 0.5 is about 0.125 ATR (judgement before any backtest).
    * The closes are written after the entries: they act on the position held at the bar's start (as #430850); a
      cross outside the zone only closes. Entries reverse (REVERSAL INTENDED).
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit zone -> an ATR band.
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

NAME = "fmz_489292_macd_cross_zero_zone"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "zone_atr": [0.125, 0.5],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "zone_atr": 0.125, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    band = p["zone_atr"] * _atr(bars_df, int(p["atr_len"]))
    zone = ((macd >= -band) & (macd <= band)).to_numpy()
    up = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    dn = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if up[i] and zone[i]:
            pos = 1
        if dn[i] and zone[i]:
            pos = -1
        if dn[i] and start == 1 and pos == 1:
            pos = 0
        if up[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
