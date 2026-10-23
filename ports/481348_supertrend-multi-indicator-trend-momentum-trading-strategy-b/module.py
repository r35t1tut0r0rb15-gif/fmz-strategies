"""2-day bars, long only: the script's supertrend (ATR 10 x 3 around hl2) flipping to up goes long; flipping to down closes it.
Port of FMZ strategy #481348 "基于SuperTrend的多指标趋势动量交易策略Multi-Indicator-Trend-Momentum-Trading-Strategy-Based-on-SuperTrend" (SuperTrend on Steroids).

FMZ source id: 481348

Source
    https://www.fmz.com/strategy/481348 (PineScript v6, FMZ last modified 2025-02-10 14:31:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-155), ATR 10 x 3; trend var starting at 1; EMA 21, VWAP and DMI only plot
    up = hl2 - 3 atr;  up := close[1] > nz(up[1], up) ? max(up, up[1]) : up;  dn mirrored;  trend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend
    trend == 1 and trend[1] == -1 -> entry Long;  trend == -1 and trend[1] == 1 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The classic (KivancOzbilgic) supertrend recursion, with the trend flag starting at 1 and the flips
      read against the previous bar's bands. The EMA 21, the VWAP and the DMI only plot, so volume is not
      used (held for volume, not used). Long only. No sizing code. 2-day bars are blocks of two broker
      days counted from 1970-01-01, each stamped with its first minute. FREQ = "2D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, supertrend flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker days in 2-day blocks (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481348_supertrend_flip_2d_long_only"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [10, 14],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"days": 2, "atr_len": 10, "mult": 3.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1),
               int(p["atr_len"])).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cn = c.to_numpy(dtype=float)
    k = float(p["mult"])
    m = len(cn)
    up, dn, tr = np.full(m, np.nan), np.full(m, np.nan), np.ones(m)
    for i in range(m):
        u, d = src[i] - k * atr[i], src[i] + k * atr[i]
        u1 = up[i - 1] if i > 0 and not np.isnan(up[i - 1]) else u     # nz(up[1], up)
        d1 = dn[i - 1] if i > 0 and not np.isnan(dn[i - 1]) else d
        c1 = cn[i - 1] if i > 0 else np.nan
        up[i] = max(u, u1) if c1 > u1 else u
        dn[i] = min(d, d1) if c1 < d1 else d
        prev = tr[i - 1] if i > 0 else 1.0
        tr[i] = 1.0 if (prev == -1 and cn[i] > d1) else (-1.0 if (prev == 1 and cn[i] < u1) else prev)
    t = pd.Series(tr, index=c.index)
    buy = (t == 1) & (t.shift(1) == -1)
    sell = (t == -1) & (t.shift(1) == 1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
