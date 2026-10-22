"""Double-EMA alignment starts in a 04:00-15:00 UTC session, 1-hour bars: in the session, the first bar of the open above its double EMA 5 above the double EMA 21 goes long; the mirror goes short; the opposite
alignment closes; reversing.
Port of FMZ strategy #440078 "Dual Moving Average Trading Strategy" ([STRATEGY][RS]MA Strategy test V0).

FMZ source id: 440078

Source
    https://www.fmz.com/strategy/440078 (PineScript v2, FMZ last modified 2024-01-26 14:45:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-175), double EMA 5 / 21 of open; session 0400-1500
    osc0 = open - ema(ema(open, 5), 5);  osc1 = ma0 - ema(ema(open, 21), 21);  isbull = both > 0;  buy = in session and isbull and not isbull[1];  close buy when both < 0;  sell / close sell mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session test is read on the bar's UTC open (as #435514; the exchange time zone is UTC):
      04:00 <= open < 15:00. The closes come after their entries: a close of the side just reversed out
      of meets no position and the reversal stands (as #438020); a held position meeting its close ends
      flat, and a sell entry on that bar then opens the short. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, double-EMA alignment and a UTC session.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 04:00-15:00 UTC on the bar open.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440078_double_ema_alignment_session"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length0": [5, 8],
    "length1": [21, 34],
}
DEFAULT_PARAMS = {"length0": 5, "length1": 21, "session_start": 4, "session_end": 15}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o = bars_df["open"]
    n0, n1 = int(p["length0"]), int(p["length1"])
    ma0 = o.ewm(span=n0, adjust=False).mean().ewm(span=n0, adjust=False).mean()
    ma1 = o.ewm(span=n1, adjust=False).mean().ewm(span=n1, adjust=False).mean()
    o0, o1 = o - ma0, ma0 - ma1
    bull = ((o0 > 0) & (o1 > 0)).to_numpy()
    bear = ((o0 < 0) & (o1 < 0)).to_numpy()
    hr = bars_df.index.tz_convert("UTC").hour.to_numpy()
    sess = (hr >= int(p["session_start"])) & (hr < int(p["session_end"]))
    pb = np.concatenate(([False], bull[:-1]))
    pr = np.concatenate(([False], bear[:-1]))
    buy = sess & bull & ~pb
    sell = sess & bear & ~pr
    m = len(o)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and pos != 1:
            new = 1
        if pos == 1 and bear[i] and new == 1:
            new = 0
        if sell[i] and new != -1:
            new = -1
        if pos == -1 and bull[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
