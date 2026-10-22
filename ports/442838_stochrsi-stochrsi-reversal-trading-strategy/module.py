"""Stochastic RSI crossings at the extremes, daily bars: %K (SMA 3 of the stochastic of RSI 14) crossing over %D under 20 goes long, crossing under above 80 goes short; reversing.
Port of FMZ strategy #442838 "StochRSI反转交易策略StochRSI-Reversal-Trading-Strategy" (StochRSIStrategy).

FMZ source id: 442838

Source
    https://www.fmz.com/strategy/442838 (PineScript v4, FMZ last modified 2024-02-26 14:17:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-189), %K 3, %D 3; RSI 14; stochastic 14; levels 80 / 20
    bull = K < 20 and crossover(K, D) -> entry L, close S;  bear = K > 80 and crossunder(K, D) -> close L, entry S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes repeat the reversals. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ
      = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic RSI crossings.
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

NAME = "fmz_442838_stoch_rsi_extreme_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_length": [14, 7],
    "oversold": [20, 10],
}
DEFAULT_PARAMS = {"stoch_length": 14, "oversold": 20, "rsi_length": 14, "k": 3, "d": 3}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["stoch_length"])
    lo, hi = r.rolling(n).min(), r.rolling(n).max()
    st = 100.0 * (r - lo) / (hi - lo).where(hi > lo)
    k = st.rolling(int(p["k"])).mean()
    d = k.rolling(int(p["d"])).mean()
    os_ = float(p["oversold"])
    le = (k < os_) & (k > d) & (k.shift(1) <= d.shift(1))
    se = (k > 100.0 - os_) & (k < d) & (k.shift(1) >= d.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
