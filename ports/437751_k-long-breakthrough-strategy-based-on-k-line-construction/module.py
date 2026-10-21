"""Outside-reversal bar buys with a 4 % bracket, 1-hour bars, long only: from flat, an up candle that dipped under its open and the previous low and closed above the previous open and close buys; the trade has
a 4 % target and a 4 % stop.
Port of FMZ strategy #437751 "基于K线构建的多头突破策略Long-Breakthrough-Strategy-Based-on-K-Line-Construction" (SimpleBarPattern_LongOnly).

FMZ source id: 437751

Source
    https://www.fmz.com/strategy/437751 (PineScript v5, FMZ last modified 2024-01-05 12:37:46).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 177-199), take profit 4 %, stop loss 4 % (as ticks of the close); date range true
    IsLong = low < open and low < low[1] and close > open and close > open[1] and close > close[1];  entry Open_Long when IsLong and opentrades == 0, exit(profit = 4 % close / mintick, loss = 4 % close / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is written in ticks of 4 % of the signal close; the port reads it as fixed 4 % fractions
      of the entry fill (as #437684). "Flat" follows the house bracket. inDateRange is true: dropped. Long
      only. Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size and commission are
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, candle pattern and percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_437751_outside_reversal_bar_pct_bracket_long"
FAMILY = "candle_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.04, 0.02],
    "sl": [0.04, 0.02],
}
DEFAULT_PARAMS = {"tp": 0.04, "sl": 0.04}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sig = ((lo < o) & (lo < lo.shift(1)) & (c > o) & (c > o.shift(1)) & (c > c.shift(1))).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - sl) or hv[i] >= e * (1 + tp):
                pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            le[i] = True
            pos, entry_i = 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
