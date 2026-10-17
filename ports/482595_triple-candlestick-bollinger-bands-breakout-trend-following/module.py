"""Three strong candles closing outside the Bollinger band (20, 2) from flat: long above the upper band with the stop
at the first candle's low and a 1 R target, short mirrored, twelve-hour bars.
Port of FMZ strategy #482595 "基于布林带突破的三连阳阳线高点趋势跟踪策略-Triple-Candlestick-Bollinger-Bands-Breakout-Trend-Following-Strategy-with-High-Low-Point-Confirmation" (Bollinger Band Strategy (Close Near High/Low Relative to Half Range)).

FMZ source id: 482595

Source
    https://www.fmz.com/strategy/482595 (PineScript v6, FMZ last modified 2025-02-19 11:05:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 136-173), BB 20 / 2
    buy = for each of the last three bars: close > upper band, close > open, close > (high + low) / 2
    buy and flat -> stop = low[2], target = close + (close - stop), entry long with exit(stop, limit)
    sell mirrored with high[2]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: (close - low[2]) / close for both stop and target
      (1 R), shifted one bar inside stops() and re-based on the fill (house rule). A stop not below the close
      (zero-length trade) emits no entry (as L2 #491035).
    * Flat-only entries with stops: simulate() mirrors the house bracket from the fill bar (as #430254); an entry is
      allowed on the bar a stop is hit. Opposite entries cannot occur while held.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "12h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, Bollinger bands, candle shape and the setup's extreme.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries from flat only).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482595_three_strong_closes_outside_bb_1r_flat"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [2.0, 1.5],
    "rr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rr": 1.0}


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


def _parts(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    mid = (h + lo) / 2
    up1 = (c > basis + dev) & (c > o) & (c > mid)
    dn1 = (c < basis - dev) & (c < o) & (c < mid)
    buy = up1 & up1.shift(1, fill_value=False) & up1.shift(2, fill_value=False)
    sell = dn1 & dn1.shift(1, fill_value=False) & dn1.shift(2, fill_value=False)
    sl_l, sl_s = (c - lo.shift(2)) / c, (h.shift(2) - c) / c
    return buy.to_numpy() & (sl_l > 0).to_numpy(), sell.to_numpy() & (sl_s > 0).to_numpy(), sl_l, sl_s


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    buy, sell, sl_l, sl_s = _parts(bars_df, p)
    sl_l, sl_s = sl_l.to_numpy(), sl_s.to_numpy()
    rr = p["rr"]
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + rr * s_)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - rr * s_)):
                pos = 0
        if pos == 0 and i + 1 < m:
            if buy[i]:
                le[i], pos, entry_i, s_ = True, 1, i + 1, sl_l[i]
            elif sell[i]:
                se[i], pos, entry_i, s_ = True, -1, i + 1, sl_s[i]
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, _, sl_l, sl_s = _parts(bars_df, p)
    sl = sl_l.where(buy, sl_s)                             # picked by the signal's side
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
