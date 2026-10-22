"""UT Bot ATR trailing line (key 1, ATR 10) crossings, broker days: the close crossing up through the line goes long, crossing down goes short; reversing, no other exit.
Port of FMZ strategy #483117 "ATR动态趋势跟踪与均线交叉交易策略-ATR-Dynamic-Trend-Following-and-EMA-Crossover-Trading-Strategy" (UT Bot Strategy).

FMZ source id: 483117

Source
    https://www.fmz.com/strategy/483117 (PineScript v6, FMZ last modified 2025-02-27 16:57:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-160), key value 1; ATR 10; Heikin Ashi source off; 100 % of equity
    xATRTrailingStop: the UT Bot ratchet of close -/+ atr(10) (with na handling of the previous value)
    buy = close > line and crossover(ema(close, 1), line);  sell = close < line and crossover(line, ema(close, 1)) -> entries Long / Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi option is off by default (the source is the close), and ema(close, 1) is the close.
      The line follows the source's na tests: with no previous value it takes close - / + nLoss by the
      else branch (close + nLoss, as the comparison with na is false). The position colouring is drawing
      only. Entries only: each reverses the other side (REVERSAL INTENDED), no other exit. The 100 % of
      equity size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing-line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_483117_ut_bot1_atr10_line_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key_value": [1.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"key_value": 1.0, "atr_period": 10}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    nl = (float(p["key_value"]) * _rma(tr, int(p["atr_period"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    for i in range(m):
        prev = ts[i - 1] if i >= 1 else np.nan
        s1 = cv[i - 1] if i >= 1 else np.nan
        if not np.isnan(prev) and cv[i] > prev and s1 > prev:
            ts[i] = max(prev, cv[i] - nl[i])
        elif not np.isnan(prev) and cv[i] < prev and s1 < prev:
            ts[i] = min(prev, cv[i] + nl[i])
        else:
            ts[i] = (cv[i] - nl[i]) if (not np.isnan(prev) and cv[i] > prev) else (cv[i] + nl[i])
    line = pd.Series(ts, index=c.index)
    le = (c > line) & (c > line) & (c.shift(1) <= line.shift(1))
    se = (c < line) & (line > c) & (line.shift(1) <= c.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
