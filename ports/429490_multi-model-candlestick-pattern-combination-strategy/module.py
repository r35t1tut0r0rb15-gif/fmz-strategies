"""Noro candle models, broker days: a bullish engulfing, harami or harami cross goes long, the bearish ones go short;
a sizeable candle in the position's direction closes it.
Port of FMZ strategy #429490 "Multi model Candlestick Pattern Combination Strategy" (Noro's CandleModels Tests).

FMZ source id: 429490

Source
    https://www.fmz.com/strategy/429490 (PineScript v3, FMZ last modified 2023-10-17 15:53:06).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-226), engulfing / harami / harami cross on, doji = body < sma(body,10) / 10
    up1 engulfing: green after red, body range covers the previous one; up2 harami: inside it; up3 harami cross: doji inside a red body
    up -> close a short, entry long; dn (mirrors) -> close a long, entry short
    exit = ((long and green) or (short and red)) and body > sma(body,10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit closes a long on a sizeable GREEN candle (and a short on a red one), as written ("Reversive
      trading" off). It tests the position held at the start of the bar; an entry on the same bar wins.
    * The date window is dropped. One-bar reversals: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle shapes and body ratios only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
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

NAME = "fmz_429490_noro_candle_models"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_len": [10, 20],
    "exit_frac": [0.5, 1.0],
}
DEFAULT_PARAMS = {"body_len": 10, "exit_frac": 0.5, "doji_frac": 0.1}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body = (c - o).abs()
    abody = body.rolling(int(p["body_len"])).mean()
    mn, mx = pd.concat([c, o], axis=1).min(axis=1), pd.concat([c, o], axis=1).max(axis=1)
    bar = pd.Series(np.where(c > o, 1, np.where(c < o, -1, 0)), index=c.index)
    b1 = bar.shift(1)
    doji = body < abody * p["doji_frac"]
    up = ((bar == 1) & (b1 == -1) & (mn <= mn.shift(1)) & (mx >= mx.shift(1))) \
        | ((bar == 1) & (b1 == -1) & (mn >= mn.shift(1)) & (mx <= mx.shift(1))) \
        | (doji & (b1 == -1) & (lo >= mn.shift(1)) & (h <= mx.shift(1)))
    dn = ((bar == -1) & (b1 == 1) & (mn <= mn.shift(1)) & (mx >= mx.shift(1))) \
        | ((bar == -1) & (b1 == 1) & (mn >= mn.shift(1)) & (mx <= mx.shift(1))) \
        | (doji & (b1 == 1) & (lo >= mn.shift(1)) & (h <= mx.shift(1)))
    big = (body > abody * p["exit_frac"]).to_numpy()
    upv, dnv, barv = up.to_numpy(), dn.to_numpy(), bar.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        p0 = pos
        if upv[i]:
            pos = 1
        if dnv[i]:
            pos = -1
        if pos == p0 and big[i] and ((p0 > 0 and barv[i] == 1) or (p0 < 0 and barv[i] == -1)):
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
