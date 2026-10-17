"""EMA 9 / 21 crosses with RSI 30 tests, 3-hour bars: EMA 9 crossing above EMA 21 with RSI 14 above 30 goes long; EMA 9
crossing below EMA 21 with RSI below 30 goes short; a long closes on a cross down or RSI below 30, a short on a cross
up or RSI above 30.
Port of FMZ strategy #488276 "双指数移动平均线交叉与RSI趋势确认策略-Dual-EMA-Crossover-with-RSI-Trend-Confirmation-Strategy" (vefaema).

FMZ source id: 488276

Source
    https://www.fmz.com/strategy/488276 (PineScript v5, FMZ last modified 2025-03-26 14:44:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 120-157), EMA 9 / 21, RSI 14, level 30
    long = crossover(ema9, ema21) and rsi > 30 -> entry long;  short = crossunder(ema9, ema21) and rsi < 30 -> entry short
    crossunder(ema9, ema21) or rsi < 30 -> close long;  crossover(ema9, ema21) or rsi > 30 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850): a short signal
      while long reverses. REVERSAL INTENDED. As written a short closes on the first bar whose RSI is back above 30.
    * FREQ = "3h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and an oscillator.
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

NAME = "fmz_488276_ema9_21_cross_rsi30"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_slow": [21, 30],
    "rsi_level": [30, 40],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_slow": 21, "rsi_len": 14, "rsi_level": 30}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    lvl = p["rsi_level"]
    x_up = (f > s) & (f.shift(1) <= s.shift(1))
    x_dn = (f < s) & (f.shift(1) >= s.shift(1))
    go_l, go_s = (x_up & (rsi > lvl)).to_numpy(), (x_dn & (rsi < lvl)).to_numpy()
    out_l, out_s = (x_dn | (rsi < lvl)).to_numpy(), (x_up | (rsi > lvl)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
