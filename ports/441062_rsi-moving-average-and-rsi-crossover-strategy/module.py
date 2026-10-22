"""SMA 10 / 50 crossings with RSI filters, 1-minute bars, long only: the SMA 10 crossing over the SMA 50 with the RSI 14 under 50 goes long; the SMA 10 crossing under with the RSI over 70 closes.
Port of FMZ strategy #441062 "基于均线和RSI交叉策略Moving-Average-and-RSI-Crossover-Strategy" (MA_RSI_Strategy).

FMZ source id: 441062

Source
    https://www.fmz.com/strategy/441062 (PineScript v5, FMZ last modified 2024-02-05 11:52:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-197), SMA 10 / 50; RSI 14; overbought 70, "oversold" 50
    buy = crossover(fastMA, slowMA) and rsi < 50 -> entry Buy;  sell = crossunder(fastMA, slowMA) and rsi > 70 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit needs the RSI above 70 on the bar the fast SMA crosses under, as written. Long only. No
      sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441062_sma10_50_cross_rsi_filter_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "rsi_length": 14, "overbought": 70, "oversold": 50}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    up = (f > s) & (f.shift(1) <= s.shift(1)) & (r < float(p["oversold"]))
    dn = (f < s) & (f.shift(1) >= s.shift(1)) & (r > float(p["overbought"]))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
