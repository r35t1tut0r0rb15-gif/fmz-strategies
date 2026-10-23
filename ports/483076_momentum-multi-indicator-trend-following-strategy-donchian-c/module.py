"""Broker days, long only: the close crossing over the previous bar's 21-bar high on above-average volume goes long; the close crossing under the supertrend (2, 10) closes it (exit option 3).
Port of FMZ strategy #483076 "Momentum Multi Indicator Trend Following Strategy Donchian Channel with SuperTrend and Volume Filter Entry System" (Donchian BO with Volume Filter and Supertrend (DBO+Vol+ST)).

FMZ source id: 483076

Source
    https://www.fmz.com/strategy/483076 (PineScript v5, FMZ last modified 2025-02-21 11:47:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-183), Donchian 21; volume SMA 20; supertrend 2 / 10; exit option 3; date range 2016-01-01 .. 2030-07-01; 2 % of equity
    longCondition = crossover(close, highest(21)[1]) and volume > sma(volume, 20) -> entry Long
    exit == 3: crossunder(close, supertrend) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default exit option is 3 (the supertrend crossing); the other options and the trailing-stop
      code are not used. The date range covers all the data. The short condition is computed but never
      traded. The entry and the close never meet on one bar (above the channel high vs under the
      supertrend). Long only. 2 % of equity is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian breakouts on volume with a supertrend exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483076_donchian21_breakout_volume_supertrend_exit_long_only"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 55],
    "st_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 21, "st_mult": 2.0, "st_len": 10}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c, v = bars_df["high"], bars_df["close"], bars_df["volume"]
    up1 = h.rolling(int(p["length"])).max().shift(1)
    buy = (c > up1) & (c.shift(1) <= up1.shift(1)) & (v > v.rolling(20).mean())
    st, _ = _supertrend(bars_df, float(p["st_mult"]), int(p["st_len"]))
    ex = (c < st) & (c.shift(1) >= st.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), ex.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
