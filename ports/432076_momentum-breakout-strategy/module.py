"""UT Bot (HPotter's ATR trailing line), broker days: the close crossing above its ATR 10 trailing line goes long, crossing
below goes short (the %B filter "bbr > 20 or bbr < 80" is always true).
Port of FMZ strategy #432076 "Momentum Breakout Strategy" (UT Bot Strategy).

FMZ source id: 432076

Source
    https://www.fmz.com/strategy/432076 (PineScript v4, FMZ last modified 2023-11-14 11:19:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 160-248), key 1, ATR 10, HA off, BB 20 / 2 (filter inert)
    trailing line of close with nLoss = 1 x ATR(10) (UT Bot);  buy = close > line and crossover(close, line)
    sell = close < line and crossover(line, close);  buy -> entry long;  sell -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The %B filter (bbr > 20 or bbr < 80) is true for every value, as written. Heikin Ashi signals
      are off. ATR is Pine's (Wilder, SMA seed).
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR trailing line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432076_ut_bot_atr_line"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "atr_len": [10, 20],
}
DEFAULT_PARAMS = {"key": 1.0, "atr_len": 10}


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
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1s = c.shift(1)
    tr = pd.concat([h - lo, (h - c1s).abs(), (lo - c1s).abs()], axis=1).max(axis=1).where(c1s.notna(), h - lo)
    nl = _rma(tr, int(p["atr_len"])) * float(p["key"])
    src = c.to_numpy(dtype=float)
    m = len(src)
    line = np.zeros(m)
    prev = 0.0
    for i in range(m):
        s1 = src[i - 1] if i else np.nan
        if src[i] > prev and s1 > prev:
            v = max(prev, src[i] - nl[i])
        elif src[i] < prev and s1 < prev:
            v = min(prev, src[i] + nl[i])
        else:
            v = src[i] - nl[i] if src[i] > prev else src[i] + nl[i]
        line[i] = v
        prev = 0.0 if np.isnan(v) else v
    l1 = np.concatenate(([np.nan], line[:-1]))
    s1a = np.concatenate(([np.nan], src[:-1]))
    buy = (src > line) & (s1a <= l1)
    sell = (src < line) & (s1a >= l1)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(buy & ~sell, index=idx), false, pd.Series(sell, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
