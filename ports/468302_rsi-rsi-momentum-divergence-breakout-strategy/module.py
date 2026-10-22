"""RSI 14 extremes with 3-bar divergences, daily bars: an RSI under 30 with a lower 3-bar closing low but a higher 3-bar RSI low goes long, an RSI over 70 with the mirror divergence goes short; reversing. The 50 / 20-point bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #468302 "RSI动量背离突破策略-RSI-Momentum-Divergence-Breakout-Strategy" (RSI + RSI Divergence Strategy).

FMZ source id: 468302

Source
    https://www.fmz.com/strategy/468302 (PineScript v5, FMZ last modified 2024-09-26 14:37:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 238-286), RSI 14, levels 30 / 70 (constants); divergence: lowest(close, 3) vs lowest(close[1], 3)[1], the same for the RSI; target 50, stop 20 points from the current close
    rsi < 30 and lowest(close, 3) < lowest(close[1], 3)[1] and lowest(rsi, 3) > lowest(rsi[1], 3)[1] -> entry Long;  the mirror with highest and rsi > 70 -> entry Short
    every bar: exit(Long, limit = close + 50, stop = close - 20);  exit(Short, limit = close - 50, stop = close + 20)

Interpretation choices (Pine rules in SURVEY_README.md)
    * lowest(x[1], 3)[1] is the lowest of the values 2 to 4 bars back. The bracket is re-sent on every
      bar from that bar's close, so its levels move after entry: stops() cannot express a level re-set
      every bar, so it is described here and kept pending (as #438034, mark trailing_stop_pending).
      Positions end at the opposite entry until then. REVERSAL INTENDED. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes with short divergences; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point bracket stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_468302_rsi_extreme_three_bar_divergence_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "window": [3, 5],
}
DEFAULT_PARAMS = {"rsi_len": 14, "window": 3}


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
    r = _rsi(c, int(p["rsi_len"]))
    w = int(p["window"])
    bull = (c.rolling(w).min() < c.shift(2).rolling(w).min()) & (r.rolling(w).min() > r.shift(2).rolling(w).min())
    bear = (c.rolling(w).max() > c.shift(2).rolling(w).max()) & (r.rolling(w).max() < r.shift(2).rolling(w).max())
    le = (r < 30) & bull
    se = (r > 70) & bear
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
