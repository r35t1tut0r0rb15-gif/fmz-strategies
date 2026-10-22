"""Stochastic RSI (14 / 14, K 3, D 3) cross-ups under 20 in an SMA 21 > 55 up-trend, broker days, long only: such a cross buys; a K cross-down over 80 closes.
Port of FMZ strategy #481352 "双均线交叉与随机RSI超买超卖区间优化交易策略-Dual-Moving-Average-Crossover-with-Stochastic-RSI-Overbought-Oversold-Enhanced-Trading-Strategy" (SMA & Stoch RSI Buy Strategy with K > 80 Exit).

FMZ source id: 481352

Source
    https://www.fmz.com/strategy/481352 (PineScript v6, FMZ last modified 2025-02-10 14:40:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-143), SMA 21 / 55; Stoch RSI 14, K 3, D 3; 20 / 80
    sma21 > sma55 and crossover(k, d) and k < 20 -> entry Buy;  crossunder(k, d) and k > 80 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * A zero stochastic range gives na (no signal). Long only. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Stochastic RSI crossings in an SMA up-trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481352_stochrsi_cross_under20_sma21_55_trend_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_len": [14, 21],
    "fast_sma": [21, 50],
}
DEFAULT_PARAMS = {"stoch_len": 14, "fast_sma": 21, "slow_sma": 55, "k_smooth": 3, "d_smooth": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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
    n = int(p["stoch_len"])
    r = _rsi(c, n)
    rl, rh = r.rolling(n).min(), r.rolling(n).max()
    st = 100 * (r - rl) / (rh - rl).where(rh > rl)
    k = st.rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    trend = c.rolling(int(p["fast_sma"])).mean() > c.rolling(int(p["slow_sma"])).mean()
    le = trend & (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20)
    lx = (k < d) & (k.shift(1) >= d.shift(1)) & (k > 80)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
