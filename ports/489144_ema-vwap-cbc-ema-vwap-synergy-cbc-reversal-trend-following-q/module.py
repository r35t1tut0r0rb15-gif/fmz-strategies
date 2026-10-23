"""Hourly bars: a "CBC" state flips up when a close tops the previous high and down when a close breaks the previous low; from flat, an up-flip with the close, EMA 9 and EMA 20 above the session VWAP and EMA 9 over EMA 20 goes long, the mirror short; the opposite flip closes the trade.
Port of FMZ strategy #489144 "EMA-VWAP协同CBC反转趋势跟踪量化交易策略-EMA-VWAP-Synergy-CBC-Reversal-Trend-Following-Quantitative-Trading-Strategy" (EMA-VWAP Synergy CBC Reversal Trend Following Quantitative Trading Strategy).

FMZ source id: 489144

Source
    https://www.fmz.com/strategy/489144 (PineScript v6, FMZ last modified 2025-04-02 10:31:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 215-318), EMA 9 / 20 (EMA 200 plotted only); session VWAP of close; CBC flip; previous-day and Monday levels plotted only; 100 % of equity
    cbc: true -> false on close < low[1], false -> true on close > high[1];  cbc_long / cbc_short = the flips
    longCondition = cbc_long and close > vwap and ema9 > ema20 and both EMAs > vwap -> entry Long if not in a position;  shortCondition mirrored
    cbc_short and inLong -> close Long;  cbc_long and inShort -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's own flags track the position exactly (there are no stops), so entries come only from
      flat and each trade closes on the opposite flip, at the next open. The daily security values and
      the Monday high / low are drawn but never traded. ta.vwap(close) restarts each session: the house
      session is the broker day (17:00 America/New_York). Opposite entries cannot occur (entries only from
      flat). 100 % of equity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close-beyond-previous-bar flips in the EMA and VWAP trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
Opposite entries cannot occur (entries only from flat; the opposite flip closes the trade).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489144_cbc_flip_ema9_20_session_vwap_flip_exit_1h"
FAMILY = "breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "middle": [20, 30],
}
DEFAULT_PARAMS = {"fast": 9, "middle": 20}


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
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    mid = c.ewm(span=int(p["middle"]), adjust=False).mean()
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    bull = ((c > vw) & (f > mid) & (f > vw) & (mid > vw)).to_numpy()
    bear = ((c < vw) & (f < mid) & (f < vw) & (mid < vw)).to_numpy()
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cbc, pos = False, 0
    for i in range(m):
        prev = cbc
        if i > 0:
            if cbc and cn[i] < ln[i - 1]:
                cbc = False
            if not cbc and cn[i] > hn[i - 1]:
                cbc = True
        flip_up, flip_dn = cbc and not prev, (not cbc) and prev
        if i + 1 >= m:
            continue
        if pos == 0:
            if flip_up and bull[i]:
                le[i], pos = True, 1
            elif flip_dn and bear[i]:
                se[i], pos = True, -1
        elif pos == 1 and flip_dn:
            lx[i], pos = True, 0
        elif pos == -1 and flip_up:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
