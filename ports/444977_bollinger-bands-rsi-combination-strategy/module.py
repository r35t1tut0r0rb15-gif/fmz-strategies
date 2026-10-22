"""Bollinger band re-entries confirmed by the RSI, daily bars: the close crossing back over the lower band (20, 2) with the RSI 14 under 30 goes long, crossing back under the upper band with the RSI over 70
goes short; reversing.
Port of FMZ strategy #444977 "Bollinger Bands RSI Combination Strategy" (Bollinger Bands & RSI Strategy).

FMZ source id: 444977

Source
    https://www.fmz.com/strategy/444977 (PineScript v5, FMZ last modified 2024-03-15 16:28:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-154), BB 20 / 2 on close; RSI 14, levels 30 / 70
    crossover(close, lower) and rsi < 30 -> entry BBandLE, else cancel;  crossunder(close, upper) and rsi > 70 -> entry BBandSE, else cancel

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are market orders filled at the next open, before the next bar's cancel can reach
      them, so the cancels never act. Pine's stdev is the population deviation. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-entry crossings with RSI levels.
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

NAME = "fmz_444977_band_reentry_rsi_extreme_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"length": 20, "rsi_length": 14, "mult": 2.0, "os": 30.0, "ob": 70.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    lower, upper = basis - dev, basis + dev
    r = _rsi(c, int(p["rsi_length"]))
    c1 = c.shift(1)
    le = (c > lower) & (c1 <= lower.shift(1)) & (r < float(p["os"]))
    se = (c < upper) & (c1 >= upper.shift(1)) & (r > float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
