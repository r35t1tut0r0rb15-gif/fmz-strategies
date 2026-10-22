"""SMA 14 / 28 state, broker days, long only (the default type): while the SMA 14 is at or above the SMA 28 the script holds a long, otherwise it closes; a 2 % stop from the entry and a trailing take
profit that starts 1.2 % up and trails a quarter of the price behind.
Port of FMZ strategy #440864 "Dual Moving Average Reversal Strategy" (A061ZigTuto).

FMZ source id: 440864

Source
    https://www.fmz.com/strategy/440864 (PineScript v4, FMZ last modified 2024-02-02 17:37:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 319-860), Long Only; stop loss 2 % on; take profit off; trailing take profit on (trigger 1.2 %, offset 25 % of the trigger base price, in ticks); 25 % of capital; 6-minute order spacing
    LONG = sma14 >= sma28 (and not too recent);  LONG_CLOSE = not LONG;  Long Only: LONG -> entry [B], else LONG_CLOSE -> close [B]
    strategy.exit("[SL/TP]", "[B]", stop = position price x 0.98, trail_price = position price x 1.012, trail_offset = floor(position price x 1.012 x 0.25 / mintick))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are a level: an entry while long does nothing, and after a stop the next bar re-enters
      while the averages agree. The 6-minute order spacing never binds on daily bars. The stop is a
      fixed fraction of the entry: sl_stop 0.02. The trailing take profit activates 1.2 % above the
      entry and then trails about 25 % of the price behind the best price: the house trail {"type":
      "percent", "pct": 0.253, "anchor": "high_low", "activate_after": 0.012} (stated approximation, as
      #437390; the script's offset is a fixed price distance; mark trailing_stop); the tighter of the two
      applies. The Zignaly alert texts, capital and commission settings are not ported (sizing and
      costs). Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, SMA state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital, percent-of-capital orders and commission settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440864_sma14_28_state_long_stop_trail"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss": [0.02, 0.05],
    "trail_trigger": [0.012, 0.03],
}
DEFAULT_PARAMS = {"stop_loss": 0.02, "trail_trigger": 0.012, "trail_pct": 0.253, "fast": 14, "slow": 28}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    lg = f >= s
    false = pd.Series(False, index=c.index)
    return lg, ~lg & s.notna(), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_loss"]),
            "trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["trail_trigger"])}}


def portfolio_kwargs(**params):
    return {}
