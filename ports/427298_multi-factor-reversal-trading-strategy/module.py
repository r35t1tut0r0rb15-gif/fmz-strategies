"""Combo: 123 reversal and Polarized Fractal Efficiency (PFE): long while both the 123-reversal state
(stochastic 14 / 1 / 3, level 50) and the PFE state (EMA 5 of PFE 9 above +50) are long, short while
both are short (PFE below -50), flat otherwise.
Port of FMZ strategy #427298 "Multi-factor Reversal Trading Strategy".

FMZ source id: 427298

Source
    https://www.fmz.com/strategy/427298 (PineScript v4, FMZ last modified 2023-09-19 21:13:04).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 175-218), 123: 14 / 1 / 3 / 50; PFE 9, EMA 5, bands +-50
    PFE = sqrt((close - close[9])^2 + 100); C2C = sum(sqrt((close - close[1])^2 + 1), 9)
    eff = +-round(100 PFE / C2C) (sign of close - close[9]); x = ema(eff, 5)
    pPFE = x < -50 ? -1 : x > 50 ? 1 : pPFE[1]; p123 as in the 123-reversal combos
    both 1 -> long; both -1 -> short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: PFE adds squared price differences to squared bar counts (100 = 10^2, 1 per bar),
      so as written it depends on the price scale (on a pair near 1.10 the bar counts dominate).
      The price differences are measured in multiples of Wilder ATR(14) of the same bar, so one ATR
      counts as one bar (ADAPT); the rest of the formula is as written (round() kept).
    * strategy.entry reverses: REVERSAL INTENDED; disagreement closes. "Trade reverse" is off.
    * FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, PFE price differences in ATR units.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427298_combo_123_pfe"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_pfe": [9, 20],
    "band": [50, 30],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length_pfe": 9,
                  "length_ema": 5, "band": 50, "atr_length": 14}


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


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    s = 0
    for i in range(len(up)):
        if up[i]:
            s = 1
        elif dn[i]:
            s = -1
        out[i] = s
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
    st = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    fast = st.rolling(int(p["k_smoothing"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lvl = p["level"]
    s123 = _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > lvl)).to_numpy(),
                  ((c2 > c1) & (c < c1) & (fast > slow) & (fast < lvl)).to_numpy())
    L = int(p["length_pfe"])
    atr = _atr(bars_df, int(p["atr_length"]))
    dL = (c - c.shift(L)) / atr
    pfe = np.sqrt(dL ** 2 + 100)
    c2c = np.sqrt(((c - c1) / atr) ** 2 + 1).rolling(L).sum()
    ratio = 100 * pfe / c2c
    eff = np.where((c - c.shift(L)) > 0, np.round(ratio), np.round(-ratio))
    eff = pd.Series(eff, index=c.index).where(ratio.notna())
    x = eff.ewm(span=int(p["length_ema"]), adjust=False).mean()
    b = float(p["band"])
    spfe = _state((x > b).to_numpy(), (x < -b).to_numpy())
    tgt = np.where((s123 == 1) & (spfe == 1), 1, np.where((s123 == -1) & (spfe == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
