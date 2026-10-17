"""HPotter combo of the 123 reversal and the Ergodic CSI, 1-hour bars: long while both sides say up, short while both say
down, flat otherwise. The CSI side is K x ADXR x true range / close, smoothed over 5 bars; above 0.02 it says up,
otherwise down (the 0.06 sell zone overlaps, as written).
Port of FMZ strategy #433069 "Combo Momentum Reversal Dual Rail Matching Strategy" (Combo Backtest 123 Reversal & Ergodic CSI).

FMZ source id: 433069

Source
    https://www.fmz.com/strategy/433069 (PineScript v4, FMZ last modified 2023-11-24 10:17:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 164-219), stoch 14 / 1 / 3, level 50; CSI r 32, length 1, big point value 1, smoothing 5, sell 0.06, buy 0.02; reverse false
    p123 as Reversal123(14, 1, 3, 50);  K = 100 (1 / sqrt(32) / 155);  ADX(1) with rma, ADXR = (ADX + ADX[1]) / 2
    CSI = K x ADXR x atr(1) / 1 / close;  pcsi = sma(CSI, 5) > 0.02 ? 1 : sma(CSI, 5) <= 0.06 ? -1 : pcsi[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The CSI is a true range divided by the close times ADXR, so it is scale-free. With the buy zone
      checked first, every value above 0.02 is "up" and every other value "down" (the zones overlap,
      as written). fixnan in the ADX holds the last defined value. rma(x, 1) is x itself.
    * Each side keeps its last state until it changes. strategy.entry reverses: REVERSAL INTENDED.
      reverse is false. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and a range / close ratio.
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

NAME = "fmz_433069_combo_123_ergodic_csi"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "buy_zone": [0.02, 0.04],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "r": 32, "csi_len": 1,
                  "big_point": 1.0, "smth_len": 5, "sell_zone": 0.06, "buy_zone": 0.02}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _rma(x, n):
    return x.ewm(alpha=1 / n, adjust=False).mean()


def _fixnan(x):
    """Pine fixnan(): an undefined value takes the indicator's last defined value (no bars are filled)."""
    v = x.replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


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
    p123 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    ln = int(p["csi_len"])
    up, dn = h.diff(), -lo.diff()
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    trur = _rma(tr, ln)
    plus = (100 * _rma(pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index), ln) / trur)
    minus = (100 * _rma(pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index), ln) / trur)
    plus, minus = _fixnan(plus), _fixnan(minus)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), ln)
    adxr = (adx + adx.shift(1)) * 0.5
    kk = 100 * (float(p["big_point"]) / np.sqrt(float(p["r"])) / (150 + 5))
    csi = (kk * adxr * tr / ln) / c
    sm = csi.rolling(int(p["smth_len"])).mean()
    pcsi = _hold((sm > p["buy_zone"]).to_numpy(), (sm <= p["sell_zone"]).to_numpy())
    tgt = np.where((p123 == 1) & (pcsi == 1), 1, np.where((p123 == -1) & (pcsi == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
