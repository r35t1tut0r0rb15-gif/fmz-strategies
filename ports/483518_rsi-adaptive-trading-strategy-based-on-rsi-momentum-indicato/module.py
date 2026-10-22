"""RSI 14 states beyond 30 / 70, broker days: RSI at or under 30 goes long, at or over 70 goes short; reversing (the per-bar 0.2 % / 0.6 % bracket from the current close is pending).
Port of FMZ strategy #483518 "基于RSI动量指标的自适应交易策略-Adaptive-Trading-Strategy-Based-on-RSI-Momentum-Indicator" (MultiSymbol Smart Money EA without Lot Sizes or Pairs).

FMZ source id: 483518

Source
    https://www.fmz.com/strategy/483518 (PineScript v5, FMZ last modified 2025-02-27 16:47:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-133), RSI 14 / 70 / 30; stop 0.2 %; target 0.6 %
    rsi <= 30 -> entry Buy;  rsi >= 70 -> entry Sell
    long -> exit(stop = close x 0.998, limit = close x 1.006) re-sent every bar from the current close;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close (longPrice = close), so its levels follow
      the price: not ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite entry is
      the exit. The entries are states; a repeat on the side held adds nothing, the other side reverses
      (REVERSAL INTENDED). No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent close bracket pending.
    2 generic: PASS, RSI extreme states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483518_rsi14_30_70_state_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [14, 7],
    "rsi_oversold": [30.0, 20.0],
}
DEFAULT_PARAMS = {"rsi_period": 14, "rsi_oversold": 30.0}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_period"]))
    os_ = float(p["rsi_oversold"])
    le = r <= os_
    se = r >= 100 - os_
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
