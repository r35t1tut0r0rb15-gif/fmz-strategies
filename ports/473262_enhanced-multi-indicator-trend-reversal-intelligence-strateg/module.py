"""MACD 6 / 13 / 5 crossings with the EMA 20 / 50 trend and an RSI filter, daily bars: the MACD cross up with the EMA 20 over the EMA 50 and the RSI over 40 goes long, the mirror with the RSI under 60 goes short; reversing.
Port of FMZ strategy #473262 "Enhanced Multi Indicator Trend Reversal Intelligence Strategy" (Enhanced Trend Reversal Strategy with Take Profit).

FMZ source id: 473262

Source
    https://www.fmz.com/strategy/473262 (PineScript v5, FMZ last modified 2024-11-28 17:04:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-149), MACD 6 / 13 / 5; EMA 20 / 50; RSI 14, 40 / 60; take-profit level 1.5 % computed and plotted only
    crossover(macd, signal) and ema20 > ema50 and rsi > 40 -> entry Buy;  crossunder and ema20 < ema50 and rsi < 60 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The take-profit price is stored and plotted, but no exit order uses it. There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings with trend and RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473262_macd6_13_5_cross_ema20_50_rsi_filter_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    c = bars_df["close"]
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    macd = c.ewm(span=6, adjust=False).mean() - c.ewm(span=13, adjust=False).mean()
    sig = macd.ewm(span=5, adjust=False).mean()
    r = _rsi(c, 14)
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (e20 > e50) & (r > 40)
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (e20 < e50) & (r < 60)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
