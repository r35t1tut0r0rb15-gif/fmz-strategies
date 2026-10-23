"""A score of six indicators (close vs EMA 80, MACD 12 / 26 / 9 lines, an EMA 15 close-open oscillator at +/- 3 each; RSI 2 zones, a stochastic 11 / 3 and Bollinger 10 / 2 at up to +/- 2), 4-hour bars: a score of 7 or more goes long and under 3 closes it; -7 or less goes short and over -3 closes it; reversing.
Port of FMZ strategy #428095 "多重指标EMA策略Multi-Indicator-EMA-Strategy" (ELIA MULTI STRATEGY).

FMZ source id: 428095

Source
    https://www.fmz.com/strategy/428095 (PineScript v4, FMZ last modified 2023-09-28 15:57:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 223-314), EMA 80; MACD 12 / 26 / 9 (the inputs are not used); OCC EMA 15; RSI 2; stoch 11, smooth 3; BB 10, 2; strategy() commented out
    trigger = (close > ema80 ? 3 : -3) + (macd > signal ? 3 : -3) + (occ > 0 ? 3 : -3) + rsi zones (2 / 1 / -2 / -1 / 0) + (stoch < 20 ? 2 : > 80 ? -2 : 0) + (close < lower ? 2 : > upper ? -2 : 0)
    trigger >= 7 -> entry LONG;  trigger < 3 -> close LONG;  trigger <= -7 -> entry SHORT;  trigger > -3 -> close SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI zones are as written: under 20 scores 2, 50-80 scores 1, over 80 scores -2, 20-50 scores -1,
      exactly 20, 50 or 80 score 0. The momentum, OBV and Donchian values are computed but never scored, so
      volume does not reach the orders: ported as not using volume (check 8). The closes act only on a
      position the bar's entries leave unchanged. The year window (2021 .. 9999) is dropped. REVERSAL
      INTENDED. strategy() is commented out. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, multi-indicator score thresholds.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (25 % of equity, capital 1000) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the author's 2021 .. 9999 window dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428095_six_indicator_score_7_3_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "emalen": [80, 50],
    "entry_score": [7, 9],
}
DEFAULT_PARAMS = {"emalen": 80, "entry_score": 7, "exit_score": 3, "occlen": 15, "rsilen": 2, "stochklen": 11,
                  "stochlen": 3, "bblength": 10, "mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ema = c.ewm(span=int(p["emalen"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    n = int(p["occlen"])
    occ = c.ewm(span=n, adjust=False).mean() - o.ewm(span=n, adjust=False).mean()
    r = _rsi(c, int(p["rsilen"]))
    k = int(p["stochklen"])
    raw = 100 * (c - lo.rolling(k).min()) / (h.rolling(k).max() - lo.rolling(k).min()).replace(0.0, np.nan)
    st = raw.rolling(int(p["stochlen"])).mean()
    b = int(p["bblength"])
    basis, dev = c.rolling(b).mean(), float(p["mult"]) * c.rolling(b).std(ddof=0)
    s_ema = np.where(c > ema, 3, -3)
    s_macd = np.where(macd > sig, 3, -3)
    s_occ = np.where(occ > 0, 3, -3)
    rv = r.to_numpy()
    s_rsi = np.where(rv < 20, 2, np.where((rv > 50) & (rv < 80), 1, np.where(rv > 80, -2,
                     np.where((rv < 50) & (rv > 20), -1, 0))))
    sv = st.to_numpy()
    s_st = np.where(sv < 20, 2, np.where(sv > 80, -2, 0))
    s_bb = np.where(c < basis - dev, 2, np.where(c > basis + dev, -2, 0))
    trig = (s_ema + s_macd + s_occ + s_rsi + s_st + s_bb).astype(float)
    trig[np.isnan(ema.to_numpy()) | np.isnan(sig.to_numpy())] = 0.0
    es, xs = float(p["entry_score"]), float(p["exit_score"])
    m = len(trig)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        old = pos
        if trig[i] >= es:
            pos = 1
        if trig[i] < xs and old == 1 and pos == 1:
            pos = 0
        if trig[i] <= -es:
            pos = -1
        if trig[i] > -xs and old == -1 and pos == -1:
            pos = 0
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
