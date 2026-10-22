"""EMA 9 / 21 crossings with RSI 14, 3-hour bars: the up-cross with RSI over 30 goes long, the down-cross with RSI under 30 goes short; the long closes on a down-cross or RSI under 30, the short on an up-cross or RSI over 30; reversing.
Port of FMZ strategy #488276 "双指数移动平均线交叉与RSI趋势确认策略-Dual-EMA-Crossover-with-RSI-Trend-Confirmation-Strategy" (vefaema).

FMZ source id: 488276

Source
    https://www.fmz.com/strategy/488276 (PineScript v5, FMZ last modified 2025-03-26 14:44:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-158), EMA 9 / 21; RSI 14 / 30
    crossover(ema9, ema21) and rsi > 30 -> entry Long;  crossunder(ema9, ema21) and rsi < 30 -> entry Short
    crossunder or rsi < 30 -> close Long;  crossover or rsi > 30 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, a short is closed on the first bar its RSI is back over 30. A short entry also meets the
      long exit, so it reverses (REVERSAL INTENDED). No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an RSI filter and exits.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_488276_ema9_21_cross_rsi30_filter_exits_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_length": 14, "rsi_level": 30}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    lv = float(p["rsi_level"])
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    le, se = up & (r > lv), dn & (r < lv)
    lx = (dn | (r < lv)) & ~se
    sx = (up | (r > lv)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
