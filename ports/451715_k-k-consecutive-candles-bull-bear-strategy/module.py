"""Runs of rising or falling closes, 1-hour bars: 3 closes in a row over the previous close go long and 3 under go short, each with a 500-tick stop and target (0.333 ATR); a long that has run 200 ticks (0.133 ATR) past its fill closes on a close back under the halfway point between the fill and its highest high; reversing.
Port of FMZ strategy #451715 "K线连续数目牛熊判断策略-K-Consecutive-Candles-Bull-Bear-Strategy" (K Consecutive Candles 數來寶V2).

FMZ source id: 451715

Source
    https://www.fmz.com/strategy/451715 (PineScript v5, FMZ last modified 2024-05-17 13:54:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-162), k 3 / 3; stop / target 500 ticks; trail start iTGT 200 ticks, give-back iPcnt 50 %
    countLong >= 3 -> entry Long Entry, exit(loss = 500, profit = 500);  countShort >= 3 -> entry Short Entry, exit(loss = 500, profit = 500)
    long: trail = highest(high, barssince(flat));  trail > avg + 200 ticks and close < trail - 50 % x (trail - avg) -> close Long Entry
    short: the mirror test closes 'short60', an id never entered

Interpretation choices (Pine rules in SURVEY_README.md)
    * The tick distances are 50 and 20 at the 0.1 tick, ported as ATR multiples at the 1-hour reading
      (~150): 0.333 ATR 14 for the stop and target (read from the bar before the fill) and 0.133 ATR
      for the trail start. The long's give-back exit is a bar-close test, followed in a loop that
      tracks the bracket on each bar's high / low: the highest high runs from the bar after the last
      flat bar close (barssince(position_size == 0)), the fill price is the fill bar's open. The
      short's give-back close names 'short60', never entered, so it never acts: shorts end at their
      bracket or the opposite entry. An entry on the held side is ignored; an opposite run reverses.
      The alert-string helper is unused. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples; the long give-back exit in a loop.
    2 generic: PASS, consecutive-close runs with a profit give-back exit.
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

NAME = "fmz_451715_consecutive_close_runs_atr_bracket_giveback_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k": [3, 5],
    "k_atr": [0.333, 1.0],
}
DEFAULT_PARAMS = {"k": 3, "k_atr": 0.333, "tgt_atr": 0.133, "pcnt": 50.0, "atr_len": 14}


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


def _atr_frac(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n)) / c


def _runs(c, k):
    v = c.to_numpy(dtype=float)
    m = len(v)
    cl, cs = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    nl = ns = 0
    for i in range(1, m):
        if v[i] > v[i - 1]:
            nl, ns = nl + 1, 0
        elif v[i] < v[i - 1]:
            nl, ns = 0, ns + 1
        else:
            nl = ns = 0
        cl[i], cs[i] = nl >= k, ns >= k
    return cl, cs


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o = bars_df["open"].to_numpy(dtype=float)
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    c = bars_df["close"].to_numpy(dtype=float)
    cl, cs = _runs(bars_df["close"], int(p["k"]))
    fr = _atr_frac(bars_df, p["atr_len"]).to_numpy()
    ka, kt, give = float(p["k_atr"]), float(p["tgt_atr"]), float(p["pcnt"]) / 100
    m = len(c)
    lx = np.zeros(m, dtype=bool)
    pos, pend, avg, frac, last_flat = 0, 0, np.nan, np.nan, 0
    for i in range(m):
        if pend in (1, -1):
            pos, avg = pend, o[i]
            frac = fr[i - 1] if i > 0 else np.nan
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == 1 and (lo[i] <= avg * (1 - ka * frac) or h[i] >= avg * (1 + ka * frac)):
            pos = 0
        elif pos == -1 and (h[i] >= avg * (1 + ka * frac) or lo[i] <= avg * (1 - ka * frac)):
            pos = 0
        if pos == 0:
            last_flat = i
        cur = pos
        if cl[i] and cur != 1:
            cur = 1
        if pos == 1:
            trail = h[last_flat + 1:i + 1].max()
            if trail > avg * (1 + kt * frac) and c[i] < trail - give * (trail - avg):
                lx[i], cur = True, 0
        if cs[i] and cur != -1:
            cur = -1
        if cur != pos:
            pend = 2 if cur == 0 else cur
    ix = bars_df.index
    le, se = pd.Series(cl, index=ix), pd.Series(cs, index=ix)
    lxs = pd.Series(lx, index=ix)
    false = pd.Series(False, index=ix)
    return le & ~lxs, lxs & ~se, se, false


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["k_atr"]) * _atr_frac(bars_df, p["atr_len"])
    return {"sl_stop": a.shift(1), "tp_stop": a.shift(1)}


def portfolio_kwargs(**params):
    return {}
