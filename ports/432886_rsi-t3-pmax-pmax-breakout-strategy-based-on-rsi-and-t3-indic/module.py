"""PMax on RSI (KivancOzbilgic), 5-minute bars: the Tillson T3 (8, 0.7) of a Wilder RSI 14 crossing above its PMax line (a
3 x ATR-of-RSI ratchet band, ATR from the RSI of the highs and lows, SMA 10) goes long, crossing below goes short; always
in once started.
Port of FMZ strategy #432886 "基于RSI和T3指标的PMax自适应突破策略PMax-Breakout-Strategy-Based-on-RSI-and-T3-Indicators" (PMax on Rsi w T3 Strategy).

FMZ source id: 432886

Source
    https://www.fmz.com/strategy/432886 (PineScript v4, FMZ last modified 2023-11-22 15:03:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 175-272), RSI 14 (Wilder, zero-seeded), T3 8 / 0.7, ATR-of-RSI 10, multiplier 3
    rsi = 100 - 100 / (1 + wwma(up, 14) / wwma(down, 14));  rsih / rsil from SMA-based averages with the bar's high / low change
    atr = sma(max(rsih - rsil, |rsih - rsi[1]|, |rsil - rsi[1]|), 10);  T3 = Tillson T3 of rsi
    PMax: longStop / shortStop = T3 -+ 3 atr with ratchets; dir flips when T3 crosses the opposite stop
    crossover(T3, PMax) -> entry long;  crossunder(T3, PMax) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Coded as written: the Wilder averages start from 0 (nz), the "high / low RSI" use SMA-based
      averages updated with the bar's high / low change, the PMax ratchets and direction as in the
      source. Everything is in RSI units, so the rule is scale-free.
    * strategy.entry reverses: REVERSAL INTENDED. The date window (2005 on) is dropped. FREQ = "5min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI-unit bands.
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

NAME = "fmz_432886_pmax_on_rsi_t3"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 1.5],
    "t3_len": [8, 5],
}
DEFAULT_PARAMS = {"mult": 3.0, "t3_len": 8, "t3_a": 0.7, "atr_len": 10, "rsi_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wwma(x, n):
    """The source's Wwma_Func: a / n smoothing started from 0 (nz)."""
    v = np.nan_to_num(x.to_numpy(dtype=float))
    out = np.zeros(len(v))
    prev = 0.0
    for i, z in enumerate(v):
        prev = (1 / n) * z + (1 - 1 / n) * prev
        out[i] = prev
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["rsi_len"])
    c1 = c.shift(1)
    i1 = (c - c1).where(c >= c1, 0.0)
    i2 = (c1 - c).where(c < c1, 0.0)
    rsi = 100 - 100 / (1 + _wwma(i1, n) / _wwma(i2, n))
    au, ad = i1.rolling(n).mean(), i2.rolling(n).mean()
    k1 = (h - c1).where(h > c1, 0.0)
    k2 = (c1 - h).where(h < c1, 0.0)
    k3 = (lo - c1).where(lo > c1, 0.0)
    k4 = (c1 - lo).where(lo < c1, 0.0)
    rsih = 100 - 100 / (1 + ((au * (n - 1) + k1) / n) / ((ad * (n - 1) + k2) / n))
    rsil = 100 - 100 / (1 + ((au * (n - 1) + k3) / n) / ((ad * (n - 1) + k4) / n))
    r1 = rsi.shift(1)
    trr = pd.concat([rsih - rsil, (rsih - r1).abs(), (rsil - r1).abs()], axis=1).max(axis=1, skipna=False)
    atr = trr.rolling(int(p["atr_len"])).mean().to_numpy()
    L, a = int(p["t3_len"]), float(p["t3_a"])
    e = [rsi]
    for _ in range(6):
        e.append(e[-1].ewm(span=L, adjust=False).mean())
    t3 = (-a ** 3 * e[6] + (3 * a * a + 3 * a ** 3) * e[5] + (-6 * a * a - 3 * a - 3 * a ** 3) * e[4]
          + (1 + 3 * a + a ** 3 + 3 * a * a) * e[3]).to_numpy()
    k = float(p["mult"])
    m = len(c)
    pmax = np.full(m, np.nan)
    ls_p = ss_p = np.nan
    d = 1
    for i in range(m):
        ls, ss = t3[i] - k * atr[i], t3[i] + k * atr[i]
        lsp = ls if np.isnan(ls_p) else ls_p
        ssp = ss if np.isnan(ss_p) else ss_p
        ls = max(ls, lsp) if t3[i] > lsp else ls
        ss = min(ss, ssp) if t3[i] < ssp else ss
        if d == -1 and t3[i] > ssp:
            d = 1
        elif d == 1 and t3[i] < lsp:
            d = -1
        pmax[i] = ls if d == 1 else ss
        ls_p, ss_p = ls, ss
    t3s, pm = pd.Series(t3, index=c.index), pd.Series(pmax, index=c.index)
    x = ((t3s > pm) & (t3s.shift(1) <= pm.shift(1))).to_numpy()
    y = ((t3s < pm) & (t3s.shift(1) >= pm.shift(1))).to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if x[i]:
            pos = 1
        if y[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a_, index=bars_df.index) for a_ in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
