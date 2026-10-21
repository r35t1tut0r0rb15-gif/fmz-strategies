"""Stochastic RSI crossings up through 20, broker days, long only: the Stochastic RSI 14 crossing over 20 buys. The bracket at the signal bar's low / high is sent only on a later cross down through 80 and is
not ported (pending), so the port has no exit.
Port of FMZ strategy #438950 "移动平均线与随机RSI组合交易策略Moving-Average-and-Stochastic-RSI-Combination-Trading-Strategy" (MA+Stoch RSI).

FMZ source id: 438950

Source
    https://www.fmz.com/strategy/438950 (PineScript v5, FMZ last modified 2024-01-16 15:46:11).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 172-211), MA 20 / 50 (unused); Stochastic RSI 14, levels 80 / 20; risk 2 % (sizing)
    stoch = (rsi - lowest(rsi, 14)) / (highest(rsi, 14) - lowest(rsi, 14)) x 100;  crossover(stoch, 20) -> stopLoss := low, takeProfit := high, entry Buy
    else crossunder(stoch, 80) -> exit(from Buy, stop = stopLoss, limit = takeProfit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent only on a later sell signal, with levels from the buy signal bar's low and high,
      so the bracket starts after entry: stops() cannot express it, so it is not ported (as #435169) and
      the module gets the mark trailing_stop_pending (the intended bracket is owed). Without it the port
      has no exit. The moving averages are not used by any order. Long only. The risk-based size is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket not ported (mark).
    2 generic: PASS, Stochastic RSI crossing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG438950 (2 members, best partner #440699, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_438950_stoch_rsi_cross_up_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_length": [14, 7],
    "oversold": [20, 30],
}
DEFAULT_PARAMS = {"stoch_length": 14, "oversold": 20.0}


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
    n = int(p["stoch_length"])
    r = _rsi(c, n)
    rh, rl = r.rolling(n).max(), r.rolling(n).min()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = (r - rl) / (rh - rl) * 100
    os_ = float(p["oversold"])
    up = (st > os_) & (st.shift(1) <= os_)
    false = pd.Series(False, index=c.index)
    return up, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
