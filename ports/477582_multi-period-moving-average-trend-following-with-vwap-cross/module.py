"""2-hour bars: the SMA 9 crossing over the SMA 50 with the SMA 200 below the SMA 50 and the close above the session VWAP goes long, the mirror goes short; a long closes on the SMA 9 crossing back under the SMA 50, a short on crossing back over; reversing.
Port of FMZ strategy #477582 "Multi Period Moving Average Trend Following with VWAP Cross Strategy" (SMA Crossover Strategy with VWAP).

FMZ source id: 477582

Source
    https://www.fmz.com/strategy/477582 (PineScript v5, FMZ last modified 2025-01-06 15:30:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 152-192), SMA 9 / 50 / 200; session VWAP
    longCondition = crossover(sma9, sma50) and sma200 < sma50 and close > vwap -> entry Long;  crossunder(sma9, sma50) -> close Long
    shortCondition = crossunder(sma9, sma50) and sma200 > sma50 and close < vwap -> entry Short;  crossover(sma9, sma50) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.vwap(close) restarts each session: the house session is the broker day (17:00
      America/New_York), so the VWAP is the volume-weighted close of the day's 2-hour bars so far, each
      bar placed in the broker day of its start. A crossing bar closes the other side and, when its
      filters hold, opens this side (a reversal); otherwise it only closes. REVERSAL INTENDED. No sizing
      code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA 9 / 50 crossings in the SMA 200 trend with a session-VWAP filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477582_sma9_50_cross_sma200_session_vwap_2h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 20],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 50, "trend": 200}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    t = c.rolling(int(p["trend"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    buy = (up & (t < s) & (c > vw)).to_numpy()
    sell = (dn & (t > s) & (c < vw)).to_numpy()
    upn, dnn = up.to_numpy(), dn.to_numpy()
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
            if pos == 1 and dnn[i]:
                new = 0
            elif pos == -1 and upn[i]:
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
