"""Seven same-colour candles, 10-minute bars: seven red candles in a row go long, seven green ones go short (reversing); every position
is closed at 05:00, 11:00, 17:00 and 23:00 exchange time (UTC for the backtest's exchange).
Port of FMZ strategy #435514 "Seven Candlestick Oscillation Breakthrough Strategy" (Breakeven Line Demo).

FMZ source id: 435514

Source
    https://www.fmz.com/strategy/435514 (PineScript v5, FMZ last modified 2023-12-15 16:14:32).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 139-147), seven red / green candles; close_all at hour 5, 11, 17 and 23, minute 0
    sevenReds = open > close for 7 bars;  sevenGreens = open < close for 7 bars;  sevenReds -> entry long;  sevenGreens -> entry short
    (hour == 5 or 11 or 17 or 23) and minute == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule (checks 6 / 9 of the skill do not apply: no venue open): the closes fire on the
      10-minute bar that OPENS at 05:00, 11:00, 17:00 or 23:00 UTC (the exchange time zone of the
      Binance backtest; UTC has no daylight saving), filled at the next open. On such a bar the
      entry order and the close order are both sent and the close wins: the position ends flat. A
      long streak re-enters on the next bar. strategy.entry reverses: REVERSAL INTENDED. FREQ =
      "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, clock-time closes in the exchange time zone (UTC).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: clock closes at 05:00, 11:00, 17:00, 23:00 UTC (the backtest exchange's time zone; no DST); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435514_seven_candles_clock_close"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [7, 5, 9],
}
DEFAULT_PARAMS = {"n": 7}
CLOCK_HOURS_UTC = (5, 11, 17, 23)   # the script's hours in the exchange time zone (UTC)


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["n"])
    red = (o > c).astype(int).rolling(n).sum() == n
    green = (o < c).astype(int).rolling(n).sum() == n
    ix = bars_df.index
    clock = np.isin(ix.hour, CLOCK_HOURS_UTC) & (ix.minute == 0)
    rv, gv = red.to_numpy(), green.to_numpy()
    m = len(rv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if clock[i]:
            q = 0
        elif rv[i]:
            q = 1
        elif gv[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((tgt == 0) & (prev == 1), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((tgt == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
