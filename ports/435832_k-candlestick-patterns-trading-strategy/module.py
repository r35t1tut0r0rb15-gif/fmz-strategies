"""Candlestick pattern signals, broker days, long only: bullish patterns (dragonfly doji, three white soldiers, three line strike up, piercing,
morning star, bullish engulfing, hammer) buy, bearish patterns (gravestone doji, three black crows, three line strike down, dark cloud,
evening star, bearish engulfing, falling star) close the long.
Port of FMZ strategy #435832 "形态K线交易策略Candlestick-Patterns-Trading-Strategy" (Candlestick Signals Strategy).

FMZ source id: 435832

Source
    https://www.fmz.com/strategy/435832 (PineScript v3, FMZ last modified 2023-12-19 10:56:36).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 130-226), all pattern switches on; the plain Doji up / down patterns are computed but not used by the orders
    buy = dragondojibear or dragondojibull or tws or tlsu or pu or ms1u or ms2u or beu or bhu1 or bhu2;  sell = gravedojibear or gravedojibull or tbc or tlsd or dc or es1d or es2d or bed or bfs1 or bfs2
    buy -> entry long (floor(equity / close) units);  sell -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every pattern is written out as in the script (body / shadow comparisons between the current and the
      three earlier candles, no price constants). A bar that is both a buy and a sell pattern leaves
      the position flat (the entry is sent first, then the close), so the entry is dropped. The
      equity-based size is sizing. Long only. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle shape comparisons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based order size and capital stored.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435832_candlestick_pattern_signals_long"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def S(x, k):
        return x.shift(k)

    oc, co = o - c, c - o
    # one-candle shapes
    gravedoji_bull = (co > 0) & ((h - c) / 8 > co) & ((h - c) / 5 > (o - lo))
    gravedoji_bear = (oc > 0) & ((h - o) / 8 > oc) & ((h - o) / 5 > (c - lo))
    dragon_bull = (co > 0) & ((o - lo) / 8 > co) & ((o - lo) / 5 > (h - c))
    dragon_bear = (oc > 0) & ((c - lo) / 8 > oc) & ((c - lo) / 5 > (h - o))
    # three black crows / three white soldiers
    tbc = ((S(lo, 2) < S(lo, 3)) & (S(lo, 1) < S(lo, 2)) & (lo < S(lo, 1)) & (S(h, 2) < S(h, 3)) & (S(h, 1) < S(h, 2))
           & (h < S(h, 1)) & (S(c, 3) - S(o, 3) > 0) & (S(o, 2) - S(c, 2) > 0) & (S(o, 1) - S(c, 1) > 0) & (oc > 0)
           & (oc > (c - lo)) & (oc > (h - o)) & (S(o, 1) - S(c, 1) > S(c, 1) - S(lo, 1))
           & (S(o, 1) - S(c, 1) > S(h, 1) - S(o, 1)) & (S(o, 2) - S(c, 2) > S(c, 2) - S(lo, 2))
           & (S(o, 2) - S(c, 2) > S(h, 2) - S(o, 2)))
    tws = ((S(h, 2) > S(h, 3)) & (S(h, 1) > S(h, 2)) & (h > S(h, 1)) & (S(lo, 2) > S(lo, 3)) & (S(lo, 1) > S(lo, 2))
           & (lo > S(lo, 1)) & (S(o, 3) - S(c, 3) > 0) & (S(c, 2) - S(o, 2) > 0) & (S(c, 1) - S(o, 1) > 0) & (co > 0)
           & (co > (o - lo)) & (co > (h - c)) & (S(c, 1) - S(o, 1) > S(o, 1) - S(lo, 1))
           & (S(c, 1) - S(o, 1) > S(h, 1) - S(c, 1)) & (S(c, 2) - S(o, 2) > S(o, 2) - S(lo, 2))
           & (S(c, 2) - S(o, 2) > S(h, 2) - S(c, 2)))
    # three line strike
    tlsu = ((co > 0) & (S(o, 1) - S(c, 1) > 0) & (S(o, 2) - S(c, 2) > 0) & (S(o, 3) - S(c, 3) > 0) & (o < S(c, 1))
            & (S(lo, 1) < S(lo, 2)) & (S(lo, 2) < S(lo, 3)) & (h > S(h, 3)) & (lo < S(lo, 1)))
    tlsd = ((oc > 0) & (S(c, 1) - S(o, 1) > 0) & (S(c, 2) - S(o, 2) > 0) & (S(c, 3) - S(o, 3) > 0) & (o > S(c, 1))
            & (S(h, 1) > S(h, 2)) & (S(h, 2) > S(h, 3)) & (lo < S(lo, 3)) & (h > S(h, 1)))
    # piercing / dark cloud
    pu = ((S(o, 1) - S(c, 1) > 0) & (co > 0) & (S(o, 1) - S(c, 1) > S(h, 1) - S(o, 1)) & (S(o, 1) - S(c, 1) > S(c, 1) - S(lo, 1))
          & (co > h - c) & (co > o - lo) & (o < S(c, 1)) & ((S(o, 1) + S(c, 1)) / 2 < c) & (co / 2 > h - c) & (c < S(o, 1))
          & ((h < S(h, 1)) | (lo > S(lo, 1))))
    dc = ((S(c, 1) - S(o, 1) > 0) & (oc > 0) & (S(c, 1) - S(o, 1) > S(h, 1) - S(c, 1)) & (S(c, 1) - S(o, 1) > S(o, 1) - S(lo, 1))
          & (oc > h - o) & (oc > c - lo) & (o > S(c, 1)) & ((S(o, 1) + S(c, 1)) / 2 > c) & (oc / 2 > c - lo) & (c > S(o, 1))
          & ((h < S(h, 1)) | (lo > S(lo, 1))))
    # morning / evening star
    ms1u = ((S(o, 2) - S(c, 2) > 0) & (co > 0) & (S(o, 1) - S(c, 1) >= 0) & (S(o, 2) - S(c, 2) > S(h, 2) - S(o, 2))
            & (S(o, 2) - S(c, 2) > S(c, 2) - S(lo, 2)) & (co > h - c) & (co > o - lo) & (co > S(o, 1) - S(c, 1))
            & (S(o, 2) - S(c, 2) > S(o, 1) - S(c, 1)) & (S(o, 1) < S(c, 2)) & (S(o, 1) < o) & (S(o, 1) != S(c, 1)))
    ms2u = ((S(o, 2) - S(c, 2) > 0) & (co > 0) & (S(c, 1) - S(o, 1) >= 0) & (S(o, 2) - S(c, 2) > S(h, 2) - S(o, 2))
            & (S(o, 2) - S(c, 2) > S(c, 2) - S(lo, 2)) & (co > h - c) & (co > o - lo) & (co > S(c, 1) - S(o, 1))
            & (S(o, 2) - S(c, 2) > S(c, 1) - S(o, 1)) & (S(c, 1) < S(c, 2)) & (S(c, 1) < o) & (S(o, 1) != S(c, 1)))
    es1d = ((S(c, 2) - S(o, 2) > 0) & (oc > 0) & (S(c, 1) - S(o, 1) >= 0) & (S(c, 2) - S(o, 2) > S(h, 2) - S(c, 2))
            & (S(c, 2) - S(o, 2) > S(o, 2) - S(lo, 2)) & (oc > h - o) & (oc > c - lo) & (oc > S(c, 1) - S(o, 1))
            & (S(c, 2) - S(o, 2) > S(c, 1) - S(o, 1)) & (S(o, 1) > S(c, 2)) & (S(o, 1) > o))
    es2d = ((S(c, 2) - S(o, 2) > 0) & (oc > 0) & (S(o, 1) - S(c, 1) >= 0) & (S(c, 2) - S(o, 2) > S(h, 2) - S(c, 2))
            & (S(c, 2) - S(o, 2) > S(o, 2) - S(lo, 2)) & (oc > h - o) & (oc > c - lo) & (oc > S(o, 1) - S(c, 1))
            & (S(c, 2) - S(o, 2) > S(o, 1) - S(c, 1)) & (S(c, 1) > S(c, 2)) & (S(c, 1) > o) & (S(c, 1) != S(o, 1)))
    # engulfing
    beu = ((S(o, 1) - S(c, 1) > 0) & (co > 0) & (h > S(h, 1)) & (lo < S(lo, 1)) & (co > S(o, 1) - S(c, 1))
           & (co > h - c) & (co > o - lo))
    bed = ((S(c, 1) - S(o, 1) > 0) & (oc > 0) & (h > S(h, 1)) & (lo < S(lo, 1)) & (oc > S(c, 1) - S(o, 1))
           & (oc > h - o) & (oc > c - lo))
    # hammer / falling star
    bhu1 = (co > 0) & (co / 3 > h - c) & ((o - lo) / 2 > co) & (co > (o - lo) / 8)
    bhu2 = (oc > 0) & (oc / 3 > h - o) & ((c - lo) / 2 > oc) & (oc > (c - lo) / 8)
    bfs1 = (co > 0) & (co / 3 > o - lo) & ((h - c) / 2 > co) & (co > (h - c) / 8)
    bfs2 = (oc > 0) & (oc / 3 > c - lo) & ((h - o) / 2 > oc) & (oc > (h - o) / 8)
    buy = (dragon_bear | dragon_bull | tws | tlsu | pu | ms1u | ms2u | beu | bhu1 | bhu2).fillna(False)
    sell = (gravedoji_bear | gravedoji_bull | tbc | tlsd | dc | es1d | es2d | bed | bfs1 | bfs2).fillna(False)
    false = pd.Series(False, index=bars_df.index)
    return (buy & ~sell).astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
