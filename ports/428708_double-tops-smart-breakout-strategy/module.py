"""HPotter combo, 45-minute bars: the 123 reversal and the Pivot Detector Oscillator must agree; both long
holds a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #428708 "Double Tops Smart Breakout Strategy" (Combo Backtest 123 Reversal & Pivot Detector Oscillator).

FMZ source id: 428708

Source
    https://www.fmz.com/strategy/428708 (PineScript v4, FMZ last modified 2023-10-08 15:17:51).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 232-276), stochastic 14 / 1 / 3, level 50; PDO SMA 200, RSI 14
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror (K > D, K < 50) -> -1; else pos[1]
    PDO: nRes = close > sma200 ? (rsi - 35) / 50 : (rsi - 20) / 50; nRes x 100 > 50 -> 1; < 50 -> -1; else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * stoch(close, high, low, 14) = 100 x (close - lowest low) / (highest high - lowest low), the
      current bar included; K smoothing 1, D = SMA 3 of K. The 123 conditions are as written (K
      above the level for longs).
    * Before the SMA 200 exists nRes is 0 (Pine's iff with na), so the PDO reads -1, as written.
    * "Trade reverse" defaults to false and is fixed. A one-bar change from long to short reverses:
      REVERSAL INTENDED. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and close comparisons only.
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

NAME = "fmz_428708_combo_123_pdo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_ma": [200, 100],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length_ma": 200,
                  "length_rsi": 14}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


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
    r_up = ((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy()
    r_dn = ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy()
    pos1 = _hold(r_up, r_dn)
    ma = c.rolling(int(p["length_ma"])).mean()
    r = _rsi(c, int(p["length_rsi"]))
    nres = pd.Series(np.where(c > ma, (r - 35) / (85 - 35), np.where(c <= ma, (r - 20) / (70 - 20), 0.0)),
                     index=c.index)   # an na RSI gives na: the previous state is kept
    pos2 = _hold((nres * 100 > 50).to_numpy(), (nres * 100 < 50).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
