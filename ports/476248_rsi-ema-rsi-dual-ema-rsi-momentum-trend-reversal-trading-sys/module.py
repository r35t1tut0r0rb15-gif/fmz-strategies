"""EMA 9 / 21 crossings with RSI 14 on the 50 side, hourly bars, long only: the cross up with RSI over 50 buys, the cross down with RSI under 50 closes. The 1 % / 2 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #476248 "双均线RSI趋势反转交易策略-基于EMA和RSI的动量突破系统-Dual-EMA-RSI-Momentum-Trend-Reversal-Trading-System-A-Momentum-Breakthrough-Strategy-Based-on-EMA-and-RSI-Crossover" (EMA Crossover with RSI Confirmation and Buy/Sell Signals).

FMZ source id: 476248

Source
    https://www.fmz.com/strategy/476248 (PineScript v5, FMZ last modified 2024-12-27 14:23:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 82-138), EMA 9 / 21; RSI 14, level 50; stop 1 %, target 2 % of the current close
    crossover(ema9, ema21) and rsi > 50 -> entry Buy;  crossunder(ema9, ema21) and rsi < 50 -> close Buy;  every bar: exit(from Buy, stop = close x (1 - 1 / 100), limit = close x (1 + 2 / 100))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so its levels move after entry: stops()
      cannot express a level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, EMA crossings with an RSI 50 filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_476248_ema9_21_cross_rsi50_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_length": 14, "rsi_level": 50}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    lvl = float(p["rsi_level"])
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r > lvl)
    lx = (f < s) & (f.shift(1) >= s.shift(1)) & (r < lvl)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
