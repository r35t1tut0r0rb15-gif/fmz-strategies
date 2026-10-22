"""Engulfing candles in the EMA 50 / 200 trend at a neutral RSI, daily bars: a bullish engulfing candle over the EMA 50 with EMA 50 over EMA 200 and RSI 45-55 goes long, the mirror goes short; reversing. Each trade has a 1 ATR stop and a 2.0-point target (a fraction of 42000) from its signal close.
Port of FMZ strategy #474720 "Gold Trend Channel Reversal Momentum Strategy" (Gold Scalping Strategy with Precise Entries).

FMZ source id: 474720

Source
    https://www.fmz.com/strategy/474720 (PineScript v5, FMZ last modified 2024-12-11 17:52:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-141), EMA 50 / 200; ATR 14; RSI 14, 45-55; target 20 x 0.10 = 2.0 points
    ema50 > ema200 and 45 <= rsi <= 55 and bullishEngulfing and close > ema50 -> entry Long, exit(limit = close + 2.0, stop = close - atr);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 2.0-point target is a price amount, ported as a fraction of 42000 of the signal close
      (0.0000476, as #473399). The bracket is sent on the signal bar: sent as fractions of the fill open;
      a level at or through it is marketable and closed one bar late (as #458256). REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, trend engulfing candles at a neutral RSI with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474720_trend_engulfing_rsi45_55_atr_stop_point_target_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {}
DEFAULT_PARAMS = {"tp_frac": 4.76e-05}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signals(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    r = _rsi(c, 14)
    atr = _atr(bars_df, 14)
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c > o) & (c1 < o1) & (c > c1) & (o < c1)
    bear = (c < o) & (c1 > o1) & (c < c1) & (o > c1)
    mid = (r >= 45) & (r <= 55)
    le = (e50 > e200) & mid & bull & (c > e50)
    se = (e50 < e200) & mid & bear & (c < e50)
    t = float(p["tp_frac"]) * c
    lvl = {"l_sl": c - atr, "l_tp": c + t, "s_sl": c + atr, "s_tp": c - t}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
