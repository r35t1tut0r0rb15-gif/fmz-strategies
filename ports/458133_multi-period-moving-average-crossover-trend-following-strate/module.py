"""SMA 20 / 50 crossings with an SMA 200 filter, bar size from the search: the cross up with the close over the SMA 200 goes long, the cross down with the close under it goes short; a long closes on the cross down or a close under the signal bar's low, a short on the mirror; reversing.
Port of FMZ strategy #458133 "Multi Period Moving Average Crossover Trend Following Strategy" (MA Ribbon Orders).

FMZ source id: 458133

Source
    https://www.fmz.com/strategy/458133 (PineScript v5, FMZ last modified 2024-07-30 10:54:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-257), SMA 20 / 50 / 100 / 200 (type SMA by default; the 100 only plotted); stop levels low / high of the signal bar (close tests)
    crossover(ma1, ma2) and close > ma4 -> stop_long = low, entry Long;  crossunder and close < ma4 -> stop_short = high, entry Short
    crossunder(ma1, ma2) or close < stop_long -> exit(Long, stop = stop_long) + close Long;  crossover or close > stop_short -> exit(Short, stop = stop_short) + close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. The
      exits are bar-close tests: the market close and the stop sent with it both fill at the next open
      (the stop is at or through the market when the close test holds, or below it on a cross), so the
      exit is a next-open close. The stop levels are kept from the last signal and never reset, so an
      exit order sent while flat may in Pine wait for the next entry; that is not followed (only a held
      position is closed). Entries are called before the exits; a close acts only on a position held
      into the bar and not being reversed (#437773). REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop levels as close tests.
    2 generic: PASS, SMA crossings with a long-average filter and signal-bar stops.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458133_sma20_50_cross_sma200_filter_signal_bar_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # no backtest header: the driver supplies bar_size
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [20, 10],
    "ma2": [50, 30],
    "ma4": [200, 100],
}
DEFAULT_PARAMS = {"ma1": 20, "ma2": 50, "ma4": 200}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a, b = c.rolling(int(p["ma1"])).mean(), c.rolling(int(p["ma2"])).mean()
    d = c.rolling(int(p["ma4"])).mean()
    xo = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    xu = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    buy = xo & (c > d).to_numpy()
    sell = xu & (c < d).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, stop_l, stop_s = 0, np.nan, np.nan
    for i in range(m):
        cur = pos
        if buy[i]:
            stop_l, cur = lv[i], 1
        if sell[i]:
            stop_s, cur = hv[i], -1
        if (xu[i] or cv[i] < stop_l) and pos == 1 and cur == 1:
            cur = 0                              # the close acts only on a long held, not reversed
        if (xo[i] or cv[i] > stop_s) and pos == -1 and cur == -1:
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
