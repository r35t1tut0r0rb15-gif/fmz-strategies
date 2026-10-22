"""EMA 50 / 200 crossings with an ATR filter, daily bars: the cross up with ATR 14 over 0.02 % of the close goes long, the cross down with it goes short; every cross down closes a long and every cross up closes a short; reversing.
Port of FMZ strategy #473387 "高级双均线策略与ATR波动率过滤系统-Advanced-Dual-EMA-Strategy-with-ATR-Volatility-Filter-System" (EMA Crossover with ATR Filter).

FMZ source id: 473387

Source
    https://www.fmz.com/strategy/473387 (PineScript v5, FMZ last modified 2024-11-29 16:14:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-143), EMA 50 / 200; ATR 14, threshold 0.02 % of the close; 10 % of equity
    crossover and atr / close > 0.0002 -> entry Long;  crossunder and filter -> entry Short;  crossunder -> close Long;  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close coinciding with the opposite entry only repeats the reversal (#437773), so the closes
      are masked on entry bars; a cross without the filter only closes. The ATR multiplier input feeds
      nothing. REVERSAL INTENDED. The equity share is not ported. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an ATR filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473387_ema50_200_cross_atr_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
    "atr_threshold": [0.02, 2.0],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "atr_threshold": 0.02, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1))
    f = _atr(bars_df, p["atr_len"]) / c > float(p["atr_threshold"]) / 100
    le, se = up & f, dn & f
    return le, dn & ~se, se, up & ~le


def portfolio_kwargs(**params):
    return {}
