"""Three averages, Laguerre RSI and ADX, 1-minute bars: EMA 16 > EMA 48 > SMA 200 with the Laguerre RSI over 80 and the ADX
over 20 goes long; the mirror goes short; a long is closed by the EMA 16 crossing under the EMA 48, a short by the
crossing back over. The optional fixed tick bracket is off by default and not ported.
Port of FMZ strategy #435272 "Momentum Breakout Strategy" (3MA + Laguerre RSI + ADX [Pt]).

FMZ source id: 435272

Source
    https://www.fmz.com/strategy/435272 (PineScript v5, FMZ last modified 2023-12-13 17:08:53).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 236-362), EMA 16 / 48, SMA 200; Laguerre RSI alpha 0.2 (80 / 20); ADX 14 / 14 over 20; session and bracket switches off
    L_entry1 = ma_bull and LaRSI > 80 and sig > 20;  S_entry1 = ma_bear and LaRSI < 20 and sig > 20;  L_exit1 = crossunder(ema1, ema2);  S_exit1 = crossover(ema1, ema2)
    L_entry1 -> entry long;  S_entry1 -> entry short;  L_exit1 -> close long;  S_exit1 -> close short   (use_SLPT false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Laguerre filter starts from zero, as written (nz of the first value). The ADX is the
      built-in-style DMI with RMA smoothing and fixnan. The entry session and the date window are
      off or always true; "Use Fixed SL / PT" (50 / 100 ticks) is off by default and is not ported
      (the tick bracket would need an ATR re-expression: that version is owed). Entry and exit
      signals are combined into one position state per bar: a long entry on the bar of a short exit
      is the reversal Pine performs. REVERSAL INTENDED. The percent-of-equity size is sizing.
    * FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, tick bracket switch off by default: not ported.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the tick bracket inputs stored.
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

NAME = "fmz_435272_three_ma_laguerre_adx"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1_len": [16, 8],
    "adx_th": [20, 25],
}
DEFAULT_PARAMS = {"ema1_len": 16, "ema2_len": 48, "sma_len": 200, "alpha": 0.2, "adx_len": 14, "di_len": 14, "adx_th": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _laguerre_rsi(cv, alpha):
    gamma = 1 - alpha
    m = len(cv)
    out = np.zeros(m)
    l0 = l1 = l2 = l3 = 0.0
    for i in range(m):
        p0, p1, p2 = l0, l1, l2
        l0 = (1 - gamma) * cv[i] + gamma * p0
        l1 = -gamma * l0 + p0 + gamma * l1
        l2 = -gamma * l1 + p1 + gamma * l2
        l3 = -gamma * l2 + p2 + gamma * l3
        cu = (l0 - l1 if l0 > l1 else 0.0) + (l1 - l2 if l1 > l2 else 0.0) + (l2 - l3 if l2 > l3 else 0.0)
        cd = (l1 - l0 if l0 < l1 else 0.0) + (l2 - l1 if l1 < l2 else 0.0) + (l3 - l2 if l2 < l3 else 0.0)
        t = cu + cd
        out[i] = 0.0 if t == 0 else 100 * cu / t
    return out


def _adx(h, lo, c, di_len, adx_len):
    up, dn = h.diff(), -lo.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(up.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    a = 1 / di_len
    trn = tr.ewm(alpha=a, adjust=False).mean()
    plus = (100 * plus_dm.ewm(alpha=a, adjust=False).mean() / trn).ffill()
    minus = (100 * minus_dm.ewm(alpha=a, adjust=False).mean() / trn).ffill()
    s = plus + minus
    return 100 * (((plus - minus).abs() / s.where(s != 0, 1.0)).ewm(alpha=1 / adx_len, adjust=False).mean())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e1 = c.ewm(span=int(p["ema1_len"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2_len"]), adjust=False).mean()
    s1 = c.rolling(int(p["sma_len"])).mean()
    la = pd.Series(_laguerre_rsi(c.to_numpy(dtype=float), float(p["alpha"])), index=c.index)
    adx = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    act = adx > float(p["adx_th"])
    le = ((e1 > e2) & (e2 > s1) & (la > 80) & act).to_numpy()
    se = ((e1 < e2) & (e2 < s1) & (la < 20) & act).to_numpy()
    lx = ((e1 < e2) & (e1.shift(1) >= e2.shift(1))).to_numpy()
    sx = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).to_numpy()
    m = len(le)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if le[i]:
            q = 1
        elif se[i]:
            q = -1
        elif q == 1 and lx[i]:
            q = 0
        elif q == -1 and sx[i]:
            q = 0
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((tgt == 0) & (prev == 1), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((tgt == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
