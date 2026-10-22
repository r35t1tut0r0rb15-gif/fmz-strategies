"""A two-bar ATR(5) x 3.5 trail line, daily bars: the close crossing over the line goes long, under goes short; the Fibonacci targets only plot; reversing.
Port of FMZ strategy #443034 "基于ATR和斐波那契回撤止损的趋势跟踪策略ATR-Trailing-Stop-Strategy-with-Fibonacci-Retracement-Targets" (ATR TrailStop with Fib Targets).

FMZ source id: 443034

Source
    https://www.fmz.com/strategy/443034 (PineScript v5, FMZ last modified 2024-02-28 17:09:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-141), ATR 5 x 3.5; Fib levels 61.8 / 78.6 / 88.6 (plots only)
    trendUp = close[1] > close[2] ? max(close - loss, close[1]) : close - loss;  trendDown = close[1] < close[2] ? min(close + loss, close[1]) : close + loss;  trend = sign(close - close[2])
    trailStop = trend == 1 ? trendUp : trendDown;  close > trailStop and close[1] <= trailStop -> entry Long;  close < trailStop and close[1] >= trailStop -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is rebuilt each bar from the last two closes (no recursion), and the crossing compares
      the previous close with the current line, as written. The Fibonacci levels only plot.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs ATR trail line crossings.
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

NAME = "fmz_443034_two_bar_atr_trail_line_cross_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [5, 14],
    "atr_factor": [3.5, 2.0],
}
DEFAULT_PARAMS = {"atr_period": 5, "atr_factor": 3.5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    loss = float(p["atr_factor"]) * _rma(tr, int(p["atr_period"]))
    c1, c2 = c.shift(1), c.shift(2)
    tu = pd.Series(np.where(c1 > c2, np.where(c - loss > c1, c - loss, c1), c - loss), index=c.index)
    td = pd.Series(np.where(c1 < c2, np.where(c + loss < c1, c + loss, c1), c + loss), index=c.index)
    trend = np.where(c > c2, 1, np.where(c < c2, -1, 0))
    ts = pd.Series(np.where(trend == 1, tu, td), index=c.index).where(loss.notna())
    le = (c > ts) & (c1 <= ts)
    se = (c < ts) & (c1 >= ts)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
