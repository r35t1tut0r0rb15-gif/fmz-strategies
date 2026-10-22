"""Closes beyond 15-bar linear-regression lines of highs and lows with an RSI 14 filter, daily bars: a close over the regression of highs with RSI over 50 goes long, under the regression of lows with RSI under 50 goes short; reversing.
Port of FMZ strategy #474049 "三角形突破结合RSI动量策略-Triangle-Breakout-with-RSI-Momentum-Strategy" (Triangle Breakout with RSI).

FMZ source id: 474049

Source
    https://www.fmz.com/strategy/474049 (PineScript v5, FMZ last modified 2024-12-05 16:19:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 82-128), triangle length 15; RSI 14, 50 / 50
    close > linreg(high, 15, 0) and rsi > 50 -> entry Buy;  close < linreg(low, 15, 0) and rsi < 50 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg(src, 15, 0) is the least-squares line over the last 15 bars at the current bar. Entries
      repeat while the tests hold (ignored while held). The highest / lowest levels feed no order. There
      is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression-line breakouts with an RSI filter.
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

NAME = "fmz_474049_linreg15_high_low_break_rsi50_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [15, 30],
    "rsi_buy": [50, 60],
}
DEFAULT_PARAMS = {"len": 15, "rsi_buy": 50, "rsi_sell": 50}


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


def _linreg_end(y, n):
    """ta.linreg(y, n, 0): the least-squares line over the last n bars, at the current bar."""
    x = np.arange(n, dtype=float)
    xm = x.mean()
    sxx = ((x - xm) ** 2).sum()

    def f(v):
        b = np.dot(x - xm, v - v.mean()) / sxx
        return v.mean() + b * (n - 1 - xm)

    return y.rolling(n).apply(f, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len"])
    r = _rsi(c, 14)
    le = (c > _linreg_end(h, n)) & (r > float(p["rsi_buy"]))
    se = (c < _linreg_end(lo, n)) & (r < float(p["rsi_sell"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
