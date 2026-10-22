"""SMA 10 / 30 crossings, bar size from the search: a cross up goes long with a 1 % stop and a 3 % target from the fill, a cross down goes short; the short's levels reuse the long's and sit on the wrong
side of the market, so each short closes at the next open after its fill; reversing.
Port of FMZ strategy #446560 "Moving Average Crossover Strategy" (barreto (SMA 10 / 30 crossover with stop and target)).

FMZ source id: 446560

Source
    https://www.fmz.com/strategy/446560 (PineScript v4, FMZ last modified 2024-03-29 16:38:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-148), SMA 10 / 30; stop avg x 0.99, target avg x 1.03 for both ids
    crossover -> entry Long;  crossunder -> entry Short;  crossunder -> close Long;  crossover -> close Short
    exit(Long, stop = avg x 0.99, limit = avg x 1.03);  exit(Short, stop = avg x 0.99, limit = avg x 1.03)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. The
      levels come from the average price (na while flat), so the long's bracket is a fixed 1 % / 3 % of
      the fill (as #440797). For a short the same levels are a buy stop under and a buy limit over the
      price, on the wrong side of the market: the short closes at the first open after its fill bar
      (the port closes it on that bar's signal, as #439872). Each close comes after the opposite entry
      and leaves the reversal. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close.
    2 generic: PASS, SMA crossings with a long bracket.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_446560_sma10_30_cross_long_bracket_short_next_open_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 5],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "sl": 0.01, "tp": 0.03}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def _run(bars_df, p):
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    m = len(xo)
    le, se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, sfill = 0, -1
    for i in range(m):
        new = pos
        if xo[i] and pos != 1:
            le[i], new = True, 1
        if xu[i] and pos != -1:
            se[i], new = True, -1
            sfill = i + 1
        if pos == -1 and new == -1 and i >= sfill:
            sx[i], new = True, 0                     # wrong-side levels: out at the next open
        pos = new
    return le, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    ix = bars_df.index
    on = pd.Series(le, index=ix)
    return {"sl_stop": pd.Series(float(p["sl"]), index=ix).where(on).shift(1),
            "tp_stop": pd.Series(float(p["tp"]), index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
