"""Hourly bars: the EMA 8 crossing over the EMA 50 while the EMA 50 is above the session VWAP, on a bar opening 07:30 to 14:30 UTC, goes long; the crossing under with the EMA 50 below the VWAP goes short; the opposite crossing closes the trade at any hour; reversing.
Port of FMZ strategy #489639 "Multi EMA and VWAP Trend Confirmation Analysis System" (LUX CLARA - EMA + VWAP (No ATR Filter) - v6).

FMZ source id: 489639

Source
    https://www.fmz.com/strategy/489639 (PineScript v6, FMZ last modified 2025-04-07 11:45:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 131-181), EMA 8 / 50; session VWAP of close; session "0730-1430" (exchange time); 100 % of equity
    longEntry = crossover(ema8, ema50) and ema50 > vwap and in session -> entry Long;  shortEntry = crossunder(ema8, ema50) and ema50 < vwap and in session -> entry Short
    crossunder(ema8, ema50) -> close Long;  crossover(ema8, ema50) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * time(timeframe.period, "0730-1430") is read in UTC (the header's exchange time); a bar is in the
      session when it opens inside it, so on hourly bars stamped on the hour the bars opening 08:00 to
      14:00 trade (the comment says 7:30-11:30; the code says 14:30). The closes act only on a position the
      bar's entries leave unchanged, so a crossing inside the session with the VWAP test reverses and one
      outside it closes. ta.vwap(close) restarts each session: the house session is the broker day (17:00
      America/New_York). REVERSAL INTENDED. 100 % of equity is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings in the direction of the EMA 50 against the VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: entries on bars opening 07:30 to 14:30 UTC (header exchange time); VWAP reset on the broker day (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489639_ema8_50_cross_vs_session_vwap_0730_1430_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 13],
    "slow": [50, 34],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 50, "sess_start_min": 450, "sess_end_min": 870}


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
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    slow = c.ewm(span=int(p["slow"]), adjust=False).mean()
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    ix = bars_df.index
    mins = np.asarray(ix.hour * 60 + ix.minute)
    sess = (mins >= int(p["sess_start_min"])) & (mins < int(p["sess_end_min"]))
    up_x = ((fast > slow) & (fast.shift(1) <= slow.shift(1))).to_numpy()
    dn_x = ((fast < slow) & (fast.shift(1) >= slow.shift(1))).to_numpy()
    buy = up_x & (slow > vw).to_numpy() & sess
    sell = dn_x & (slow < vw).to_numpy() & sess
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
            if pos == 1 and dn_x[i]:
                new = 0
            elif pos == -1 and up_x[i]:
                new = 0
        if new != pos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
