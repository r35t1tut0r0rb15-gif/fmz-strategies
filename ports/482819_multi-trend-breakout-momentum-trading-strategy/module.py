"""Broker days, from flat only: within 3 bars of a close above the prior 20-bar high, on volume over 2 x its 20-day average, a close above the prior 10-bar high in an EMA 30 > 50 > 200 uptrend goes long; the mirror with a falling EMA 200, or a 10-bar range under 0.5 ATR with every high under the EMA 50, goes short; a long closes under the EMA 200, a short above it.
Port of FMZ strategy #482819 "Multi Trend Breakout Momentum Trading Strategy" (Breakout Strategy (Long & Short) + Slope of 200 EMA).

FMZ source id: 482819

Source
    https://www.fmz.com/strategy/482819 (PineScript v5, FMZ last modified 2025-02-20 14:53:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 108-220), breakout 20, range 10; EMA 30 / 50 / 200; volume SMA 20 x 2; consolidation 10 bars < 0.5 ATR 14
    long_condition = barssince(close > highest(high, 20)[1]) <= 3 and volume > 2 x avg and close > highest(high, 10)[1] and close > ema200 and ema30 > ema50 > ema200 and opentrades == 0 -> entry Long
    short_condition = (the mirror with ema200 falling, or (highest(high, 10) - lowest(low, 10) < 0.5 atr and highest(high - ema50, 10) < 0)) and opentrades == 0 -> entry Short
    position_size > 0 and close < ema200 -> close Long;  position_size < 0 and close > ema200 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries need no open trade at the bar's close, so the strategy never reverses; the closes act from
      the bar after the fill. A bar where both entries hold from flat sends both; the later short call
      wins. barssince counts the current bar as 0. Opposite entries cannot occur. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume breakouts in an EMA stack, consolidation shorts, EMA 200 exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 2 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only when flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482819_breakout_ema_stack_consolidation_short_ema200_exit"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "breakout": [20, 55],
    "narrow": [0.5, 1.0],
}
DEFAULT_PARAMS = {"breakout": 20, "range": 10, "narrow": 0.5}


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


def _recent(flag, k):
    """ta.barssince(flag) <= k (the current bar counts as 0; never true -> na -> false)."""
    f = np.asarray(flag)
    out = np.zeros(len(f), dtype=bool)
    last = -10**9
    for i in range(len(f)):
        if f[i]:
            last = i
        out[i] = i - last <= k
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    nb, nr = int(p["breakout"]), int(p["range"])
    e200, e50, e30 = (c.ewm(span=n, adjust=False).mean() for n in (200, 50, 30))
    vol_ok = (v > 2 * v.rolling(nb).mean()).to_numpy()
    bu = _recent((c > h.rolling(nb).max().shift(1)).to_numpy(), 3)
    bd = _recent((c < lo.rolling(nb).min().shift(1)).to_numpy(), 3)
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    narrow = (h.rolling(nr).max() - lo.rolling(nr).min()) < atr * float(p["narrow"])
    below_mid = (h - e50).rolling(nr).max() < 0
    longc = bu & vol_ok & (c > h.rolling(nr).max().shift(1)).to_numpy() & (c > e200).to_numpy() \
        & ((e30 > e50) & (e50 > e200)).to_numpy()
    shortc = (bd & vol_ok & (c < lo.rolling(nr).min().shift(1)).to_numpy() & (c < e200).to_numpy()
              & ((e30 < e50) & (e50 < e200) & (e200 < e200.shift(1))).to_numpy()) | (narrow & below_mid).to_numpy()
    above, under = (c > e200).to_numpy(), (c < e200).to_numpy()
    m = len(longc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0:
            if shortc[i]:
                se[i], pos = True, -1
            elif longc[i]:
                le[i], pos = True, 1
        elif pos == 1 and under[i]:
            lx[i], pos = True, 0
        elif pos == -1 and above[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
