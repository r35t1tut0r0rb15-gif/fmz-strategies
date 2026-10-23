"""Broker days, long only: RSI 14 crossing over 30 on the same bar as the close crossing over the SMA 20 goes long; RSI crossing under 70 on the same bar as the close crossing under the SMA 20 closes it.
Port of FMZ strategy #442224 "Multi factor Intelligent Trading Strategy" (ProfitCraft Strategy (PRIDELEGENX005)).

FMZ source id: 442224

Source
    https://www.fmz.com/strategy/442224 (PineScript v5, FMZ last modified 2024-02-20 14:03:36).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 163-215), RSI 14, 30 / 70; Bollinger 20 x 2 (only the SMA is used)
    buy_condition = crossover(rsi, 30) and crossover(close, sma20) -> entry Buy
    sell_condition = crossunder(rsi, 70) and crossunder(close, sma20) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Bollinger bands, "VPVR", Fibonacci lines, manual ADX and VWAP are computed but feed no order:
      volume is not used (held for volume, not used). Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, simultaneous RSI and SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442224_rsi_and_sma20_joint_cross_long_only"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [30, 40],
    "overbought": [70, 60],
}
DEFAULT_PARAMS = {"length": 14, "oversold": 30, "overbought": 70, "bb_length": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["length"]))
    sma = c.rolling(int(p["bb_length"])).mean()
    os_, ob = float(p["oversold"]), float(p["overbought"])
    buy = ((r > os_) & (r.shift(1) <= os_) & (c > sma) & (c.shift(1) <= sma.shift(1))).to_numpy()
    sell = ((r < ob) & (r.shift(1) >= ob) & (c < sma) & (c.shift(1) >= sma.shift(1))).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
