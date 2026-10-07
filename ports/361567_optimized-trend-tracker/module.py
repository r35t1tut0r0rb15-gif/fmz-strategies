"""Optimized Trend Tracker (OTT): the VAR (CMO-adaptive) average crossing the OTT line two bars
back; long on the cross up, short on the cross down (always in).
Port of FMZ strategy #361567 "Optimized-Trend-Tracker" (KivancOzbilgic / Anil Ozeksi OTT).

Source
    https://www.fmz.com/strategy/361567 (PineScript v4, FMZ last modified 2022-05-07 01:30:12).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 104-190), length 2, percent 1.4, mav "VAR"
    VAR: alpha = 2/(length+1); CMO over 9 bars of close changes;
         VAR := alpha*|CMO|*src + (1-alpha*|CMO|)*nz(VAR[1])
    fark = MAvg*percent%; longStop = MAvg-fark (ratchets up), shortStop = MAvg+fark (ratchets down)
    dir flips on MAvg crossing the previous stops; MT = dir==1 ? longStop : shortStop
    OTT = MAvg > MT ? MT*(200+percent)/200 : MT*(200-percent)/200
    crossover(MAvg, OTT[2]) -> entry long;  crossunder(MAvg, OTT[2]) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the percent band fark = MAvg*percent% becomes `band_atr` x Wilder ATR(14),
      and the OTT offset MT*percent/200 becomes half of that band (the source's ratio).
    * VAR starts from 0 (nz) as written; the port emits nothing for the first 50 bars.
    * Only the default moving-average type (VAR) is ported; the other seven are input options.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361567_ott_var_cross"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [2, 5, 10],
    "band_atr": [1.0, 2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 2, "band_atr": 2.0, "atr_length": 14, "warmup": 50}


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
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _var_ma(src, length):
    d = src.diff()
    ud = d.clip(lower=0).rolling(9).sum()
    dd = (-d).clip(lower=0).rolling(9).sum()
    cmo = ((ud - dd) / (ud + dd)).replace([np.inf, -np.inf], np.nan).fillna(0).abs().to_numpy()
    s = src.to_numpy(dtype=float)
    alpha = 2 / (length + 1)
    out = np.zeros(len(s))
    prev = 0.0
    for i in range(len(s)):
        k = alpha * cmo[i]
        prev = out[i] = k * s[i] + (1 - k) * prev
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    mavg = _var_ma(bars_df["close"], int(p["length"]))
    fark = p["band_atr"] * _atr_pine(bars_df, int(p["atr_length"])).to_numpy()
    m = len(mavg)
    ott = np.full(m, np.nan)
    ls_prev = ss_prev = np.nan
    dirn = 1
    for i in range(m):
        if np.isnan(fark[i]):
            continue
        ls, ss = mavg[i] - fark[i], mavg[i] + fark[i]
        lsp = ls if np.isnan(ls_prev) else ls_prev          # nz(longStop[1], longStop)
        ssp = ss if np.isnan(ss_prev) else ss_prev
        ls = max(ls, lsp) if mavg[i] > lsp else ls
        ss = min(ss, ssp) if mavg[i] < ssp else ss
        if dirn == -1 and mavg[i] > ssp:
            dirn = 1
        elif dirn == 1 and mavg[i] < lsp:
            dirn = -1
        mt = ls if dirn == 1 else ss
        ott[i] = mt + fark[i] / 2 if mavg[i] > mt else mt - fark[i] / 2
        ls_prev, ss_prev = ls, ss
    ott2 = pd.Series(ott).shift(2).to_numpy()
    mv = pd.Series(mavg).to_numpy()

    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(max(int(p["warmup"]), 1), m):
        up = mv[i] > ott2[i] and mv[i - 1] <= ott2[i - 1]
        dn = mv[i] < ott2[i] and mv[i - 1] >= ott2[i - 1]
        if up and pos != 1:
            le[i], pos = True, 1
        elif dn and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
