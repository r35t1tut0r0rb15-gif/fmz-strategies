"""Closes under the lower Bollinger band (50, 3) on two bars in a row, counted by the script, buy, 1-hour bars, long only: the counted second such bar goes long; a close over the upper band closes (the
four add-on buys never fill).
Port of FMZ strategy #446554 "布林带与DCA结合的高频交易策略-High-Frequency-Trading-Strategy-Combining-Bollinger-Bands-and-DCA" (DCA Booster (1 minute)).

FMZ source id: 446554

Source
    https://www.fmz.com/strategy/446554 (PineScript v5, FMZ last modified 2024-03-29 16:20:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-199), BB 50 / 3; DCA sizes 50000 / close x 1.2 / 1.3 / 1.5 / 1.5; two-bar counter
    cond_k = close < lower and close[1] < lower[1] and (bought_k-1) and not bought_k;  each true block: counter += 1, at >= 2 -> entry Compra_k, bought_k, counter = 0
    close > upper and bought_k -> close Compra_k, bought_k off  (for k = 1 .. 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy() sets no pyramiding, so only the first buy fills: Compra2-5 never fill (their flags
      still change, and their blocks still move the shared counter, which an exit does not reset), as
      written. The port runs the five flags and the counter in the script's order; the position is the
      first buy. barstate.isconfirmed is true on historical bars. Long only. The DCA quantities are
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, lower-band closes counted by the script, upper-band exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the DCA quantities stored.
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

NAME = "fmz_446554_lower_band_counted_buy_upper_exit_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 50, "mult": 3.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    lower, upper = basis - dev, basis + dev
    with np.errstate(invalid="ignore"):
        below2 = ((c < lower) & (c.shift(1) < lower.shift(1))).to_numpy()
        above = (c > upper).to_numpy()
    m = len(below2)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    bought = [False] * 6                             # bought[1..5]; bought[0] stands for "always true"
    bought[0] = True
    cnt = 0
    held = False
    for i in range(m):
        cond = [below2[i] and bought[k - 1] and not bought[k] for k in range(1, 6)]   # all read before the blocks
        for k in range(1, 6):
            if cond[k - 1]:
                cnt += 1
                if cnt >= 2:
                    if k == 1 and not held:
                        le[i] = True                 # only the first buy fills (no pyramiding)
                    bought[k] = True
                    cnt = 0
        if above[i]:
            if bought[1] and held:
                lx[i] = True
            for k in range(1, 6):
                bought[k] = False
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
