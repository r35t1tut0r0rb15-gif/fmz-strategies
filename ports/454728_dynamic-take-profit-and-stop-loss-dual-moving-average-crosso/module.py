"""SMA 50 / 100 crossings, 1-hour bars: the cross up goes long and the cross down goes short; a close 5 % in favour or 3 % against the signal close (levels reset by each signal) closes; reversing.
Port of FMZ strategy #454728 "Dynamic Take Profit and Stop Loss Dual Moving Average Crossover Trading Strategy" (TSLA 1-Hour SMA Crossover Strategy with Buy/Sell Signals).

FMZ source id: 454728

Source
    https://www.fmz.com/strategy/454728 (PineScript v5, FMZ last modified 2024-06-21 14:02:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-174), SMA 50 / 100; take profit 5 %, stop 3 % of the signal close (close tests)
    crossover -> levels from the close, entry Long;  crossunder -> levels from the close, entry Short
    long and (close >= tp or close <= sl) -> close Long;  short and (close <= tp or close >= sl) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are bar-close tests on the close, filled at the next open, against the latest
      signal's close. On a reversal bar the levels are already the new side's, and the old side's close
      test then finds the trade reversed and does nothing. REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop / target are close tests.
    2 generic: PASS, SMA crossings with close-test exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454728_sma50_100_cross_close_test_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [50, 20],
    "long_len": [100, 200],
    "tp_pct": [0.05, 0.10],
}
DEFAULT_PARAMS = {"short_len": 50, "long_len": 100, "tp_pct": 0.05, "sl_pct": 0.03}


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
    a = c.rolling(int(p["short_len"])).mean()
    b = c.rolling(int(p["long_len"])).mean()
    buy = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    sell = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp, sl = float(p["tp_pct"]), float(p["sl_pct"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, tpl, sll = 0, np.nan, np.nan
    for i in range(m):
        cur = pos
        if buy[i]:
            tpl, sll = cv[i] * (1 + tp), cv[i] * (1 - sl)
            if cur != 1:
                cur = 1
        if sell[i]:
            tpl, sll = cv[i] * (1 - tp), cv[i] * (1 + sl)
            if cur != -1:
                cur = -1
        if pos > 0 and cur == 1 and (cv[i] >= tpl or cv[i] <= sll):
            cur = 0
        if pos < 0 and cur == -1 and (cv[i] <= tpl or cv[i] >= sll):
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
