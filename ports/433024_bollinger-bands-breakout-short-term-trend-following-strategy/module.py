"""Bollinger breakouts with a volatility filter, broker days: with the 15-day stdev of closes above its 15-day average, a
close crossing above the upper band (SMA 15, 2 sd) goes long and a close crossing under the lower band goes short; the
opposite band cross closes each side. Every trade also carries a 2 % stop, a 9 % target and a trail that starts after
2 % of profit and follows 0.5 % behind the best price.
Port of FMZ strategy #433024 "Bollinger Bands Breakout short term trend following Strategy" (Bollinger Bands - Breakout Strategy).

FMZ source id: 433024

Source
    https://www.fmz.com/strategy/433024 (PineScript v5, FMZ last modified 2023-11-23 17:01:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 208-341), BB 15 / 2; trend filter off (EMA 223); volatility filter on (stdev 15 > its SMA 15); ROC filter off; SL 2 %, TP 9 %, trail threshold 2 %, offset 0.5 %
    entryLong = crossover(close, upper) and stdev(close, 15) > sma(stdev(close, 15), 15);  entryShort = crossunder(close, lower) and the same
    exitLong = crossunder(close, lower);  exitShort = crossover(close, upper)
    exit(stop = avg (1 -/+ 2 %), limit = avg (1 +/- 9 %), trail_points = 2 % of close, trail_offset = 0.5 % of close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail activates after a profit of 2 % and then trails 0.5 % behind the best high (low for
      shorts): ported natively (mark trailing_stop) as {"type": "percent", "pct": 0.005, "anchor":
      "high_low", "activate_after": 0.02}, with sl_stop 0.02 and tp_stop 0.09. Stated approximation:
      the source sizes the trail distances from each bar's close in ticks (re-issued every bar), the
      house from the fill price (as #430671).
    * The exit cross of one side is the entry cross of the other, so a band cross reverses: REVERSAL
      INTENDED. The crosses are the signals (no held state), so after a stop, target or trail exit
      the next qualifying cross enters again (corrected in batch C58). The daily-close ROC filter and
      the trend filter are off by default; the max-intraday-loss input and the monthly results table
      are not trading rules.
    * Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; stops on daily bars: mark coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket and a house trail (approximation stated).
    2 generic: PASS, band crosses, a stdev filter and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the exit percentages quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_433024_bb_breakout_vol_filter_trail"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_len": [15, 30],
    "trail_pct": [0.005, 0.02],
}
DEFAULT_PARAMS = {"bb_len": 15, "bb_dev": 2.0, "vol_len": 15, "vol_ma": 15, "sl_pct": 0.02, "tp_pct": 0.09,
                  "trail_pct": 0.005, "activate": 0.02}


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
    n = int(p["bb_len"])
    mid = c.rolling(n).mean()
    dev = float(p["bb_dev"]) * c.rolling(n).std(ddof=0)
    up, dn = mid + dev, mid - dev
    sd = c.rolling(int(p["vol_len"])).std(ddof=0)
    vol_ok = sd > sd.rolling(int(p["vol_ma"])).mean()
    xo_up = ((c > up) & (c.shift(1) <= up.shift(1))).to_numpy()
    xu_dn = ((c < dn) & (c.shift(1) >= dn.shift(1))).to_numpy()
    vo = vol_ok.to_numpy()
    # the band crosses themselves are the signals (no held state), so after a stop, target or
    # trail exit the next qualifying cross enters again; a cross that opens the other side
    # reverses on its own, and a plain exit is emitted only when it does not
    ix = bars_df.index
    le, se = xo_up & vo, xu_dn & vo
    return (pd.Series(le, index=ix), pd.Series(xu_dn & ~se, index=ix),
            pd.Series(se, index=ix), pd.Series(xo_up & ~le, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"]),
            "trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
