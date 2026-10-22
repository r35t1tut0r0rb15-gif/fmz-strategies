"""A hand-built SuperTrend (ATR 10 x 3 on hl2) flip, 3-day bars: the flip up goes long and the flip down goes short; reversing (the take-profit and stop are labels only).
Port of FMZ strategy #489186 "高级多功能SuperTrend趋势跟踪策略与自动止盈止损系统-Advanced-Multi-functional-SuperTrend-Trend-Following-Strategy-with-Automated-Take-Profit-and-Stop-Loss-System" (SuperTrend STRATEGY w/ TP & SL).

FMZ source id: 489186

Source
    https://www.fmz.com/strategy/489186 (PineScript v5, FMZ last modified 2025-04-02 15:30:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 174-277), ATR 10 x 3; hl2; TP 2.5 % / SL 1 % / entry offset 0.2 % (labels only)
    up := close[1] > prevUp ? max(hl2 - 3 atr, prevUp) : hl2 - 3 atr;  dn mirror with min;  trend := close > prevDn ? 1 : close < prevUp ? -1 : trend[1]
    trend turns 1 -> entry BUY;  trend turns -1 -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands follow the script's own recursion (nz of the previous band); the trend rule takes any
      close over the previous down-band as up, as written. The TP / SL "hits" only draw labels: no exit
      orders. Each flip enters the other side: REVERSAL INTENDED. No sizing code. Bars are blocks of three
      broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their first minute. FREQ =
      "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend flips.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: three-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489186_handbuilt_supertrend10_3_flip_reversal_3d"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (three broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "atrPeriod": [10, 20],
}
DEFAULT_PARAMS = {"mult": 3.0, "atrPeriod": 10, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atrPeriod"])).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    k = float(p["mult"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn, tr_ = np.full(m, np.nan), np.full(m, np.nan), np.ones(m)
    t = 1
    for i in range(m):
        ru, rd = src[i] - k * atr[i], src[i] + k * atr[i]
        pu = up[i - 1] if i >= 1 and not np.isnan(up[i - 1]) else ru
        pdn = dn[i - 1] if i >= 1 and not np.isnan(dn[i - 1]) else rd
        c1 = cv[i - 1] if i >= 1 else np.nan
        up[i] = (np.nan if np.isnan(ru) or np.isnan(pu) else max(ru, pu)) if c1 > pu else ru
        dn[i] = (np.nan if np.isnan(rd) or np.isnan(pdn) else min(rd, pdn)) if c1 < pdn else rd
        if cv[i] > pdn:
            t = 1
        elif cv[i] < pu:
            t = -1
        tr_[i] = t
    trend = pd.Series(tr_, index=c.index)
    le = (trend == 1) & (trend.shift(1) == -1)
    se = (trend == -1) & (trend.shift(1) == 1)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
