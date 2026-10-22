"""EMA 9 / 20 (of ohlc4) crossings and close-over-EMA-9 crossings under four ids, daily bars: a 9 / 20 cross up goes long, a cross down short; a close crossing over the EMA 9 enters long then short on
the same bar (the short test repeats the long one, as written), so it ends short; reversing. The tick trails are kept pending.
Port of FMZ strategy #444007 "EMA9 20Dual Moving Average Crossover Strategy EMA9 20" (9/20 EMAs).

FMZ source id: 444007

Source
    https://www.fmz.com/strategy/444007 (PineScript v5, FMZ last modified 2024-03-08 15:22:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-166), EMA 9 / 20 of ohlc4; trail points 15, offset 10 (ticks); qty 2, commission 0.35 per contract
    if up20 -> entry Long 9Cross20;  else if crossover(close, ema9) -> entry Long 9CrossClose + trail exit;  else if dn20 -> close Long 9Cross20
    if dn20 -> entry Short 9Cross20;  else if crossover(close, ema9) (named "crossunder") -> entry Short 9CrossClose + trail exit;  else if up20 -> close Short 9Cross20

Interpretation choices (Pine rules in SURVEY_README.md)
    * closeCrossunderEma9 is written as ta.crossover, the same test as the long one, so a close crossing
      over the EMA 9 sends a long and then a short: the later short wins. Ported in call order with one
      position at a time (default pyramiding); each close acts only on its own held id. The 9CrossClose
      ids carry a trail of 15 / 10 ticks (1.5 / 1 price units on BTC), which applies to those ids only:
      the house trail is per module, so it is kept pending (mark trailing_stop_pending). strategy.entry
      reverses: REVERSAL INTENDED. The quantity and per-contract commission are sizing and costs. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-id tick trail pending.
    2 generic: PASS, EMA crossings under named ids (as written).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity and per-contract commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_444007_ema9_20_ohlc4_named_ids_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 20}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    src = (o + h + lo + c) / 4
    e9 = src.ewm(span=int(p["fast"]), adjust=False).mean()
    e20 = src.ewm(span=int(p["slow"]), adjust=False).mean()
    cxo = ((c > e9) & (c.shift(1) <= e9.shift(1))).to_numpy()
    up20 = ((e9 > e20) & (e9.shift(1) <= e20.shift(1))).to_numpy()
    dn20 = ((e9 < e20) & (e9.shift(1) >= e20.shift(1))).to_numpy()
    side = {None: 0, "L20": 1, "LC": 1, "S20": -1, "SC": -1}
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = None
    for i in range(m):
        new = held
        if up20[i]:
            if side[new] != 1:
                new = "L20"
        elif cxo[i]:
            if side[new] != 1:
                new = "LC"
        elif dn20[i] and held == "L20" and new == "L20":
            new = None
        if dn20[i]:
            if side[new] != -1:
                new = "S20"
        elif cxo[i]:
            if side[new] != -1:
                new = "SC"
        elif up20[i] and held == "S20" and new == "S20":
            new = None
        tgt[i] = side[new]
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
