"""SuperTrend-style ATR (10, 3) trend changes on hl2, broker days: the trend turning up goes long, turning down goes short; reversing. The trailing exits give only an offset and never arm.
Port of FMZ strategy #438505 "基于ATR的ES尾随停止策略ATR-based-Trailing-Stop-Strategy-for-ES" (ATR Based Trailing Stop Strategy on ES! [v4]).

FMZ source id: 438505

Source
    https://www.fmz.com/strategy/438505 (PineScript v4, FMZ last modified 2024-01-12 14:52:23).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 115-149), ATR 10 (Wilder), source hl2, multiplier 3
    up = hl2 - 3 atr, ratcheted while close[1] > up[1];  dn = hl2 + 3 atr, ratcheted while close[1] < dn[1];  trend flips on the close crossing dn[1] / up[1]
    trend turns 1 -> entry Long;  turns -1 -> entry Short;  exit(trail_offset = up - 1) / exit(trail_offset = dn + 1)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits pass a price level as trail_offset (ticks) and no trail_price or trail_points, so the
      trailing stop never activates and no exit is placed (as written; owed). The ATR is Wilder's
      (changeATR on). strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trend line changes.
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

NAME = "fmz_438505_atr_trend_change_hl2"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [10, 20],
    "multiplier": [3.0, 2.0],
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["periods"])).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    k = float(p["multiplier"])
    m = len(cv)
    upv, dnv = np.full(m, np.nan), np.full(m, np.nan)
    tr_ = np.ones(m)
    for i in range(m):
        u, d = src[i] - k * atr[i], src[i] + k * atr[i]
        u1 = upv[i - 1] if i > 0 and not np.isnan(upv[i - 1]) else u       # nz(up[1], up)
        d1 = dnv[i - 1] if i > 0 and not np.isnan(dnv[i - 1]) else d
        c1 = cv[i - 1] if i > 0 else np.nan
        upv[i] = max(u, u1) if (c1 > u1 and not np.isnan(u)) else u
        dnv[i] = min(d, d1) if (c1 < d1 and not np.isnan(d)) else d
        prev = tr_[i - 1] if i > 0 else 1.0
        tr_[i] = 1.0 if (prev == -1 and cv[i] > d1) else (-1.0 if (prev == 1 and cv[i] < u1) else prev)
    tprev = np.concatenate(([np.nan], tr_[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tr_ == 1) & (tprev == -1), index=ix), false,
            pd.Series((tr_ == -1) & (tprev == 1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
