"""Noro's Trend MAs v2.3: a trend state from the 21-bar mid-channel of the close (two bars' lows above
it = up, two highs below = down). Long on a dip under the 5-bar mid-channel on two red bars in an
up-trend, on a red bar with both highs under both centres ("extreme"), or on a "CryptoBottom" bar;
short on a pop above the 5-bar mid-channel on two green bars in a down-trend.
Port of FMZ strategy #427506 "Trend Moving Average Trading Strategy".

FMZ source id: 427506

Source
    https://www.fmz.com/strategy/427506 (PineScript v2, FMZ last modified 2023-09-21 20:34:43).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 196-276), fast 5, slow 21, bars 2, extreme on, stops off
    center = mid(highest / lowest(close, 21)); center2 = mid(highest / lowest(close, 5))
    trend = low > center and low[1] > center[1] ? 1 : high < center and high[1] < center[1] ? -1 : trend[1]
    up1 = trend 1 and low < center2 and two red bars; dn1 = trend -1 and high > center2 and two green bars
    up2 = high < center and high < center2 and red bar; up3 = CryptoBottom (as Noro's bands)
    up1 or up2 or up3 -> entry long; dn1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md; Noro's template)
    * "stops" is off by default: the stop levels stay na and no stop is placed.
    * The year / month / day window and its close_all are the author's backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED; on a bar with both a long and a short condition the
      side not held is taken (long first from flat).
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts and ratios of averages.
    3 crypto-exchange-only: no (the "crypto/fiat only" note on the extreme switch is advice, not a feature).
    4 signals only: 100 % of equity and the (off) percent stop stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND427506 (4 members, best partner #438058, Jaccard 0.651); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427506_noro_trend_mas_v23"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow_len": [21, 10, 42],
    "need_ex": [True, False],
}
DEFAULT_PARAMS = {"fast_len": 5, "slow_len": 21, "bars": 2, "need_ex": True, "use_fast": True}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ns, nf = int(p["slow_len"]), int(p["fast_len"])
    center = ((c.rolling(ns).max() + c.rolling(ns).min()) / 2).to_numpy()
    center2 = ((c.rolling(nf).max() + c.rolling(nf).min()) / 2).to_numpy()
    ch = c.diff()
    fu = _rma(ch.clip(lower=0), 2).to_numpy()
    fd = _rma((-ch).clip(lower=0), 2).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        frsi = np.where(fd == 0, 100.0, np.where(fu == 0, 0.0, 100 - 100 / (1 + fu / fd)))
    frsi[np.isnan(fu) | np.isnan(fd)] = np.nan
    lencb = (c - c.rolling(10).mean()).abs()
    body_min = pd.concat([o, c], axis=1).min(axis=1)
    up3 = ((c < o) & (lencb > lencb.rolling(100).mean() * 3) & (body_min < body_min.shift(1))).to_numpy() & (frsi < 10)
    bar = np.sign(c - o).to_numpy()
    nb = int(p["bars"])
    red = np.ones(len(bar), dtype=bool)
    green = np.ones(len(bar), dtype=bool)
    for k in range(nb):
        bk = np.concatenate((np.zeros(k), bar[:len(bar) - k])) if k else bar
        red &= bk == -1
        green &= bk == 1
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    use_fast, need_ex = bool(p["use_fast"]), bool(p["need_ex"])
    m = len(bar)
    tgt = np.zeros(m, dtype=np.int8)
    trend, pos = 0, 0
    for i in range(m):
        if i and lv[i] > center[i] and lv[i - 1] > center[i - 1]:
            trend = 1
        elif i and hv[i] < center[i] and hv[i - 1] < center[i - 1]:
            trend = -1
        up1 = trend == 1 and (lv[i] < center2[i] or not use_fast) and red[i]
        dn1 = trend == -1 and (hv[i] > center2[i] or not use_fast) and green[i]
        up2 = hv[i] < center[i] and hv[i] < center2[i] and bar[i] == -1 and need_ex
        long_c = up1 or up2 or bool(up3[i])
        if long_c and pos != 1:
            pos = 1
        elif dn1 and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
