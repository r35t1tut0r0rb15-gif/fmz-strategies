"""Three-line strike candles, always in the market, daily (broker-day) bars: three red bars followed by a larger
green bar that engulfs the previous body goes long; three green bars followed by a larger red bar goes short (the
plain engulfing entries are an off-by-default variant).
Port of FMZ strategy #483050 "基于多重K线形态的三重打击量化交易策略-Multi-Candlestick-Pattern-Based-Triple-Strike-Quantitative-Trading-Strategy" (3 Line Strike [TTF] - Strategy).

FMZ source id: 483050

Source
    https://www.fmz.com/strategy/483050 (PineScript v5, FMZ last modified 2025-02-27 17:12:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 107-254), 3LS on, big-candle (engulfing) entries off, pyramiding 0
    colour = sign(close - open); engulfing = |body| > |previous body| and the colour flips
    3LS bull = previous three bars red and a bullish engulfing bar -> entry long; 3LS bear mirrored -> entry short
    (off by default) bullish / bearish engulfing -> entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The engulfing switch (both directions) is a GRID variant, off as the source's default.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. A long and a short on one bar cannot occur (the bar's
      colour decides). Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as
      #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colours and body sizes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483050_three_line_strike_reversal_1d"
FAMILY = "candlestick"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "use_engulfing": [False, True],
}
DEFAULT_PARAMS = {"use_engulfing": False}


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
    o, c = bars_df["open"], bars_df["close"]
    body = c - o
    col = np.sign(body)
    larger = body.abs() > body.shift(1).abs()
    bull_eng = larger & (col > 0) & (col.shift(1) < 0)
    bear_eng = larger & (col < 0) & (col.shift(1) > 0)
    three_red = (col.shift(1) < 0) & (col.shift(2) < 0) & (col.shift(3) < 0)
    three_green = (col.shift(1) > 0) & (col.shift(2) > 0) & (col.shift(3) > 0)
    long_e = three_red & bull_eng
    short_e = three_green & bear_eng
    if p["use_engulfing"]:
        long_e, short_e = long_e | bull_eng, short_e | bear_eng
    false = pd.Series(False, index=bars_df.index)
    return long_e.astype(bool), false, short_e.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
