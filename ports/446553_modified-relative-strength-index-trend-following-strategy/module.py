"""RSI 14 of the EMA 13 crossing its EMA 5, daily bars: crossing up goes long, crossing down goes short; reversing.
Port of FMZ strategy #446553 "Modified Relative Strength Index Trend Following Strategy" (Modified RSI).

FMZ source id: 446553

Source
    https://www.fmz.com/strategy/446553 (PineScript v5, FMZ last modified 2024-03-29 16:16:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-178), price EMA 13; RSI 14 of it; RSI EMA 5; EMA 20 / 50 (unused)
    modrsi = rsi(ema(close, 13), 14);  avg = ema(modrsi, 5);  crossover(modrsi, avg) and modrsi - avg > 0 -> entry B;  crossunder and < 0 -> entry S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The histogram tests repeat the crossings. The EMA 20 / 50 are computed and not used. No exit:
      positions end at the opposite entry. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed-RSI signal crossings.
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

NAME = "fmz_446553_rsi_of_ema13_signal_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [13, 5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"ema_len": 13, "rsi_len": 14, "avg_len": 5}


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
    r = _rsi(c.ewm(span=int(p["ema_len"]), adjust=False).mean(), int(p["rsi_len"]))
    a = r.ewm(span=int(p["avg_len"]), adjust=False).mean()
    le = (r > a) & (r.shift(1) <= a.shift(1))
    se = (r < a) & (r.shift(1) >= a.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
