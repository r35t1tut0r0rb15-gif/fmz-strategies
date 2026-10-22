"""Classic Supertrend flips (ATR 10 x 3 around hl2), daily bars, long only: the trend turning up buys, with a 5 % target and 2 % stop from the fill.
Port of FMZ strategy #471713 "基于ATR的多重趋势跟踪策略与止盈止损优化系统-ATR-Based-Multi-Trend-Following-Strategy-with-Take-Profit-and-Stop-Loss-Optimization-System" (Custom Buy BID Strategy (Buy BID by MR.STOCKVN)).

FMZ source id: 471713

Source
    https://www.fmz.com/strategy/471713 (PineScript v5, FMZ last modified 2024-11-12 16:14:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-172), ATR 10 (rma, the "change ATR" switch on), multiplier 3, source hl2; target 5 %, stop 2 % of the average price; date window 2018-9999
    trend turns from -1 to 1 -> entry BUY (in the date window);  while long: exit(limit = avg x 1.05, stop = avg x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The classic Supertrend recursion as written (#458061's helper). The date window is dropped like
      other date windows. The bracket comes from the average (fill) price and is sent every bar while
      held: ported active from the fill bar (#440797) as the fixed fractions 0.05 / 0.02 of the fill.
      There is no other exit. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily
      bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, Supertrend flips with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_471713_classic_supertrend_flip_up_pct_bracket_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "periods": [10, 14],
    "multiplier": [3.0, 2.0],
    "tp_pct": [0.05, 0.10],
}
DEFAULT_PARAMS = {"periods": 10, "multiplier": 3.0, "tp_pct": 0.05, "sl_pct": 0.02}


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


def _classic_trend(bars_df, n, k):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(n)).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    upv, dnv, trend = np.full(m, np.nan), np.full(m, np.nan), np.ones(m, dtype=int)
    t = 1
    for i in range(m):
        up, dn = hl2[i] - k * atr[i], hl2[i] + k * atr[i]
        up1 = upv[i - 1] if i > 0 and not np.isnan(upv[i - 1]) else up
        dn1 = dnv[i - 1] if i > 0 and not np.isnan(dnv[i - 1]) else dn
        cp = cv[i - 1] if i > 0 else np.nan
        if cp > up1:
            up = max(up, up1)
        if cp < dn1:
            dn = min(dn, dn1)
        if t == -1 and cv[i] > dn1:
            t = 1
        elif t == 1 and cv[i] < up1:
            t = -1
        upv[i], dnv[i], trend[i] = up, dn, t
    return trend


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tr = pd.Series(_classic_trend(bars_df, p["periods"], float(p["multiplier"])), index=bars_df.index)
    le = (tr == 1) & (tr.shift(1) == -1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
