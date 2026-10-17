"""Eight-candle colour sequences, always in, martingale sizing not ported, broker days: four red candles, then green,
red, green, red goes long; four... red, red, red, green, red, green, red, green goes short (the exact sequences below);
each entry reverses the other side.
Port of FMZ strategy #489742 "八阶蜡烛模式序列马丁格尔策略-Eight-Candle-Pattern-Sequence-Martingale-Strategy" (SUPRA MTS1).

FMZ source id: 489742

Source
    https://www.fmz.com/strategy/489742 (PineScript v6, FMZ last modified 2025-04-08 10:53:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 193-229), no parameters besides the bet sizing
    green = close > open, red = close < open
    buy = red[7] red[6] red[5] red[4] green[3] red[2] green[1] red;  sell = red[7] red[6] red[5] green[4] red[3] green[2] red[1] green
    entry long on buy, short on sell (strategy.entry reverses); no other exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The martingale bet (doubled after a loss, capped by a capital limit) is sizing: quoted in original_sizing.txt,
      not ported. A doji (close == open) is neither colour, as written.
    * The two sequences differ in the last candle, so they cannot fall on one bar. REVERSAL INTENDED.
    * Criterion 5: the source has no signal parameters; one declared variant (the rule as written): GRID {} (1 trial).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colours only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the martingale bet quoted in original_sizing.txt.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489742_eight_candle_sequence_always_in"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}

BUY_SEQ = ("r", "r", "r", "r", "g", "r", "g", "r")    # oldest [7] ... current [0]
SELL_SEQ = ("r", "r", "r", "g", "r", "g", "r", "g")


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


def _seq(green, red, pattern):
    out = pd.Series(True, index=green.index)
    for k, col in enumerate(pattern):
        lag = 7 - k
        s = (green if col == "g" else red).shift(lag, fill_value=False)
        out &= s.astype(bool)
    return out


def simulate(bars_df, **params):
    o, c = bars_df["open"], bars_df["close"]
    green, red = (c > o), (c < o)
    buy = _seq(green, red, BUY_SEQ)
    sell = _seq(green, red, SELL_SEQ)
    false = pd.Series(False, index=bars_df.index)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
