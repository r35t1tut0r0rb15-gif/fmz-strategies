"""HPotter combo of the 123 reversal and the ADXR, 1-hour bars: long while both sides say up, short while both say down,
flat otherwise. The 123 side is as in the other combo ports (stochastic 14 / 1 / 3, level 50); the ADXR side is up when
the ADXR (ADX 14 averaged with its value 14 bars back) is under 13 and down when it is over 45.
Port of FMZ strategy #432346 "Momentum Trend Following Oscillation Strategy" (Combo Backtest 123 Reversal and Average Directional Movement Index Rating).

FMZ source id: 432346

Source
    https://www.fmz.com/strategy/432346 (PineScript v3, FMZ last modified 2023-11-16 16:46:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 209-255), stoch 14 / 1 / 3, level 50, ADX 14, ADXR 14, signals 13 / 45, reverse false
    p123 as Reversal123(14, 1, 3, 50)
    adx = 100 x rma(|plus - minus| / (plus + minus), 14), plus / minus = fixnan(100 x rma(DM+- , 14) / rma(tr, 14))
    adxr = (adx + adx[14]) / 2;  padxr = adxr < 13 ? 1 : adxr > 45 ? -1 : padxr[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each side keeps its last state until it changes, as written; fixnan keeps the last valid DI
      value (coded as a running value, nothing is filled in the bars). rma is Wilder smoothing.
      strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and ADXR levels.
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

NAME = "fmz_432346_combo_123_adxr"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "sig2": [45, 30],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50, "adx_len": 14, "adxr_len": 14, "sig1": 13,
                  "sig2": 45}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _keep_last(v):
    """Pine fixnan: the last non-NaN value up to each bar (a running value on the indicator)."""
    out = np.full(len(v), np.nan)
    last = np.nan
    for i, x in enumerate(v):
        if not np.isnan(x):
            last = x
        out[i] = last
    return out


def _adx(h, lo, c, n):
    up = h.diff()
    dn = -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    trur = tr.ewm(alpha=1 / n, adjust=False).mean()
    dmp = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index)
    dmm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index)
    plus = _keep_last((100 * dmp.ewm(alpha=1 / n, adjust=False).mean() / trur).to_numpy(dtype=float))
    minus = _keep_last((100 * dmm.ewm(alpha=1 / n, adjust=False).mean() / trur).to_numpy(dtype=float))
    s = plus + minus
    ratio = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1.0, s), index=h.index)
    return 100 * ratio.ewm(alpha=1 / n, adjust=False).mean()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    lv = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    a_up = ((c2 < c1) & (c > c1) & (k < d) & (k > lv)).to_numpy()
    a_dn = ((c2 > c1) & (c < c1) & (k > d) & (k < lv)).to_numpy()
    adx = _adx(h, lo, c, int(p["adx_len"]))
    adxr = ((adx + adx.shift(int(p["adxr_len"]))) / 2).to_numpy()
    s1v, s2v = float(p["sig1"]), float(p["sig2"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    s1 = s2 = 0
    for i in range(m):
        if a_up[i]:
            s1 = 1
        elif a_dn[i]:
            s1 = -1
        if adxr[i] < s1v:
            s2 = 1
        elif adxr[i] > s2v:
            s2 = -1
        tgt[i] = 1 if (s1 == 1 and s2 == 1) else (-1 if (s1 == -1 and s2 == -1) else 0)
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
