"""Bollinger fall-back entries with a six-hour pause, 1-hour bars, long only: the close crossing under the upper band (25, 2 sd) buys unless a
position changed in the last six hours; a 1 % stop and a close over +2 % of the entry price close the long.
Port of FMZ strategy #435869 "Bollinger Band Breakout Trading Strategy" (I11L OIL Bot).

FMZ source id: 435869

Source
    https://www.fmz.com/strategy/435869 (PineScript v5, FMZ last modified 2023-12-19 14:08:45).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 128-166), Bollinger 25 / 2 sd; risk 1 %, take-profit factor 2; six-hour pause after any position change
    isBuy = crossunder(close, upper);  pause: disabled = true after any change of position_size, false again once time > last change + 6 h;  isBuy and not disabled -> entry long
    long: exit(stop = avg 0.99);  close long when close > avg (1 + 0.01 2)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pause is a TIME difference from the last position change (not a clock time): it is
      followed inside simulate with the bar times, and a stop-out inside the bar counts as a change on
      that bar (the bracket is followed as in the house stop engine: the stop is checked from the
      fill bar on). The take-profit rule is a rule on bar closes (close over avg x 1.02), filled at the
      next open: a close-based exit signal, not a broker target. The stop is a fraction of the fill price
      (sl_stop 0.01). The cash size and leverage are sizing. Long only. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-hour bars: not coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: REVIEW, the pause is relative to the last position change.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash size, leverage and risk inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435869_bollinger_fallback_long_pause"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [25, 40],
    "dev_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"lookback": 25, "dev_mult": 2.0, "sl": 0.01, "tp_factor": 2.0, "pause_hours": 6}


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
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    upper = c.rolling(n).mean() + float(p["dev_mult"]) * c.rolling(n).std(ddof=0)
    is_buy = ((c < upper) & (c.shift(1) >= upper.shift(1))).fillna(False).to_numpy()
    ov, lv, cv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    secs = (bars_df.index - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)
    t = np.asarray(secs, dtype=np.int64)
    sl, tp_factor = float(p["sl"]), float(p["tp_factor"])
    pause = int(p["pause_hours"]) * 3600
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, avg = 0, np.nan
    pend_enter = pend_exit = False
    disabled, last_change = False, -(10 ** 18)
    prev_pos = 0
    for i in range(m):
        if pend_enter and pos == 0:
            pos, avg = 1, ov[i]
        elif pend_exit and pos == 1:
            pos, avg = 0, np.nan
        pend_enter = pend_exit = False
        if pos == 1 and lv[i] <= avg * (1 - sl):          # the house stop, checked from the fill bar on
            pos, avg = 0, np.nan
        if t[i] > last_change + pause:
            disabled = False
        if pos != prev_pos:
            disabled, last_change = True, t[i]
        prev_pos = pos
        if is_buy[i] and not disabled:
            le[i] = True
            if pos == 0:
                pend_enter = True
        if pos == 1 and cv[i] > avg * (1 + sl * tp_factor):
            lx[i] = True
            pend_exit = True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
