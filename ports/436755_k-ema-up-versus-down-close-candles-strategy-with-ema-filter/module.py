"""Up-versus-down close count with an EMA filter in two clock windows, 1-hour bars: inside 09:00-12:00 or 13:00-16:00 UTC, more up closes than down closes over the last 20 bars with the close above the EMA 50 goes long,
the mirror goes short; one entry per side change (the signal flag), reversing.
Port of FMZ strategy #436755 "基于K线收盘价多空比较与EMA过滤的量化交易策略Up-versus-Down-Close-Candles-Strategy-with-EMA-filter-and-Session-Timeframes" (UvD Strat EMA Session).

FMZ source id: 436755

Source
    https://www.fmz.com/strategy/436755 (PineScript v5, FMZ last modified 2023-12-27 14:38:28).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 139-182), lookback 20, EMA 50, sessions 0900-1200 and 1300-1600
    upCloseCount / downCloseCount = number of close[i] > close[i+1] / close[i] < close[i+1] for i = 0 .. 19;  inSession = time(period, session1) or time(period, session2)
    long = inSession and up > down and close > ema and currentSignal != "long" -> entry Buy;  short = inSession and down > up and close < ema and currentSignal != "short" -> entry Sell;  close Sell / Buy when the flag disagrees with the position

Interpretation choices (Pine rules in SURVEY_README.md)
    * The count includes the current bar's change; changes before the first bar count as neither (Pine's
      na comparisons are false). The session strings use the backtest exchange's time zone (UTC, no DST):
      a 1-hour bar is in a window when it opens at 09:00, 10:00, 11:00, 13:00, 14:00 or 15:00 UTC. The
      currentSignal flag allows one entry per side change; the two strategy.close lines only close a
      position the reversing entry already closes, so they add nothing. ta.ema is seeded with the first
      close. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, close counts and EMA side inside fixed UTC clock windows.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:00-12:00 and 13:00-16:00 UTC (the backtest exchange's time zone; no DST); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436755_up_down_close_count_sessions"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [20, 30],
    "ema_period": [50, 100],
}
DEFAULT_PARAMS = {"lookback": 20, "ema_period": 50, "s1_start": 540, "s1_end": 720, "s2_start": 780,
                  "s2_end": 960}  # windows in minutes after 00:00 UTC


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
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    d = c.diff()
    n = int(p["lookback"])
    up = (d > 0).astype(float).rolling(n, min_periods=1).sum()
    dn = (d < 0).astype(float).rolling(n, min_periods=1).sum()
    ix = bars_df.index.tz_convert("UTC")
    t = pd.Series(ix.hour * 60 + ix.minute, index=bars_df.index)
    ins = (((t >= p["s1_start"]) & (t < p["s1_end"])) | ((t >= p["s2_start"]) & (t < p["s2_end"])))
    lc = (ins & (up > dn) & (c > ema)).to_numpy()
    sc = (ins & (dn > up) & (c < ema)).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cur = 0
    for i in range(m):
        if lc[i] and cur != 1:
            le[i] = True
            cur = 1
        elif sc[i] and cur != -1:
            se[i] = True
            cur = -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
