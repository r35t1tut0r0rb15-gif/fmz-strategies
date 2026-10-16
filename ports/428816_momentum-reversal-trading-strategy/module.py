"""HPotter combo, hourly bars: the 123 reversal and a filtered Chande momentum oscillator must agree; both long
holds a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #428816 "Momentum Reversal Trading Strategy" (Combo Backtest 123 Reversal & CMOfilt).

FMZ source id: 428816

Source
    https://www.fmz.com/strategy/428816 (PineScript v4, FMZ last modified 2023-10-09 17:21:27).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 234-280), stochastic 14 / 1 / 3, level 50; CMO 9, filter 3 (price units), bands 70 / -70
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    CMOfilt: changes with |change| <= 3 count as 0; nRes = 100 x sum(change, 9) / sum(|change|, 9)
             nRes > 70 -> 1; nRes < -70 -> -1; else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the filter of 3 price units becomes filter_atr x Wilder ATR(14) of the same bar
      (3 USD on hourly BTC is about 0.02 ATR, judgement before any backtest).
    * stoch(close, high, low, 14) includes the current bar; K smoothing 1, D = SMA 3. A zero sum of
      absolute changes gives na (no change of state).
    * "Trade reverse" defaults to false and is fixed. A one-bar change from long to short reverses:
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit filter -> an ATR multiple.
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

NAME = "fmz_428816_combo_123_cmofilt"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_cmo": [9, 14],
    "filter_atr": [0.02, 0.1],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length_cmo": 9,
                  "filter_atr": 0.02, "top_band": 70, "low_band": -70, "atr_length": 14}


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


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    filt = p["filter_atr"] * _rma(tr, int(p["atr_length"]))
    mom = c - c.shift(1)
    big = mom.abs() > filt
    m_f = mom.where(big, 0.0).where(mom.notna() & filt.notna())
    a_f = mom.abs().where(big, 0.0).where(mom.notna() & filt.notna())
    nc = int(p["length_cmo"])
    nres = 100 * m_f.rolling(nc).sum() / a_f.rolling(nc).sum().replace(0.0, np.nan)
    pos2 = _hold((nres > p["top_band"]).to_numpy(), (nres < p["low_band"]).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
