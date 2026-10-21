"""SuperTrend-style ATR (10, 3) trend changes on hl2, broker days: the trend turning up goes long, turning down goes short; reversing. The filtered equity curve and its table only display.
Port of FMZ strategy #438771 "Quantitative Trading Strategy Based on Supertrend Indicator and Equity Curve Trading" (Supertrend & Equity curve with EMA).

FMZ source id: 438771

Source
    https://www.fmz.com/strategy/438771 (PineScript v5, FMZ last modified 2024-01-15 11:41:53).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 183-211), ATR 10 (Wilder), source hl2, multiplier 3; equity EMA 25 (display); capital 100000
    up / dn ATR lines and trend as the SuperTrend family;  trend turns 1 -> entry Long;  turns -1 -> entry Short;  equity-curve EMA, new curve and statistics table: display only

Interpretation choices (Pine rules in SURVEY_README.md)
    * The equity-curve filter only feeds the table and plots; no order depends on it. The ATR is
      Wilder's (changeATR on). strategy.entry reverses: REVERSAL INTENDED. The capital is sizing. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trend line changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital stored.
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

NAME = "fmz_438771_atr_trend_change_equity_display"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [10, 14],
    "multiplier": [3.0, 4.0],
}
DEFAULT_PARAMS = {"periods": 10, "multiplier": 3.0}


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


def _trend(bars_df, n, k):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    upv, dnv = np.full(m, np.nan), np.full(m, np.nan)
    t = np.ones(m)
    for i in range(m):
        u, d = src[i] - k * atr[i], src[i] + k * atr[i]
        u1 = upv[i - 1] if i > 0 and not np.isnan(upv[i - 1]) else u       # nz(up[1], up)
        d1 = dnv[i - 1] if i > 0 and not np.isnan(dnv[i - 1]) else d
        c1 = cv[i - 1] if i > 0 else np.nan
        upv[i] = max(u, u1) if (c1 > u1 and not np.isnan(u)) else u
        dnv[i] = min(d, d1) if (c1 < d1 and not np.isnan(d)) else d
        prev = t[i - 1] if i > 0 else 1.0
        t[i] = 1.0 if (prev == -1 and cv[i] > d1) else (-1.0 if (prev == 1 and cv[i] < u1) else prev)
    return t


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = _trend(bars_df, int(p["periods"]), float(p["multiplier"]))
    tp = np.concatenate(([np.nan], t[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((t == 1) & (tp == -1), index=ix), false, pd.Series((t == -1) & (tp == 1), index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
