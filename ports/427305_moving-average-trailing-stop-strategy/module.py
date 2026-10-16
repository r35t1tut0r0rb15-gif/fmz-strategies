"""XPloRR MA trailing stop, long only, broker days: EMA 12 crossing above SMA 54 while the EMA rises
faster than 52 basis points a day goes long; the long is closed when EMA 18 crosses under SMA 55 while
falling faster than 100 basis points a day, or when EMA 6 falls below a ratchet line kept 8 x the
average range under it.
Port of FMZ strategy #427305 "Moving Average Trailing Stop Strategy".

FMZ source id: 427305

Source
    https://www.fmz.com/strategy/427305 (PineScript v2, FMZ last modified 2023-09-19 21:33:48).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 177-244), EMA 12 / SMA 54 / 52, EMA 18 / SMA 55 / 100, delta 8
    strength = 10000 (ema - ema[1]) / ema[1]
    long = crossover(ema12, sma54) and strength12 > 52; short = crossunder(ema18, sma55) and strength18 < -100
    stopval = ema(close, 6); atr = sma(high - low, 15)
    on entry: stop = stopval - 8 atr; while long: stop = stopval > stop[1] + 8 atr ? stopval - 8 atr : stop[1]
    (short or stopval < stop) and long -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line is checked on the close-based EMA 6, not on prices inside the bar: a
      close-based exit signal from simulate() (rule 2, second half), no mark.
    * `atr` here is the SMA 15 of high - low (the source's own definition).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. The
      test-period inputs are the author's window (testPeriod() is the constant true).
    * Long only; entries only from flat.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is close-based.
    2 generic: PASS, slopes in basis points and range multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427305_xplorr_ma_trailing"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "strength1": [52, 20],
    "strength2": [100, 50],
    "delta": [8, 4],
}
DEFAULT_PARAMS = {"ema1": 12, "sma1": 54, "strength1": 52, "ema2": 18, "sma2": 55, "strength2": 100,
                  "delta": 8, "stop_ema": 6, "range_len": 15}


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
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    s1 = c.rolling(int(p["sma1"])).mean()
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    s2 = c.rolling(int(p["sma2"])).mean()
    st1 = 10000 * (e1 - e1.shift(1)) / e1.shift(1)
    st2 = 10000 * (e2 - e2.shift(1)) / e2.shift(1)
    long_c = ((e1 > s1) & (e1.shift(1) <= s1.shift(1)) & (st1 > p["strength1"])).to_numpy()
    short_c = ((e2 < s2) & (e2.shift(1) >= s2.shift(1)) & (st2 < -p["strength2"])).to_numpy()
    sv = c.ewm(span=int(p["stop_ema"]), adjust=False).mean().to_numpy()
    rng = (bars_df["high"] - bars_df["low"]).rolling(int(p["range_len"])).mean().to_numpy()
    d = float(p["delta"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    inlong, stop = False, 0.0
    for i in range(m):
        was_long = inlong
        if was_long:
            stop = sv[i] - d * rng[i] if sv[i] > stop + d * rng[i] else stop
        if long_c[i] and not was_long:
            le[i], inlong, stop = True, True, sv[i] - d * rng[i]
        if (short_c[i] or sv[i] < stop) and was_long:
            lx[i], inlong, stop = True, False, 0.0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
