"""A 1 % zigzag on the closes of RSI 5 crossings, 1-hour bars, long only: the zigzag of the last close at an RSI cross over 25 (highs) and the last close at an RSI cross under 75 (lows) turning up goes long,
turning down closes.
Port of FMZ strategy #442536 "基于RSI指标和ZigZag指标趋势追踪策略Trend-Tracking-Strategy-Based-on-RSI-and-ZigZag-Indicators" (Crypto ZigZag RSI strategy 15min).

FMZ source id: 442536

Source
    https://www.fmz.com/strategy/442536 (PineScript v4, FMZ last modified 2024-02-22 16:15:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-210), RSI 5 (25 / 75); minimum change 1 %; longa on, shorta off
    last_open_long = crossover(rsi, 25) ? close : nz(prev);  last_open_short = crossunder(rsi, 75) ? close : nz(prev);  r1 = last_open_long, s1 = last_open_short
    trend > 0: r1 >= HH -> HH = r1, else s1 < HH (1 - 1 %) -> trend = -1, LL = s1;  trend < 0: s1 <= LL -> LL = s1, else r1 > LL (1 + 1 %) -> trend = 1, HH = s1
    crossover(trend, 0) -> entry long;  crossunder(trend, 0) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zigzag runs on the two remembered closes, which start at 0 (nz), as written; HH restarts from
      s1 on an up turn, as written. The "Minimum % Change" table value true is the 1 default. The short
      side is off by default. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zigzag on RSI-cross closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND379760 (2 members, best partner #379760, Jaccard 0.701); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442536_rsi_cross_close_zigzag_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 14],
    "zz_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 5, "zz_pct": 1.0, "over_sold": 25, "over_bought": 75}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["length"]))
    os_, ob = float(p["over_sold"]), float(p["over_bought"])
    lg = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    sh = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    cv = c.to_numpy(dtype=float)
    pi = float(p["zz_pct"]) * 0.01
    m = len(cv)
    trend = np.zeros(m, dtype=np.int8)
    r1 = s1 = 0.0
    t, hh, ll = 1, np.nan, np.nan
    for i in range(m):
        if lg[i]:
            r1 = cv[i]
        if sh[i]:
            s1 = cv[i]
        if np.isnan(ll):
            ll = s1
        if np.isnan(hh):
            hh = r1
        if t > 0:
            if r1 >= hh:
                hh = r1
            elif s1 < hh * (1 - pi):
                t, ll = -1, s1
        else:
            if s1 <= ll:
                ll = s1
            elif r1 > ll * (1 + pi):
                t, hh = 1, s1
        trend[i] = t
    prev = np.concatenate(([1], trend[:-1]))
    le = (prev <= 0) & (trend > 0)
    lx = (prev >= 0) & (trend < 0)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
