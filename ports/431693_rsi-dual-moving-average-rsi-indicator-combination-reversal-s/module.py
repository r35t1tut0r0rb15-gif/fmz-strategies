"""Quiet-market band fades (Senpai), 1-hour bars: with ADX 30 under 18.5, a bar touching the lower Bollinger band (50, 0.5)
with RSI 14 at or under 30 and the PSAR above the close starts a long (mirror short at the upper band); each position is
closed three bars after its signal.
Port of FMZ strategy #431693 "双均线RSI指标组合反转策略Dual-Moving-Average-RSI-Indicator-Combination-Reversal-Strategy" (Senpai_Strat_3).

FMZ source id: 431693

Source
    https://www.fmz.com/strategy/431693 (PineScript v2, FMZ last modified 2023-11-10 18:01:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 185-264), PSAR 0.02 / 0.02 / 0.2, ADX 30 / DI 30 under 18.5, BB 50 / 0.5, RSI 14
    long1 = adx < 18.5 and low <= lower and rsi <= 30 and psar > close;  short1 = adx < 18.5 and high >= upper and rsi >= 70 and psar < close
    long = long1 newly true -> entry long;  short = short1 newly true -> entry short (qty 10)
    long[3] -> close long;  short[3] -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the RSI's zero case tests the DI "up" series (up == 0) instead of up1; ADX, PSAR
      (TradingView's ta.sar) and the RSI are otherwise Pine's. The %B impulse lines are unused.
    * Order of the source: entry short, entry long, close long, close short; a close acts on the
      position held at the bar's start and does not undo a reversal. strategy.entry reverses:
      REVERSAL INTENDED. stdev is the population deviation. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a three-bar exit.
    2 generic: PASS, ADX, Bollinger bands, RSI and PSAR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 10 per entry stored in original_sizing.txt.
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

NAME = "fmz_431693_senpai_quiet_band_fade"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_max": [18.5, 25.0],
    "hold": [3, 6],
}
DEFAULT_PARAMS = {"adx_max": 18.5, "hold": 3, "adx_len": 30, "di_len": 30, "length": 50, "mult": 0.5,
                  "ps_start": 0.02, "ps_inc": 0.02, "ps_max": 0.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _fixnan(x):
    """Pine fixnan: an indicator value that is na keeps the last valid value (no bars are filled)."""
    v = x.to_numpy(dtype=float).copy()
    for i in range(1, len(v)):
        if np.isnan(v[i]):
            v[i] = v[i - 1]
    return pd.Series(v, index=x.index)


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


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
    up, down = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    dl = int(p["di_len"])
    trr = _rma(tr, dl)
    pdm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    mdm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=h.index).where(down.notna())
    plus = _fixnan(100 * _rma(pdm, dl) / trr)
    minus = _fixnan(100 * _rma(mdm, dl) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), int(p["adx_len"]))
    ch = c.diff()
    u1 = _rma(ch.clip(lower=0), 14)
    d1 = _rma((-ch).clip(lower=0), 14)
    rsi = (100 - 100 / (1 + u1 / d1)).where(plus != 0, 0.0).where(d1 != 0, 100.0)
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + p["mult"] * sd, basis - p["mult"] * sd
    ps = _sar_pine(bars_df, float(p["ps_start"]), float(p["ps_inc"]), float(p["ps_max"]))
    q = adx < float(p["adx_max"])
    l1 = (q & (lo <= lower) & (rsi <= 30) & (ps > c)).to_numpy()
    s1 = (q & (h >= upper) & (rsi >= 70) & (ps < c)).to_numpy()
    m = len(l1)
    lg = np.zeros(m, dtype=bool)
    sh = np.zeros(m, dtype=bool)
    lg[1:] = l1[1:] & ~l1[:-1]
    sh[1:] = s1[1:] & ~s1[:-1]
    k = int(p["hold"])
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if sh[i]:
            pos = -1
        if lg[i]:
            pos = 1
        if i >= k and lg[i - k] and start == 1 and pos == 1:
            pos = 0
        if i >= k and sh[i - k] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
