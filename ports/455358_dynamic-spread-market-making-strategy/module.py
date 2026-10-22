"""Mean-reversion around the SMA 14 with an order counter, no bar size in the source: a close at or under SMA x 0.999 (less a 0.01 offset) goes long while the counter is under 100; a close at or over SMA x 1.001 (plus the offset) goes short while the counter is positive; reversing.
Port of FMZ strategy #455358 "Dynamic Spread Market Making Strategy" (Market Making Example).

FMZ source id: 455358

Source
    https://www.fmz.com/strategy/455358 (PineScript v5, FMZ last modified 2024-06-28 15:08:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-190), SMA 14; spread 0.1 %; inventory limit 100; price offset 0.01 (price units); quantity 1
    close <= sma x 0.999 - 0.01 and inventory < 100 -> entry Buy (qty 1), inventory + 1;  close >= sma x 1.001 + 0.01 and inventory > 0 -> entry Sell (qty 1), inventory - 1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 'inventory' counts entry calls, not positions: it rises on every buy bar (also while the
      long is held and the repeat entry is refused) and falls on every sell bar, so a short is only
      sent while more buy bars than sell bars have been seen, as written (followed in a loop). The 0.01
      offset is a price amount, read against BTC near 42000 (#440456) as 0.01 / 42000 of the close.
      The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size.
      REVERSAL INTENDED. The quantity 1 is sizing.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA band reversion with an order counter.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: the quantity 1 stored.
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

NAME = "fmz_455358_sma14_spread_band_counter_reversal"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 50],
    "spread_pct": [0.1, 0.5],
}
DEFAULT_PARAMS = {"length": 14, "spread_pct": 0.1, "limit": 100, "offset_frac": 2.38e-07}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = c.rolling(int(p["length"])).mean()
    s = float(p["spread_pct"]) / 100
    off = float(p["offset_frac"]) * c
    buy = (c <= ma * (1 - s) - off).to_numpy()
    sell = (c >= ma * (1 + s) + off).to_numpy()
    lim = int(p["limit"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    inv = 0
    for i in range(m):
        if buy[i] and inv < lim:
            le[i] = True
            inv += 1
        if sell[i] and inv > 0:
            se[i] = True
            inv -= 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
