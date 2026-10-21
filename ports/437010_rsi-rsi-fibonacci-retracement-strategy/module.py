"""RSI of hl2 against a Fibonacci level, broker days: the 14-bar RSI of hl2 at or above 38.2 is long, below is short; always in the market, reversing.
Port of FMZ strategy #437010 "RSI菲波那契回调策略RSI-Fibonacci-Retracement-Strategy" (RSI Fibonacci Levels).

FMZ source id: 437010

Source
    https://www.fmz.com/strategy/437010 (PineScript v4, FMZ last modified 2023-12-29 14:51:43).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-170), RSI 14 of hl2 (rma), Fibonacci level 38.2 (options 50, 61.8); backtest range 2010-2020 (not used by the orders)
    rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down) of hl2;  entry LE when rsi >= 38.2;  entry SE when rsi < 38.2

Interpretation choices (Pine rules in SURVEY_README.md)
    * The From / To inputs are never applied to the orders: dropped. The state is a level, so the entry is
      sent on every bar of the state; a same-side entry while in the position is ignored (pyramiding 0).
      REVERSAL INTENDED. The 100 % of equity size and commission are sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437010_rsi_hl2_fib_level_state"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "fib_level": [38.2, 50.0],
}
DEFAULT_PARAMS = {"length": 14, "fib_level": 38.2}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = (bars_df["high"] + bars_df["low"]) / 2
    d = src.diff()
    n = int(p["length"])
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    fi = float(p["fib_level"])
    false = pd.Series(False, index=bars_df.index)
    return r >= fi, false, r < fi, false.copy()


def portfolio_kwargs(**params):
    return {}
