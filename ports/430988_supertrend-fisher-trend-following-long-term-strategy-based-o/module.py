"""SuperTrend turn with a Fisher low, 1-minute bars, long only: a SuperTrend (ATR 10 x 2) turning up on a bar whose Fisher
transform (10) is under -2.5 and rising goes long; a close at or below the signal close - 2 ATR, or at or above the
signal close + 2 ATR, closes the long.
Port of FMZ strategy #430988 "基于SuperTrend和Fisher变换的趋势跟随长线策略Trend-Following-Long-Term-Strategy-Based-on-SuperTrend-and-Fisher-Transform" (Supertrend and Fisher_LONG).

FMZ source id: 430988

Source
    https://www.fmz.com/strategy/430988 (PineScript v5, FMZ last modified 2023-11-03 15:42:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 157-231), Fisher 10, SuperTrend hl2 ATR 10 x 2 (Wilder ATR), risk $10
    buy_signal = fish1 < -2.5 and fish1 > fish1[1];  buySignal = trend turns 1 and buy_signal (same bar)
    buySignal: entryPrice = close; stopLoss = close - 2 ATR; takeProfit = close + 2 ATR -> entry long (qty from risk)
    close <= stopLoss -> close;  else close >= takeProfit -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * durum is reset to 0 on every bar, so the Fisher condition must hold on the SuperTrend turn bar
      itself, as written. Fisher as written (value clipped at +-0.999, nz recursions).
    * The levels are checked on bar closes with strategy.close (market exits at the next open): exit
      signals from the signal close, tested from the bar after the signal. takeProfit2 / 3 are
      plot-only. The risk-based contracts are sizing. Long only; Opposite entries cannot occur.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, Fisher transform, SuperTrend and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-amount contract formula stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430988 (2 members, best partner #443139, Jaccard 0.696); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430988_supertrend_fisher_long"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [2.0, 3.0],
    "fisher_level": [-2.5, -1.5],
}
DEFAULT_PARAMS = {"fisher_len": 10, "atr_len": 10, "mult": 2.0, "fisher_level": -2.5}


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
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    fl = int(p["fisher_len"])
    hh = pd.Series(hl2).rolling(fl).max().to_numpy()
    ll = pd.Series(hl2).rolling(fl).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    fish = np.full(m, np.nan)
    val_p, fish_p = 0.0, 0.0
    for i in range(m):
        v = 0.66 * ((hl2[i] - ll[i]) / (hh[i] - ll[i]) - 0.5) + 0.67 * val_p
        v = 0.999 if v > 0.99 else (-0.999 if v < -0.99 else v)
        f = 0.5 * np.log((1 + v) / (1 - v)) + 0.5 * fish_p
        fish[i] = f
        val_p = 0.0 if np.isnan(v) else v
        fish_p = 0.0 if np.isnan(f) else f
    fish1 = np.concatenate(([np.nan], fish[:-1]))
    buy_f = (fish < p["fisher_level"]) & (fish > fish1)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_len"]))
    k = float(p["mult"])
    trend = np.ones(m)
    up_p = dn_p = np.nan
    t = 1.0
    for i in range(m):
        up, dn = hl2[i] - k * atr[i], hl2[i] + k * atr[i]
        up1 = up if np.isnan(up_p) else up_p
        dn1 = dn if np.isnan(dn_p) else dn_p
        if i and cv[i - 1] > up1:
            up = max(up, up1)
        if i and cv[i - 1] < dn1:
            dn = min(dn, dn1)
        t = 1.0 if (t == -1 and cv[i] > dn1) else (-1.0 if (t == 1 and cv[i] < up1) else t)
        trend[i] = t
        up_p, dn_p = up, dn
    tgt = np.zeros(m, dtype=np.int8)
    pos, stop, take = 0, np.nan, np.nan
    for i in range(m):
        start = pos
        if i and trend[i] == 1 and trend[i - 1] == -1 and buy_f[i]:
            stop, take = cv[i] - atr[i] * k, cv[i] + atr[i] * k
            pos = 1
        if start == 1 and (cv[i] <= stop or cv[i] >= take):   # the levels as updated on this bar
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
