"""SMA 3 / SMA 8 state, long only, no bar size of its own: from flat, SMA 3 above SMA 8 goes long; the long
is closed when SMA 3 is below SMA 8.
Port of FMZ strategy #428756 "blackcat L1 MartinGale Scalping Strategy" ([blackcat] L1 MartinGale Scalping Strategy).

FMZ source id: 428756

Source
    https://www.fmz.com/strategy/428756 (PineScript v5, FMZ last modified 2023-11-03 17:27:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 59-128), SMA 3 / 8, take profit 1.03, stop 0.95, trading mode Long
    flat: sma3 > sma8 -> entry Buy; sma3 < sma8 -> entry Sell (forbidden: allow_entry_in long)
    long: (close > takeProfitPrice or close < stopLossPrice) and sma3 < sma8 -> close; else entry Buy again (add)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The level variables are declared without `var`, so they are 0.0 again on every bar when the
      exits are tested: `close > takeProfitPrice` is always true, and the long closes exactly when
      SMA 3 < SMA 8 (as written; the 1.03 / 0.95 multipliers are inert). Same for the short side.
    * Trading mode defaults to Long: strategy.risk.allow_entry_in(long) forbids short entries, so
      from flat only longs open. Long only.
    * The "else" re-entries while long are adds (pyramiding 5): sizing, stored.
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1).
      precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]);
      the driver supplies bar_size (never in GRID / DEFAULT_PARAMS).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average comparisons only.
    3 crypto-exchange-only: no.
    4 signals only: pyramiding, the adds and the inert take-profit / stop levels stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428756 (2 members, best partner #433071, Jaccard 0.828); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_428756_sma3_8_state_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5],
    "slow": [8, 13],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 8}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    above, below = (f > s).to_numpy(), (f < s).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if not held and above[i]:
            le[i], held = True, True
        elif held and below[i]:
            lx[i], held = True, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
