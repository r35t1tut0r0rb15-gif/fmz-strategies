"""RSI divergences with an Ichimoku / EMA 200 filter, 3-hour bars: a regular or hidden bullish RSI 14 divergence at a
confirmed pivot low (5 / 5), with the cloud top above the EMA 200, goes long; the bearish mirror with the cloud bottom
below the EMA 200 goes short; RSI crossing up through 75 closes a long, through 25 closes a short (as written).
Port of FMZ strategy #430850 "RSI敢死队融合策略RSI-Daredevil-Squadron-Fusion-Strategy" (RSI Divergence X Ichimoku Cloud X 200EMA).

FMZ source id: 430850

Source
    https://www.fmz.com/strategy/430850 (PineScript v4, FMZ last modified 2023-11-02 14:52:03).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 177-272), RSI 14, pivots 5 / 5, range 5-60 bars, take profit RSI 75 / 25, Ichimoku 9 / 26 / 52, EMA 200
    bull = low[5] < low at the previous pivot low and rsi[5] > rsi there, in range, at a pivot low of rsi
    hidden bull = low[5] > previous and rsi[5] < previous;  bear / hidden bear mirrored at pivot highs
    long = (bull or hidden bull) and max(lead1, lead2) > ema200;  short = (bear or hidden bear) and ema200 > min(lead1, lead2)
    crossover(rsi, 75) -> close long;  crossover(rsi, 25) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivotlow / pivothigh(rsi, 5, 5): the value 5 bars back strictly below (above) the 5 before and the
      5 after (ties are not pivots), known 5 bars later. "In range" is 5 to 60 bars since the bar after
      the previous pivot. The cloud lines are the current (undisplaced) lead lines, as written.
    * The short close tests a cross UP through 25, as written. Closes act on the position held at the
      start of the bar unless the bar's entry reverses it.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed after their right bars.
    2 generic: PASS, RSI divergences, channel midpoints and an EMA.
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

NAME = "fmz_430850_rsi_divergence_cloud_ema200"
FAMILY = "macd_divergence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lb": [5, 3],
    "tp_long": [75, 70],
}
DEFAULT_PARAMS = {"rsi_len": 14, "lb": 5, "tp_long": 75, "tp_short": 25, "range_lower": 5, "range_upper": 60}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _pivots(x, lb, rb, high):
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        if np.isnan(v):
            continue
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        out[t] = (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())
    return out


def _div(found, osc, price, rb, lo_rng, hi_rng, bullish):
    """Regular and hidden divergence flags at confirmed pivots, as the source's valuewhen(found, x[rb], 1)."""
    m = len(osc)
    reg, hid = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    prev_o = prev_p = np.nan
    last_cond = -1
    for t in range(m):
        if t >= 1 and found[t - 1]:
            last_cond = t
        if found[t]:
            o_now, p_now = osc[t - rb], price[t - rb]
            bars = t - last_cond if last_cond >= 0 else np.inf
            ok = lo_rng <= bars <= hi_rng
            if ok and not np.isnan(prev_o):
                if bullish:
                    reg[t] = p_now < prev_p and o_now > prev_o
                    hid[t] = p_now > prev_p and o_now < prev_o
                else:
                    reg[t] = p_now > prev_p and o_now < prev_o
                    hid[t] = p_now < prev_p and o_now > prev_o
            prev_o, prev_p = o_now, p_now
    return reg | hid


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
    osc = _rsi(c, int(p["rsi_len"]))
    ov = osc.to_numpy(dtype=float)
    lb = int(p["lb"])
    pl, ph = _pivots(ov, lb, lb, False), _pivots(ov, lb, lb, True)
    lo_r, hi_r = int(p["range_lower"]), int(p["range_upper"])
    bull = _div(pl, ov, lo.to_numpy(dtype=float), lb, lo_r, hi_r, True)
    bear = _div(ph, ov, h.to_numpy(dtype=float), lb, lo_r, hi_r, False)
    mid = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    lead1 = (mid(9) + mid(26)) / 2
    lead2 = mid(52)
    ema200 = c.ewm(span=200, adjust=False).mean()
    above = (np.maximum(lead1, lead2) > ema200).to_numpy()
    below = (ema200 > np.minimum(lead1, lead2)).to_numpy()
    le, se = bull & above, bear & below
    xl = ((osc > p["tp_long"]) & (osc.shift(1) <= p["tp_long"])).to_numpy()
    xs = ((osc > p["tp_short"]) & (osc.shift(1) <= p["tp_short"])).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if le[i]:
            pos = 1
        if start == 1 and pos == 1 and xl[i]:
            pos = 0
        if se[i]:
            pos = -1
        if start == -1 and pos == -1 and xs[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
