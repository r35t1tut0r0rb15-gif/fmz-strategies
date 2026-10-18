"""Donchian close breakouts, broker days, long only: a close at or over the previous bar's 20-bar high goes long; a close at or under the previous bar's 20-bar low closes the long. The two channel lengths are separate inputs.
Port of FMZ strategy #436595 "Dual Channel Donchian Breakout Strategy" (Donchian Backtest (separate channels)).

FMZ source id: 436595

Source
    https://www.fmz.com/strategy/436595 (PineScript v3, FMZ last modified 2023-12-26 10:18:51).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 134-160), upper 20, lower 20, offset 0
    upper = highest(high, length1);  lower = lowest(low, length2);  break_up = close >= upper[1];  break_down = close <= lower[1];  entry "buy" (quantity 1) when break_up;  close "buy" when break_down

Interpretation choices (Pine rules in SURVEY_README.md)
    * The offset input is not used. Entry and close are filled at the next open in the script's call order.
      Long only; the quantity (1) is sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 1 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436595_donchian_separate_channels"
FAMILY = "donchian_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [20, 30],
    "length2": [20, 10],
}
DEFAULT_PARAMS = {"length1": 20, "length2": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    upper = h.rolling(int(p["length1"])).max()
    lower = lo.rolling(int(p["length2"])).min()
    break_up = (c >= upper.shift(1)).to_numpy()
    break_down = (c <= lower.shift(1)).to_numpy()
    m = len(c)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos == 0:
                    pos = 1
                elif op == "XL" and pos > 0:
                    pos = 0
        held[i] = pos
        ops = []
        if break_up[i]:
            ops.append("eL")
        if break_down[i]:
            ops.append("XL")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
