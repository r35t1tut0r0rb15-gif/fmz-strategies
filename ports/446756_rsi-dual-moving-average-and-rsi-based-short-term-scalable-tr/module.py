"""SMA 5 / 10 crossings against RSI 7 extremes, 1-minute bars: a cross down with the RSI under 20 goes long, a cross up with the RSI over 80 goes short; reversing (the closes name ids that never exist and
never act).
Port of FMZ strategy #446756 "基于双均线和RSI的短线可扩展趋势追踪策略-Dual-Moving-Average-and-RSI-Based-Short-Term-Scalable-Trend-Following-Strategy" (Short-Term Scalp Trading Strategy).

FMZ source id: 446756

Source
    https://www.fmz.com/strategy/446756 (PineScript v5, FMZ last modified 2024-04-01 10:58:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-150), SMA 5 / 10; RSI 7, levels 20 / 80
    crossunder(fast, slow) and rsi < 20 -> entry Long;  crossover(fast, slow) and rsi > 80 -> entry Short;  exit tests -> strategy.close("Exit Long", "Long") / strategy.close("Exit Short", "Short")

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close's first argument is the entry id: "Exit Long" and "Exit Short" are never entered
      (the second argument is only the comment), so the closes never act and positions end at the
      opposite entry. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, contrarian SMA crossings at RSI extremes.
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

NAME = "fmz_446756_sma5_10_contrarian_cross_rsi7_extreme_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [7, 14],
    "oversold": [20.0, 30.0],
}
DEFAULT_PARAMS = {"rsi_len": 7, "oversold": 20.0, "overbought": 80.0, "fast": 5, "slow": 10}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (f < s) & (f.shift(1) >= s.shift(1)) & (r < float(p["oversold"]))
    se = (f > s) & (f.shift(1) <= s.shift(1)) & (r > float(p["overbought"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
