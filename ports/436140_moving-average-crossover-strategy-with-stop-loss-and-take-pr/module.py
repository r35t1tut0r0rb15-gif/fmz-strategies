"""SMA 9 / 55 upcrossings with an ATR bracket, broker days, long only: the SMA 9 crossing over the SMA 55 buys, with a stop one ATR under the close and a target twice that
distance over it.
Port of FMZ strategy #436140 "Moving Average Crossover Strategy with Stop Loss and Take Profit" (MA Crossover Strategy with Stop-Loss and Take-Profit).

FMZ source id: 436140

Source
    https://www.fmz.com/strategy/436140 (PineScript v5, FMZ last modified 2023-12-21 15:52:57).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 134-157), SMA 9 / 55; ATR 14; risk : reward 1 : 2
    buy = crossover(sma9, sma55) -> entry long;  exit(loss = close - atr, profit = close + 2 atr)   (loss and profit are in TICKS; the intent is a 1 ATR stop and a 2 ATR target)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels are handed to loss / profit, which count ticks, so the script as typed
      asks for distances of about the price in ticks; the port reads the stated intent: sl_stop = k_atr x ATR
      / close and tp_stop = rr x sl_stop of the signal bar, shifted one bar inside stops() (re-based on the
      fill). The sellCondition is computed and unused. Long only. Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick-typed levels read as the intended ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436140_sma_9_55_cross_atr_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [1.0, 2.0],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"k_atr": 1.0, "rr": 2.0, "short": 9, "long": 55, "atr_len": 14}


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
    c = bars_df["close"]
    f, s = c.rolling(int(p["short"])).mean(), c.rolling(int(p["long"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f * float(p["rr"])}


def portfolio_kwargs(**params):
    return {}
