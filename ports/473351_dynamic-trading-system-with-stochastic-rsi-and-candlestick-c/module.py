"""Stochastic RSI (14, 14, K 3) level crossings with candle colour, daily bars: K crossing over 20 on a white candle goes long, under 80 on a black candle goes short; K crossing under 80 closes a long, over 20 closes a short; reversing.
Port of FMZ strategy #473351 "Dynamic Trading System with Stochastic RSI and Candlestick Confirmation" (Stochastic RSI Strategy with Candlestick Confirmation).

FMZ source id: 473351

Source
    https://www.fmz.com/strategy/473351 (PineScript v5, FMZ last modified 2024-11-29 14:58:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-159), RSI 14, stoch 14, K 3 (D unused); levels 20 / 80
    crossover(k, 20) and close > open -> entry Long;  crossunder(k, 80) and close < open -> entry Short;  crossunder(k, 80) -> close Long;  crossover(k, 20) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close coinciding with the opposite entry only repeats the reversal (#437773), so the closes
      are masked on entry bars. The level crossings up and down cannot hold on one bar. REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Stochastic RSI level crossings with candle filters.
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

NAME = "fmz_473351_stochrsi_k_20_80_cross_candle_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [20, 30],
    "overbought": [80, 70],
}
DEFAULT_PARAMS = {"oversold": 20, "overbought": 80, "rsi_len": 14, "stoch_len": 14, "k_len": 3}


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
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    lo_, hi_ = r.rolling(n).min(), r.rolling(n).max()
    k = (100 * (r - lo_) / (hi_ - lo_)).rolling(int(p["k_len"])).mean()
    os_, ob = float(p["oversold"]), float(p["overbought"])
    up = (k > os_) & (k.shift(1) <= os_)
    dn = (k < ob) & (k.shift(1) >= ob)
    le = up & (c > o)
    se = dn & (c < o)
    lx = dn & ~se
    sx = up & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
