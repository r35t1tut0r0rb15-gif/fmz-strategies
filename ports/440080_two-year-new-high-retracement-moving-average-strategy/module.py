"""Pullbacks to the EMA 13 / 21 zone near a two-year high, long only, 1-hour bars: a low reaching between the EMA 21 and the EMA 13 while the EMA 13 is within 10 % of the 504-bar high goes long; a close 5 %
under the EMA 21 or 20 % under that high closes.
Port of FMZ strategy #440080 "Two Year New High Retracement Moving Average Strategy" (AMRS_LongOnly_PartTimer).

FMZ source id: 440080

Source
    https://www.fmz.com/strategy/440080 (PineScript v4, FMZ last modified 2024-01-26 14:49:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-196), EMA 11 / 13 / 21 (11 unused); 504-bar high; start 2000 (open), end 2021-06-03
    TrigLow = low <= ema13 and low >= ema21 and (b - ema13) / b x 100 <= 10 (b = highest(high, 504)[1]) -> entry Long
    stopprice = close <= ema21 x 0.95 ? that : 0, then close <= b x 0.8 ? that;  exit(stop = stopprice) every bar;  close_all on every bar with time >= 2021-06-03

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop sits at 0 (never reached) until the close falls under one of the two levels; it is then
      placed at a level at or above the close, on the wrong side of the market, so it fills at the next
      open: the port closes on that bar's signal. The close_all from 3 Jun 2021 onward is the author's
      backtest window ("beforeEndDate" is true after that date): dropped, as earlier date windows. The
      entry and the close act on the position held at the bar close. Long only. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the wrong-side stop read as a close signal.
    2 generic: PASS, EMA zone, two-year high and percent levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440080_two_year_high_ema_zone_pullback_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "high_len": [504, 252],
    "var_max": [10.0, 5.0],
}
DEFAULT_PARAMS = {"high_len": 504, "var_max": 10.0}


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
    lo, c = bars_df["low"], bars_df["close"]
    e13 = c.ewm(span=13, adjust=False).mean()
    e21 = c.ewm(span=21, adjust=False).mean()
    b = bars_df["high"].rolling(int(p["high_len"])).max().shift(1)
    var = (b - e13) / b * 100
    trig = ((lo <= e13) & (lo >= e21) & (var <= float(p["var_max"]))).to_numpy()
    out = ((c <= e21 * 0.95) | (c <= b * 0.8)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1:
            if out[i]:
                lx[i], pos = True, 0
        elif trig[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
