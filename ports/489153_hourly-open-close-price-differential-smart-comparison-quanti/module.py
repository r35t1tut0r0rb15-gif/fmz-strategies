"""Gap-up buys from flat with a 3 % close-checked target, long only, hourly bars: a bar opening above the previous
close goes long when no position is open; a close at least 3 % above the entry price closes it (no other exit).
Port of FMZ strategy #489153 "小时周期价格开口策略追踪开盘与收盘价差的智能对比量化交易系统-Hourly-Open-Close-Price-Differential-Smart-Comparison-Quantitative-Trading-System" (1 Hour Open vs Close Buy Strategy).

FMZ source id: 489153

Source
    https://www.fmz.com/strategy/489153 (PineScript v6, FMZ last modified 2025-04-02 11:15:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 202-232), target 3 %
    buy = open > close[1] and position == 0 -> entry long
    position > 0 and close >= avg price x 1.03 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is checked on closes: a close-based exit signal (rule 3). The average price is the fill (the open of
      the bar after the signal); there is no stop, as written.
    * Entries only from flat: Opposite entries cannot occur. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a close-checked target.
    2 generic: PASS, a gap test and a percentage.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489153_gap_up_buy_3pct_target_long"
FAMILY = "price_action_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "target_pct": [3.0, 1.0],
}
DEFAULT_PARAMS = {"target_pct": 3.0}


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
    o, c = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    k = 1 + p["target_pct"] / 100
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, pending, exiting, avg = False, False, False, np.nan
    for i in range(1, m):
        if pending:
            held, pending, avg = True, False, o[i]
        if exiting:
            held, exiting = False, False
        if not held and not pending and o[i] > c[i - 1] and i + 1 < m:
            le[i], pending = True, True
        if held and not exiting and c[i] >= avg * k:
            lx[i], exiting = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
