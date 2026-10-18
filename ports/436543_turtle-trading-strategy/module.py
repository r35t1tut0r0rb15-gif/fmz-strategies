"""Turtle channel breakouts, broker days: a high over the previous 20-bar high goes long (a low under the previous 20-bar low goes short, reversing); a low at or under the previous 10-bar low closes the long, a high at or over
the previous 10-bar high closes the short. The 55 / 20 slow system can never trade.
Port of FMZ strategy #436543 "Turtle Trading Strategy" (Turtles).

FMZ source id: 436543

Source
    https://www.fmz.com/strategy/436543 (PineScript v2, FMZ last modified 2023-12-25 17:12:05).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 128-193), enter 20, exit 10 (fast); enter 55, exit 20 (slow); shorting on
    enterL1 = high > highest(high, 20)[1];  exitL1 = low <= lowest(low, 10)[1];  enterS1 = low < lowest(low, 20)[1];  exitS1 = high >= highest(high, 10)[1];  slow channels 55 / 20 likewise
    entry "fast L" when enterL1;  if not enterL1: entry "slow L" when enterL2;  close "fast L" when exitL1;  close "slow L" when exitL2;  entry "fast S" when enterS1;  if not enterS2: entry "slow S" when enterS2;  close "fast S" when exitS1;  close "slow S" when exitS2

Interpretation choices (Pine rules in SURVEY_README.md)
    * The slow entries cannot fire: a high over the 55-bar high is also over the 20-bar high (the slow long
      is only tried when the fast one is false), and the slow short is tried only when its own condition
      is false. The slow closes then act on a position that never exists, so the port keeps the fast
      system only. The conditions use the bar's high / low; the orders are filled at the next open
      (not at the channel level). The four rules of one bar are filled in the script's call order;
      a close only acts on a position of its own side. REVERSAL INTENDED. The percent-of-equity size
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_436543_turtle_fast_channel"
FAMILY = "donchian_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "enter_fast": [20, 30],
    "exit_fast": [10, 15],
}
DEFAULT_PARAMS = {"enter_fast": 20, "exit_fast": 10}


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
    h, lo = bars_df["high"], bars_df["low"]
    ef, xf = int(p["enter_fast"]), int(p["exit_fast"])
    enter_l = (h > h.rolling(ef).max().shift(1)).to_numpy()
    exit_l = (lo <= lo.rolling(xf).min().shift(1)).to_numpy()
    enter_s = (lo < lo.rolling(ef).min().shift(1)).to_numpy()
    exit_s = (h >= h.rolling(xf).max().shift(1)).to_numpy()
    m = len(h)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "eS" and pos >= 0:
                    pos = -1
                elif op == "XL" and pos > 0:
                    pos = 0
                elif op == "XS" and pos < 0:
                    pos = 0
        held[i] = pos
        ops = []
        if enter_l[i]:
            ops.append("eL")
        if exit_l[i]:
            ops.append("XL")
        if enter_s[i]:
            ops.append("eS")
        if exit_s[i]:
            ops.append("XS")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
