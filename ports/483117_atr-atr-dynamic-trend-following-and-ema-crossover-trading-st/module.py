"""UT Bot: the close crossing its ATR(10) x 1 trailing level, always in the market, daily (broker-day) bars: the close
crossing above the ratcheting ATR trailing stop goes long; crossing below goes short.
Port of FMZ strategy #483117 "ATR动态趋势跟踪与均线交叉交易策略-ATR-Dynamic-Trend-Following-and-EMA-Crossover-Trading-Strategy" (UT Bot Strategy).

FMZ source id: 483117

Source
    https://www.fmz.com/strategy/483117 (PineScript v6, FMZ last modified 2025-02-27 16:57:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 108-151), key value 1, ATR 10, Heikin Ashi source off
    trail = ratchet of src -+ nLoss (UT Bot), starting na (var), src = close
    buy = src > trail and crossover(ema(src, 1), trail); sell = src < trail and crossover(trail, ema(src, 1))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is `var float ... = na`: the ratchet branches need a non-na previous level, so the first level is
      src + nLoss (a comparison with na is false), as written; this differs from the nz(..., 0) variant of L1 #492009 /
      L4 #489301. ema(src, 1) is src itself.
    * The Heikin Ashi switch (request.security of hlc3 on the same timeframe) is off by default and kept off.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. Daily bars are broker days (17:00 America/New_York)
      stamped with their first minute (as #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR trailing level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_483117_ut_bot_atr_trail_cross_1d"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "atr_len": [10, 14],
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


def _ut_trail_var(sr, nloss):
    """UT Bot ratchet with `var float trail = na`: the max / min branches need a non-na previous level."""
    m = len(sr)
    out = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        s, nl = sr[i], nloss[i]
        s1 = sr[i - 1] if i > 0 else np.nan
        known = not np.isnan(prev)
        if known and s > prev and s1 > prev:
            t = max(prev, s - nl) if not np.isnan(nl) else np.nan
        elif known and s < prev and s1 < prev:
            t = min(prev, s + nl) if not np.isnan(nl) else np.nan
        else:
            t = s - nl if (known and s > prev) else s + nl
        out[i] = t
        prev = t
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = bars_df["close"]
    nloss = p["key"] * _atr(bars_df, int(p["atr_len"]))
    trail = pd.Series(_ut_trail_var(src.to_numpy(dtype=float), nloss.to_numpy(dtype=float)), index=src.index)
    above = (src > trail) & (src.shift(1) <= trail.shift(1))
    below = (trail > src) & (trail.shift(1) <= src.shift(1))
    buy = (above & (src > trail)).astype(bool)
    sell = (below & (src < trail)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
