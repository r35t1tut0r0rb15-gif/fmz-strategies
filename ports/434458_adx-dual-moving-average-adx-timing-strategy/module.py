"""HPotter combo of the 2/20 EMA side and an ADXR band, 2-hour bars: long while both say up, short while both say down,
flat otherwise. The ADXR side is up while the ADXR 14 is under 13 and down while it is above 45, held in between.
Port of FMZ strategy #434458 "双均线ADX择时策略Dual-Moving-Average-ADX-Timing-Strategy" (Combo 2/20 EMA & ADXR).

FMZ source id: 434458

Source
    https://www.fmz.com/strategy/434458 (PineScript v5, FMZ last modified 2023-12-06 15:48:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 212-265), EMA 14; ADX 14, ADXR 14, signals 13 / 45; reverse false; start 2005-01-01
    nXS = (min(low, low[1]) > ema14 or max(high, high[1]) < ema14) ? min(low, low[1]) : max(high, high[1]);  pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pos[1]
    ADXR = (adx + adx[14]) / 2;  pos = ADXR < 13 ? 1 : ADXR > 45 ? -1 : pos[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is Pine's: rma-smoothed DI from the bar changes (fixnan) and an rma 14 of the DI
      spread over its sum (a zero sum read as 1). The start date (2005) is the author's window:
      dropped. strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an average side and ADXR levels.
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

NAME = "fmz_434458_combo_2_20_ema_adxr"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "signal2": [45, 30],
}
DEFAULT_PARAMS = {"length": 14, "adx_len": 14, "adxr_len": 14, "signal1": 13.0, "signal2": 45}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan(v, index):
    """Pine fixnan: a NaN (or inf) takes the last valid value before it (past values only)."""
    out = np.array(v, dtype=float)
    last = np.nan
    for i in range(len(out)):
        if np.isfinite(out[i]):
            last = out[i]
        else:
            out[i] = last
    return pd.Series(out, index=index)


def _adx(h, lo, c, n):
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    rma = lambda x: x.ewm(alpha=1 / n, adjust=False).mean()  # noqa: E731
    trur = rma(tr)
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index)
    ndm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index)
    plus = _fixnan((100 * rma(pdm) / trur).to_numpy(), c.index)
    minus = _fixnan((100 * rma(ndm) / trur).to_numpy(), c.index)
    s = plus + minus
    return 100 * rma((plus - minus).abs() / s.where(s != 0, 1.0))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    nhh = pd.concat([h, h.shift(1)], axis=1).max(axis=1, skipna=False)
    nll = pd.concat([lo, lo.shift(1)], axis=1).min(axis=1, skipna=False)
    nxs = np.where((nll > xa) | (nhh < xa), nll, nhh)
    c1 = c.shift(1).to_numpy()
    adx = _adx(h, lo, c, int(p["adx_len"]))
    adxr = ((adx + adx.shift(int(p["adxr_len"]))) / 2).to_numpy()
    s1, s2 = float(p["signal1"]), float(p["signal2"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pe, pa = 0, 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if nxs[i] > c1[i]:
                pe = -1
            elif nxs[i] < c1[i]:
                pe = 1
            if adxr[i] < s1:
                pa = 1
            elif adxr[i] > s2:
                pa = -1
            tgt[i] = 1 if (pe == 1 and pa == 1) else (-1 if (pe == -1 and pa == -1) else 0)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
