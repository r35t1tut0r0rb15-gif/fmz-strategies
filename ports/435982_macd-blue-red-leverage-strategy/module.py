"""Elder Impulse colours, broker days: the EMA 13 and the MACD histogram both rising (green) holds a long, both falling (red) a short; any other
bar (blue) closes the position.
Port of FMZ strategy #435982 "Macd Blue Red Leverage Strategy" (SB_Elder Impulse System).

FMZ source id: 435982

Source
    https://www.fmz.com/strategy/435982 (PineScript v3, FMZ last modified 2023-12-20 15:51:37).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 165-200), EMA 13; MACD 12 / 26 / 9 (SMA signal); chart resolution
    green = ema13 > ema13[1] and hist > hist[1];  red = ema13 < ema13[1] and hist < hist[1];  chk = green ? 1 : red ? -1 : 0;  chk == 1 -> entry long;  chk == -1 -> entry short;  chk == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security at the chart resolution returns the chart's close. The position follows the
      colour every bar; a flip from green to red on one bar is a reversal (REVERSAL INTENDED), a blue bar
      goes flat. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, slope and histogram colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435982_elder_impulse_colours"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ema": [13, 21],
    "fast": [12, 8],
}
DEFAULT_PARAMS = {"length_ema": 13, "fast": 12, "slow": 26, "signal": 9}


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
    ema = c.ewm(span=int(p["length_ema"]), adjust=False).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.rolling(int(p["signal"])).mean()
    green = ((ema > ema.shift(1)) & (hist > hist.shift(1))).fillna(False).to_numpy()
    red = ((ema < ema.shift(1)) & (hist < hist.shift(1))).fillna(False).to_numpy()
    tgt = np.where(green, 1, np.where(red, -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((tgt == 0) & (prev == 1), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((tgt == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
