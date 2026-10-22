"""The daily close above four SuperTrend (ATR 10 x 3) lines, broker days, long only: above the day's own line and the last 15-, 5- and 2-minute lines of the day buys; a close under the last 5-minute line closes.
Port of FMZ strategy #477605 "多时间周期Supertrend趋势交易策略的动态组合算法-Multi-Timeframe-Supertrend-Dynamic-Trend-Trading-Algorithm" (Multi-Timeframe Supertrend Strategy).

FMZ source id: 477605

Source
    https://www.fmz.com/strategy/477605 (PineScript v5, FMZ last modified 2025-01-06 16:38:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-186), SuperTrend ATR 10 x 3 on the chart and on "15" / "5" / "2" (lookahead off); session filter always true; 100 % of equity, capital 50000
    [st15] = security("15", supertrend(3, 10));  [st5] = security("5", ...);  [st2] = security("2", ...);  [st] = supertrend(3, 10)
    close > st15 and close > st5 and close > st2 and close > st and flat -> entry Buy;  close < st5 and long -> close Buy;  the end-of-day close needs not in_session (always false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "15", "5" and "2" requests on a daily chart are lower time frames: each returns the chart bar's
      last block (as #436765), so each line is the SuperTrend of that minute series at the day's last
      block, built from the minutes in precompute (blocks counted from the broker-day start). The session
      flag is fixed true, so the end-of-day close never fires. Long only. The 100 % of equity size and
      capital are sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; lower-time-frame lines from each day's last block.
    2 generic: PASS, multi-time-frame SuperTrend alignment.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital 50000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); minute blocks from the broker-day start; the session input is unused.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477605_mtf_supertrend_15_5_2min_daily_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_period": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
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


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    for n in (15, 5, 2):
        ltf = df.resample(f"{n}min", label="left", closed="left").agg(
            {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
        line = _supertrend(ltf, float(p["factor"]), int(p["atr_period"]))[0]
        last = line.groupby(broker_day(ltf.index)).last()       # the day's last block
        bars[f"st_{n}"] = last.reindex(bars.index).to_numpy()
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    st = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))[0]
    le = (c > bars_df["st_15"]) & (c > bars_df["st_5"]) & (c > bars_df["st_2"]) & (c > st)
    lx = c < bars_df["st_5"]
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
