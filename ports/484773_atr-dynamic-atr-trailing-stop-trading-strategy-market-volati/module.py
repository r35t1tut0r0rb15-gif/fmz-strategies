"""ATR flip-line crosses, always in, broker days: a line sits one ATR(10) under the close while the close is above the
previous line and one ATR over it otherwise; the close crossing above the line goes long, crossing below goes short.
Port of FMZ strategy #484773 "动态ATR追踪止损交易策略市场波动性自适应系统-Dynamic-ATR-Trailing-Stop-Trading-Strategy-Market-Volatility-Adaptive-System" (Xfera Trading Bot Automation).

FMZ source id: 484773

Source
    https://www.fmz.com/strategy/484773 (PineScript v5, FMZ last modified 2025-03-04 11:03:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 203-227), key value 1, ATR 10, Heikin Ashi off
    trail = src > nz(trail[1], 0) ? src - 1 x ATR : src + 1 x ATR
    crossover(src, trail) -> close short, entry long;  crossunder(src, trail) -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line as written: no ratchet (unlike the full UT Bot), it flips each bar on the close against the previous
      line. With the ATR still na the line is na (no signals).
    * The Heikin Ashi source is off by default (not ported). The close before each entry is the reversal itself
      (REVERSAL INTENDED).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_484773_atr_flip_line_cross"
FAMILY = "atr_trailing_line"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"key": 1.0, "atr_period": 10}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    loss = (p["key"] * _atr(bars_df, int(p["atr_period"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    trail = np.full(len(cv), np.nan)
    prev = np.nan
    for i in range(len(cv)):
        ref = 0.0 if np.isnan(prev) else prev            # nz(trail[1], 0)
        trail[i] = cv[i] - loss[i] if cv[i] > ref else cv[i] + loss[i]
        prev = trail[i]
    t = pd.Series(trail, index=c.index)
    long_e = ((c > t) & (c.shift(1) <= t.shift(1))).astype(bool)
    short_e = ((c < t) & (c.shift(1) >= t.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
