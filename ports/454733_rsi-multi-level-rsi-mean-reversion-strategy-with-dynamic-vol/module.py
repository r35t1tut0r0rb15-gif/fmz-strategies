"""RSI 20 dips on big bodies below the last pivot low, 1-hour bars: from flat, a falling RSI 20 under 35 / 30 / 25 / 20 on a bar whose body is at least 1 / 0.8 / 0.7 / 0.5 of the largest body of 288 bars, closing under the last 1 / 1 pivot low, goes long; the long closes on a close 60 % of the way from the fill back to that pivot low; the mirror goes short; entries only from flat.
Port of FMZ strategy #454733 "多层级RSI回归交易策略与动态波动率调整-Multi-Level-RSI-Mean-Reversion-Strategy-with-Dynamic-Volatility-Adjustment" (Retorno_Pivots_5min_Novo_v3.3).

FMZ source id: 454733

Source
    https://www.fmz.com/strategy/454733 (PineScript v5, FMZ last modified 2024-06-21 14:16:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-268), pivots 1 / 1; RSI 20; levels 35 / 30 / 25 / 20 (65 / 70 / 75 / 80); body ratios 1 / 0.8 / 0.7 / 0.5 of highest(|c - o|, 288); exit 60 % of the way to the pivot
    opentrades == 0 and rsi < rsi[1] and (a level / body pair) and close < last pivot low -> entry Long;  opentrades 1-4 add-on entries (refused, pyramiding 1)
    opentrades == 1 and close > avg + (pivot low when flat - avg) x 0.6 -> close Long;  the mirror for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * The add-on entries for opentrades 1 to 4 send the same id while the trade is open and are
      refused (pyramiding 1), so only one trade is ever open and only the first exit level applies.
      The exit is a bar-close test against the fill price and the pivot level of the last flat bar
      (the signal bar), followed in a loop, filled at the next open; there is no stop. The fourth short
      level test repeats the third (as written). A pivot is strict on both sides (house helper) and
      known one bar after its bar. Opposite entries cannot occur (entries only from flat). No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exit is a close test.
    2 generic: PASS, RSI dips on big bodies under the pivot.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454733_rsi20_big_body_pivot_break_reversion_from_flat"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [20, 14],
    "body_lookback": [288, 100],
    "exit_frac": [0.6, 1.0],
}
DEFAULT_PARAMS = {"rsi_len": 20, "body_lookback": 288, "exit_frac": 0.6, "piv": 1}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _pivots(x, lb, rb, high):
    """True at bar t when bar t - rb is a strict pivot over lb bars before and rb bars after."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if high:
            out[t] = v > left.max() and v > right.max()
        else:
            out[t] = v < left.min() and v < right.min()
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    r = _rsi(c, int(p["rsi_len"]))
    body = (c - o).abs()
    big = body.rolling(int(p["body_lookback"])).max()
    k = int(p["piv"])
    hv, lv, cv, ov = (x.to_numpy(dtype=float) for x in (h, lo, c, o))
    ph, pl = _pivots(hv, k, k, True), _pivots(lv, k, k, False)
    m = len(cv)
    last_ph, last_pl = np.full(m, np.nan), np.full(m, np.nan)
    a = b = np.nan
    for i in range(m):
        if ph[i]:
            a = hv[i - k]
        if pl[i]:
            b = lv[i - k]
        last_ph[i], last_pl[i] = a, b
    falling, rising = (r < r.shift(1)).to_numpy(), (r > r.shift(1)).to_numpy()
    rv, bv, gv = r.to_numpy(), body.to_numpy(), big.to_numpy()
    with np.errstate(invalid="ignore"):
        dip = ((rv < 35) & (bv >= gv * 1.0)) | ((rv < 30) & (bv >= gv * 0.8)) | \
              ((rv < 25) & (bv >= gv * 0.7)) | ((rv < 20) & (bv >= gv * 0.5))
        pop = ((rv > 65) & (bv >= gv * 1.0)) | ((rv > 70) & (bv >= gv * 0.8)) | \
              ((rv > 75) & (bv >= gv * 0.7)) | ((rv > 75) & (bv >= gv * 0.7))
        go_l = falling & dip & (cv < last_pl)
        go_s = rising & pop & (cv > last_ph)
    f = float(p["exit_frac"])
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend, avg, ref = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, avg = pend, ov[i]
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == 0:
            if go_l[i] and i + 1 < m:
                le[i], pend, ref = True, 1, last_pl[i]
            elif go_s[i] and i + 1 < m:
                se[i], pend, ref = True, -1, last_ph[i]
        elif pos == 1 and cv[i] > avg + (ref - avg) * f:
            lx[i], pend = True, 2
        elif pos == -1 and cv[i] < avg - (avg - ref) * f:
            sx[i], pend = True, 2
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
