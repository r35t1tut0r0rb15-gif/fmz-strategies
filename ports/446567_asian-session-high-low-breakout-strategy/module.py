"""Contrarian breaks of the 19:00-01:00 UTC session range, 1-hour bars, one trade per session: from 04:00 UTC, a close under the session low goes long and a close over the session high goes short; reversing
(the 300-tick bracket re-sent from each close is not ported).
Port of FMZ strategy #446567 "Asian Session High Low Breakout Strategy" (Asia Session (high / low breakout)).

FMZ source id: 446567

Source
    https://www.fmz.com/strategy/446567 (PineScript v4, FMZ last modified 2024-03-29 17:12:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-175), session 19:00-01:00 (exchange time); entries from 01:00 + 3 h; stop / target 300 ticks from each bar's close; one trade per session
    inSession = hour >= 19 or hour < 1;  lo / hi = running session low / high (reset after the session);  asiaLow / asiaHigh = lo / hi while in session (kept after)
    not tradeOpened and close < asiaLow and hour >= 4 -> entry Buy, tradeOpened;  not tradeOpened and close > asiaHigh and hour >= 4 -> entry Sell;  tradeOpened resets when a session starts
    exit(Buy / Sell, stop = close -+ 300 ticks, limit = close +- 300 ticks)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour is read on the bar's UTC open time (the exchange time zone, as #435514). The session range
      is the 19:00-00:59 bars' high / low; inside the session the range includes the current bar, so an
      entry can only come from 04:00 to 18:59. The bracket is re-sent on every bar at 300 ticks from
      that bar's close, so it moves after entry: not ported (mark trailing_stop_pending; as #438034;
      300 ticks of 0.1 = 30 price units, about 0.2 ATR at the 1-hour reading when expressed).
      Positions end at the next session's opposite entry meanwhile. The trade counter (limit 100000)
      and operationClosed never block. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the session range from completed bars; the moving bracket not ported (mark).
    2 generic: PASS, contrarian session-range breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the 300-tick bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 19:00-01:00 UTC session; entries from 04:00 UTC (exchange time zone, no DST).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_446567_asia_session_range_contrarian_break_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "session_start": [19, 22],
    "offset_hours": [3, 6],
}
DEFAULT_PARAMS = {"session_start": 19, "session_stop": 1, "offset_hours": 3}


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
    ix = bars_df.index
    hr = np.asarray(ix.hour)
    s0, s1 = int(p["session_start"]), int(p["session_stop"])
    ins = (hr >= s0) | (hr < s1)
    gate = hr >= s1 + int(p["offset_hours"])
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    cv = bars_df["close"].to_numpy(dtype=float)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lo = hi = np.nan
    a_lo = a_hi = np.nan
    opened = False
    prev_in = False
    for i in range(m):
        entering = ins[i] and not prev_in
        exiting = (not ins[i]) and prev_in
        if ins[i]:
            lo = min(lv[i], 1.0e23 if np.isnan(lo) else lo)
            hi = max(hv[i], 0.0 if np.isnan(hi) else hi)
        if exiting:
            lo = hi = np.nan
        if ins[i]:
            a_lo, a_hi = lo, hi
        if entering:
            opened = False
        if not opened and cv[i] < a_lo and gate[i]:
            le[i], opened = True, True
        if not opened and cv[i] > a_hi and gate[i]:
            se[i], opened = True, True
        prev_in = ins[i]
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
