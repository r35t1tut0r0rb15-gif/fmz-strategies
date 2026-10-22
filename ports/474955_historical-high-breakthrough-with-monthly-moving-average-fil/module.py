"""All-time-high breakouts with a monthly-close filter, daily bars, long only: a close over the highest previous high buys; the last completed month's close under its SMA 8 (taken over the daily samples) sells; the signals alternate.
Port of FMZ strategy #474955 "Historical High Breakthrough with Monthly Moving Average Filter Trend Following Strategy" (Buy Signal on Close Greater Than Previous All-Time High Strategy).

FMZ source id: 474955

Source
    https://www.fmz.com/strategy/474955 (PineScript v5, FMZ last modified 2024-12-13 10:25:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-139), prevATH from high[1]; "M" close; SMA 8 over the chart's samples
    na(ath) or high[1] > ath -> ath := high[1];  close > ath and last != buy -> entry Buy, last := buy;  security("M", close) < sma(security("M", close), 8) and last != sell -> close Buy, last := sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The all-time high is the running maximum of previous highs from the first bar of the loaded data
      (a loop). The monthly request (no lookahead) is the last completed broker month's close (as the
      weekly rule #437508: the previous month), and the SMA 8 runs over its daily samples, as written
      (#471719), so it reacts within 8 days of a month change. The last-signal flag makes the signals
      alternate; the close acts only on a long held into the bar (#437773), so a loop follows the
      position. Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed monthly values.
    2 generic: PASS, all-time-high breakouts with a monthly filter exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474955_all_time_high_close_break_monthly_sma8_exit_long"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [8, 4],
}
DEFAULT_PARAMS = {"sma_len": 8}


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
    h, c = bars_df["high"], bars_df["close"]
    hv, cv = h.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    ath = np.full(m, np.nan)
    cur = np.nan
    for i in range(1, m):
        if np.isnan(cur) or hv[i - 1] > cur:
            cur = hv[i - 1]
        ath[i] = cur
    day = broker_day(bars_df.index)
    month = day.to_period("M")
    mclose = c.groupby(month).last()
    prev_m = pd.Series(mclose.shift(1).reindex(month).to_numpy(), index=c.index)   # last completed month
    msma = prev_m.rolling(int(p["sma_len"])).mean()
    buy = cv > ath
    sell = (prev_m < msma).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last, pos, nxt = 0, 0, 0
    for i in range(m):
        pos = nxt
        b = buy[i] and last != 1
        s = sell[i] and last != 2
        if b:
            last = 1
        if s:
            last = 2
        if b and pos == 0:
            le[i], nxt = True, 1
        if s and pos == 1:                       # the close acts only on a long held into the bar
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
