"""Moving-average band breakouts, broker days: the close above both the previous SMA 20 and SMA 5 plus one ATR(20) band goes long, below both minus the band goes short; a long closes when the close is under
either lower line, a short when it is over either upper line; reversing.
Port of FMZ strategy #442387 "Donchian Adaptive Moving Average Trading System" (唐齐安移动平均交易系统).

FMZ source id: 442387

Source
    https://www.fmz.com/strategy/442387 (PineScript v4, FMZ last modified 2024-02-21 15:08:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-149), long 20, short 5; band factor 1 (ATR = SMA 20 of the true range)
    close > MAlong[1] + band[1] and close > MAshort[1] + band[1] -> entry Long (position < 1);  else close < both - band -> entry Short (position > -1)
    close < MAlong[1] - band[1] or close < MAshort[1] - band[1] -> close Long;  else close > either + band -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band is the SMA 20 of the true range (TrueHigh / TrueLow with the previous close). A close acts
      only on the held position; the close written after a reversing entry leaves the reversal standing (as
      #438020). REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA band breakouts.
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

NAME = "fmz_442387_ma_atr_band_breakout_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_period": [20, 50],
    "band_factor": [1.0, 2.0],
}
DEFAULT_PARAMS = {"long_period": 20, "band_factor": 1.0, "short_period": 5}


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
    pc = c.shift(1)
    th = pd.concat([pc, h], axis=1).max(axis=1).where(pc.notna() & (pc > h), h)
    tl = pd.concat([pc, lo], axis=1).min(axis=1).where(pc.notna() & (pc < lo), lo)
    lp = int(p["long_period"])
    band = ((th - tl).rolling(lp).mean() * float(p["band_factor"])).shift(1)
    ml, ms = c.rolling(lp).mean().shift(1), c.rolling(int(p["short_period"])).mean().shift(1)
    el = ((c > ml + band) & (c > ms + band)).to_numpy()
    es = ((c < ml - band) & (c < ms - band)).to_numpy()
    xl = ((c < ml - band) | (c < ms - band)).to_numpy()
    xs = ((c > ml + band) | (c > ms + band)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        elif es[i] and new != -1:
            new = -1
        if xl[i]:
            if held == 1 and new == 1:
                new = 0
        elif xs[i]:
            if held == -1 and new == -1:
                new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
