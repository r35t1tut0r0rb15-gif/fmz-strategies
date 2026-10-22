"""EMA 20 / 50 crossings with the classic Supertrend (ATR 10 x 3 on hl2), daily bars, long only: the cross up in a Supertrend up trend buys; the cross down in a down trend sells.
Port of FMZ strategy #453657 "Supertrend和EMA组合策略-Supertrend-and-EMA-Combination-Strategy" (Supertrend EMA Strategy).

FMZ source id: 453657

Source
    https://www.fmz.com/strategy/453657 (PineScript v4, FMZ last modified 2024-06-07 15:36:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-159), Supertrend ATR 10 (rma), multiplier 3, hl2; EMA 20 / 50 (100 / 200 plotted only); 10 % of equity
    up = hl2 - 3 atr, raised while close[1] > up[1];  dn = hl2 + 3 atr, lowered while close[1] < dn[1];  trend flips on close > dn[1] / close < up[1]
    crossover(ema20, ema50) and trend == 1 -> entry Buy;  crossunder(ema20, ema50) and trend == -1 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The classic Supertrend recursion as written (changeATR true: the rma ATR). The close needs the
      cross down AND the down trend, so a long can outlast a cross down taken in an up trend. Long
      only. The 10 % of equity is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a Supertrend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453657_ema20_50_cross_classic_supertrend_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [10, 14],
    "mult": [3.0, 2.0],
    "short_ema": [20, 10],
}
DEFAULT_PARAMS = {"atr_len": 10, "mult": 3.0, "short_ema": 20, "medium_ema": 50}


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
    c = bars_df["close"]
    tr = pd.Series(_classic_trend(bars_df, p["atr_len"], float(p["mult"])), index=c.index)
    a = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    b = c.ewm(span=int(p["medium_ema"]), adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (tr == 1)
    lx = (a < b) & (a.shift(1) >= b.shift(1)) & (tr == -1)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
