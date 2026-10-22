"""Weighted Ichimoku / stochastic-RSI vote, 1-hour bars: a weighted score above 50 from the strong cloud test (35), the conversion-over-base test (20) and an oversold stochastic-RSI turn (30) goes
long, the mirror short; reversing.
Port of FMZ strategy #442006 "Byron Serpent Cloud Quant Strategy" (Baracuda Ichimoku/StochRSI Strategy).

FMZ source id: 442006

Source
    https://www.fmz.com/strategy/442006 (PineScript v3, FMZ last modified 2024-02-18 15:36:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-147), decision 50; weights strong 35, standard 20 (unused), weak 20, stoch RSI 30; Ichimoku 9 / 26 / 52 (displacement 5, unused); RSI 8, stoch 5, K 3, D 3; 20 / 80
    stronglong = conversion > base and leadLine1 > leadLine2;  weaklong = conversion > base;  RSIlong = k > d and k < 20 and d < 20
    long = 35 stronglong + 20 weaklong + 30 RSIlong > 50 -> entry long;  short mirrored -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lead lines are the undisplaced values (the displacement input is unused). With these weights a
      strong cloud test alone scores 55 and the weak test plus the stochastic-RSI turn 50 (not above 50), so
      the vote is the strong test, as written. The entries are levels; an entry while already in that
      direction does nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku and stochastic-RSI vote.
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

NAME = "fmz_442006_ichimoku_stochrsi_weighted_vote_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "decision_weight": [50, 40],
    "base_periods": [26, 52],
}
DEFAULT_PARAMS = {"decision_weight": 50, "base_periods": 26, "w_strong": 35, "w_weak": 20, "w_rsi": 30,
                  "conv": 9, "span2": 52, "rsi_len": 8, "stoch_len": 5, "smooth_k": 3, "smooth_d": 3,
                  "over_sold": 20, "over_bought": 80}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def don(k):
        return (lo.rolling(k).min() + h.rolling(k).max()) / 2

    conv, base = don(int(p["conv"])), don(int(p["base_periods"]))
    l1, l2 = (conv + base) / 2, don(int(p["span2"]))
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    rl, rh = r.rolling(n).min(), r.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (r - rl) / (rh - rl).where(rh > rl)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    os_, ob = float(p["over_sold"]), float(p["over_bought"])
    ws, ww, wr = float(p["w_strong"]), float(p["w_weak"]), float(p["w_rsi"])
    sl_ = ((conv > base) & (l1 > l2)).astype(float)
    ss_ = ((conv < base) & (l1 < l2)).astype(float)
    wl, wsh = (conv > base).astype(float), (conv < base).astype(float)
    rlg = ((k > d) & (k < os_) & (d < os_)).astype(float)
    rsh = ((k < d) & (k > ob) & (d > ob)).astype(float)
    dw = float(p["decision_weight"])
    le = (sl_ * ws + wl * ww + rlg * wr) > dw
    se = (ss_ * ws + wsh * ww + rsh * wr) > dw
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
