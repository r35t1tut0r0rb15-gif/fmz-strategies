"""Broker days: the EMA 21 crossing over the EMA 50 on volume above its 20-day average goes long, crossing under on volume BELOW its average goes short; a long closes on any close under either EMA, a short on any close over either; reversing.
Port of FMZ strategy #472935 "Dual EMA Volume Trend Confirmation Strategy for Quantitative Trading" (TATA Swing Trading Strategy with Volume and EMAs).

FMZ source id: 472935

Source
    https://www.fmz.com/strategy/472935 (PineScript v5, FMZ last modified 2024-11-25 11:07:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 89-128), EMA 21 / 50; volume SMA 20
    longCondition = volume > volumeMA and crossover(ema21, ema50) -> entry Long;  shortCondition = volume < volumeMA and crossunder(ema21, ema50) -> entry Short
    close < ema21 or close < ema50 -> close Long;  close > ema21 or close > ema50 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes act only on a position the bar's entries leave unchanged, so they work from the bar
      after the fill; an opposite entry reverses. The short needs volume under its average (as written;
      the long needs it above). REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 21 / 50 crossings with volume filters and EMA exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_472935_ema21_50_cross_volume_ema_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 13],
    "slow": [50, 34],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 50}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    vma = v.rolling(20).mean()
    buy = ((v > vma) & (f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    sell = ((v < vma) & (f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    ex_l = ((c < f) | (c < s)).to_numpy()
    ex_s = ((c > f) | (c > s)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
