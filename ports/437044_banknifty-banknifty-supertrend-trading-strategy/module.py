"""Supertrend side state, 1-hour bars: once ten bars have formed, the Supertrend (ATR 50 x 3) in uptrend is long and in downtrend short, entries sent on every bar of the state, reversing; the author's stop
(re-placed every bar 100 points from the latest close, with a percent trail) is described, not emitted.
Port of FMZ strategy #437044 "BankNifty超级趋势交易策略BankNifty-Supertrend-Trading-Strategy" (BankNifty 5min Supertrend Based Strategy).

FMZ source id: 437044

Source
    https://www.fmz.com/strategy/437044 (PineScript v5, FMZ last modified 2023-12-29 17:09:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 157-212), ATR 50, factor 3; session 0915-1510 (overridden: inSession = true); delay 10 candles; stop 100 points, trail 0.1 x average price
    [supertrend, direction] = supertrend(3, 50);  candlesFormed counts bars since the session start (inSession is always true)
    entryce = change(direction) < 0 or (candlesFormed >= 10 and direction < 0) -> entry long, exit(stop = close - 100, trail_points = avg x 0.1);  entrype = the mirror -> entry short, exit(stop = close + 100, ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * inSession is hard-coded true, so the session input never acts and candlesFormed simply counts bars
      from the data start: the first nine bars trade only on a direction change. The exit is re-sent on
      every bar of the state with entryPrice = that bar's close (100 points; trail_points = 10 % of the
      average price before the entry, na when flat): a level that moves after entry, so stops() cannot
      express it; kept pending (rule 2, mark trailing_stop_pending; points -> ATR multiples when it is
      expressed: 100 points against a 1-hour BTC ATR near 150, about 0.7 ATR). Positions end at the
      opposite entry until then. The BankNifty title names an instrument; the rules are generic. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, Supertrend side; the point stop is pending.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point stop and trail inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the session input is overridden by inSession = true).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_437044_supertrend_side_state_delay"
FAMILY = "supertrend"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [50, 20],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_period": 50, "factor": 3.0, "delay": 10}


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


def _supertrend_dir(h, lo, c, factor, n):
    """Direction of Pine's supertrend(factor, atrPeriod): -1 uptrend, 1 downtrend, nan before the ATR."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    d = np.full(m, np.nan)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
            continue
        if i == 0 or np.isnan(atr[i - 1]):
            up_dir = False
        elif st[i - 1] == ub[i - 1]:
            up_dir = cv[i] > ub[i]
        else:
            up_dir = not (cv[i] < lb[i])
        st[i] = lb[i] if up_dir else ub[i]
        d[i] = -1.0 if up_dir else 1.0
    return pd.Series(d, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d = _supertrend_dir(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    ch = d.diff()
    formed = pd.Series(np.arange(1, len(c) + 1), index=c.index) >= int(p["delay"])
    long_s = (ch < 0) | (formed & (d < 0))
    short_s = (ch > 0) | (formed & (d > 0))
    false = pd.Series(False, index=bars_df.index)
    return long_s, false, short_s, false.copy()


def portfolio_kwargs(**params):
    return {}
