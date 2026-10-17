"""Buy the dip with an ATR bracket, broker days, long only: a close under the lowest low of the previous 7 days goes long;
the trade carries a stop 2 ATR and a target 1 ATR from the entry price, the ATR being the 15-day average true range up
to the signal day, fixed at entry.
Port of FMZ strategy #433022 "Buying dips with take profit and stop loss" (Buy-The-Dip).

FMZ source id: 433022

Source
    https://www.fmz.com/strategy/433022 (PineScript v4, FMZ last modified 2023-11-23 16:50:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-172), ATR = sma(tr, 15)[1], stop 2 ATR, target 1 ATR (the code's default), channel 7
    close < lowest(low, 7)[1] -> entry long
    exit(stop = avg - 2 atr, limit = avg + 1 atr), both fixed by valuewhen(bought, ...) on the fill bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the fill bar atr = sma(tr, 15)[1] is the average up to the signal bar, so the bracket is
      sl_atr / tp_atr x sma(tr, 15) / close of the signal bar, shifted one bar inside stops() and
      re-based on the fill (the source measures from the fill price itself).
    * A further dip while long is ignored (pyramiding 1). Long only; Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; stops on daily bars: mark coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, a channel break and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_433022_buy_the_dip_atr_bracket"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [2.0, 1.0],
    "tp_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"atr_len": 15, "channel": 7, "sl_atr": 2.0, "tp_atr": 1.0}


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


def _af(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    return tr.rolling(int(p["atr_len"])).mean() / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    le = (c < lo.rolling(int(p["channel"])).min().shift(1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _af(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
