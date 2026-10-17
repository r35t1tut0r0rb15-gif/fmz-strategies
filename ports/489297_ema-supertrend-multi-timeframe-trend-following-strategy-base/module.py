"""SuperTrend (10, 3) flips filtered by EMA 9 vs EMA 15, 2-minute bars: a SuperTrend flip up with EMA 9 above EMA 15
goes long; a flip down with EMA 9 below EMA 15 goes short (closing the long); any bar with the SuperTrend up closes a
short.
Port of FMZ strategy #489297 "基于EMA和Supertrend结合的多时间框架趋势跟踪策略-Multi-timeframe-Trend-Following-Strategy-Based-on-EMA-and-Supertrend-Combination" (Supertrend Strategy for Renko).

FMZ source id: 489297

Source
    https://www.fmz.com/strategy/489297 (PineScript v6, FMZ last modified 2025-04-03 11:23:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 179-225), EMA 9 / 15 (the "slow" input is also 15), SuperTrend ATR 10 x 3 on hl2
    up / dn = the SuperTrend bands (ratcheted on close[1]); trend flips up when close > dn1, down when close < up1
    buy = trend flips to 1 and ema9 > ema15 -> entry long
    sell = trend flips to -1 and ema9 < ema15 -> close long, entry short;  trend == 1 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend as written (ta.atr, i.e. Wilder, since changeATR is true; nz(up[1], up) seeds the bands).
    * The short close runs after the entries on every up-trend bar: it acts on the position held at the bar's start
      (as #430850), so a short is closed on the first up-trend bar even without a long signal. A long has no exit other
      than the reversing short. REVERSAL INTENDED.
    * The "Renko" in the title is a label; FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands and EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_489297_supertrend_flip_ema_filter"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [3.0, 2.0],
    "slow": [15, 30],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 15, "atr_period": 10, "multiplier": 3.0}


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


def _supertrend(bars_df, n, mult):
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    trend = np.ones(m, dtype=np.int8)
    up_prev = dn_prev = np.nan
    t = 1
    for i in range(m):
        up, dn = src[i] - mult * atr[i], src[i] + mult * atr[i]
        up1 = up if np.isnan(up_prev) else up_prev          # nz(up[1], up)
        dn1 = dn if np.isnan(dn_prev) else dn_prev
        if i > 0 and c[i - 1] > up1:
            up = max(up, up1)
        if i > 0 and c[i - 1] < dn1:
            dn = min(dn, dn1)
        if t == -1 and c[i] > dn1:
            t = 1
        elif t == 1 and c[i] < up1:
            t = -1
        trend[i] = t
        up_prev, dn_prev = up, dn
    return trend


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean().to_numpy()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean().to_numpy()
    tr = _supertrend(bars_df, int(p["atr_period"]), float(p["multiplier"]))
    prev_tr = np.concatenate(([tr[0]], tr[:-1]))
    buy = (tr == 1) & (prev_tr == -1) & (ef > es)
    sell = (tr == -1) & (prev_tr == 1) & (ef < es)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if sell[i]:
            pos = -1
        if tr[i] == 1 and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
