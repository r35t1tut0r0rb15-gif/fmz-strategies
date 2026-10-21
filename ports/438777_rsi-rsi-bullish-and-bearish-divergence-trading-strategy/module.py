"""RSI 20 divergences at confirmed pivots (5 / 5), 15-minute bars: a regular or hidden bullish divergence at an RSI pivot low goes long, a regular or hidden bearish divergence at an RSI pivot high goes short;
reversing; no other exit.
Port of FMZ strategy #438777 "RSI多空分歧指标交易策略RSI-Bullish-and-Bearish-Divergence-Trading-Strategy" (Divergence Indicator).

FMZ source id: 438777

Source
    https://www.fmz.com/strategy/438777 (PineScript v5, FMZ last modified 2024-01-15 12:09:54).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 128-264), RSI 20 on close; pivots 5 / 5, range 5-60; all four divergence types on
    bull = low[5] < previous pivot's low[5] and rsi[5] > previous pivot's rsi[5] and barssince(plFound[1]) in 5..60 and plFound -> entry (long);  hidden bull: higher price low, lower RSI low -> entry (long)
    bear / hidden bear mirror on pivot highs -> entry (short);  the closes are commented out

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivots are strict on both sides (as #434470) and confirmed 5 bars later; the comparisons take
      the previous pivot's RSI and low (high). The two long ids (and the two short ids) share one
      position (default pyramiding): a second same-side entry is ignored. The closes are commented out,
      so positions end at the opposite entry. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI pivots and divergences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG438777 (3 members, best partner #439702, Jaccard 0.870); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438777_rsi20_divergence_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [20, 14],
    "lb": [5, 3],
}
DEFAULT_PARAMS = {"rsi_len": 20, "lb": 5, "range_lower": 5, "range_upper": 60}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _pivot(x, left, right, low):
    """True at bar i when bar i - right is a strict pivot (both sides), known at bar i."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for i in range(left + right, m):
        p = i - right
        v = x[p]
        if np.isnan(v):
            continue
        w = np.concatenate((x[p - left:p], x[p + 1:i + 1]))
        if np.isnan(w).any():
            continue
        out[i] = (v < w).all() if low else (v > w).all()
    return out


def _divergences(osc, price, found, lb, lo_rng, hi_rng):
    """Regular (price lower, osc higher for lows) and hidden flags at bars where a pivot is found."""
    m = len(osc)
    reg, hid = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_o = last_p = np.nan
    last_bar = -1
    for i in range(m):
        if found[i]:
            o_now, p_now = osc[i - lb], price[i - lb]
            bars = i - last_bar - 1 if last_bar >= 0 else -1      # barssince(found[1])
            ok = last_bar >= 0 and lo_rng <= bars <= hi_rng
            reg[i] = ok and p_now < last_p and o_now > last_o
            hid[i] = ok and p_now > last_p and o_now < last_o
            last_o, last_p, last_bar = o_now, p_now, i
    return reg, hid


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    osc = _rsi(c, int(p["rsi_len"])).to_numpy()
    lb = int(p["lb"])
    pl = _pivot(osc, lb, lb, True)
    ph = _pivot(osc, lb, lb, False)
    lr, hr = int(p["range_lower"]), int(p["range_upper"])
    bull, hbull = _divergences(osc, lo.to_numpy(dtype=float), pl, lb, lr, hr)
    bear, hbear = _divergences(-osc, -h.to_numpy(dtype=float), ph, lb, lr, hr)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(bull | hbull, index=ix), false, pd.Series(bear | hbear, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
