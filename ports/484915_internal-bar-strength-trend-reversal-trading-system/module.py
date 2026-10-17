"""Internal bar strength reversals with an EMA 220 filter and a 14-bar time exit, 1-hour bars: when the previous bar
closed in the bottom 9 % of its range and the close is above EMA 220 the strategy goes long; when it closed in the top
1.5 % below EMA 220 it goes short; a long closes on a top-1.5 % previous bar, a short on a bottom-9 % one, and any
trade 14 bars after its last entry.
Port of FMZ strategy #484915 "内部价格强度趋势反转交易系统-Internal-Bar-Strength-Trend-Reversal-Trading-System" (IBS (Internal Bar Strength) Trading Strategy for SPY and NDQ).

FMZ source id: 484915

Source
    https://www.fmz.com/strategy/484915 (PineScript v6, FMZ last modified 2025-03-05 09:55:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 188-259), IBS entry 0.09 / exit 0.985, EMA 220, min distance 0 %, max
duration 14 (bars), pyramiding 2
    ibs = (high[1] != low[1]) ? (close[1] - low[1]) / (high[1] - low[1]) : 0.5
    enterLong = ibs < 0.09 and close > ema;  enterShort = ibs > 0.985 and close < ema
    exitLong = ibs > 0.985;  exitShort = ibs < 0.09
    lastEntryPrice = na when flat; an entry needs na(lastEntryPrice) or the close beyond it (long: below) by >= 0 %
    entries set lastEntryPrice and entryBarIndex; exit or bar_index - entryBarIndex >= 14 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * Adds (pyramiding 2) are sizing: net position only (#490570); a same-side entry while held still moves
      lastEntryPrice and the duration clock, as written. "Days" in the duration input are bars of the header chart.
    * The closes test the position held at the bar's start and never undo an entry on that bar (#430850); a short
      while long (when allowed by the distance rule) reverses. REVERSAL INTENDED.
    * The author's daily-bar notes do not override the 1-hour backtest header: FREQ = "1h". No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar-range ratios, an EMA and bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 50 % of equity and pyramiding quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484915_ibs_reversal_time_exit"
FAMILY = "ibs_mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ibs_entry": [0.09, 0.2],
    "max_bars": [14, 28],
}
DEFAULT_PARAMS = {"ibs_entry": 0.09, "ibs_exit": 0.985, "ema_period": 220, "min_entry_pct": 0.0, "max_bars": 14}


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
    h1, l1, c1 = (bars_df[k].shift(1) for k in ("high", "low", "close"))
    ibs = ((c1 - l1) / (h1 - l1)).where(h1 != l1, 0.5).to_numpy()
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    above, below = (c > ema).to_numpy(), (c < ema).to_numpy()
    cv = c.to_numpy(dtype=float)
    lo_t, hi_t, gap = p["ibs_entry"], p["ibs_exit"], p["min_entry_pct"] / 100
    hold = int(p["max_bars"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, last, ebar = 0, np.nan, None
    for i in range(m):
        start = pos
        if start == 0:
            last = np.nan
        dca_l = np.isnan(last) or (cv[i] < last and (last - cv[i]) / last >= gap)
        dca_s = np.isnan(last) or (cv[i] > last and (cv[i] - last) / last >= gap)
        if ibs[i] < lo_t and above[i] and dca_l:
            pos, last, ebar = 1, cv[i], i
        if ibs[i] > hi_t and below[i] and dca_s:
            pos, last, ebar = -1, cv[i], i
        dur = i - ebar if ebar is not None else 0
        if (ibs[i] > hi_t or dur >= hold) and start == 1 and pos == 1:
            pos = 0
        if (ibs[i] < lo_t or dur >= hold) and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
