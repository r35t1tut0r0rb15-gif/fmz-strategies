"""Three bars in a row closing beyond a Bollinger band (20, 2) in their own direction and in the outer half of their range, 12-hour bars: three up bars over the upper band go long from flat, three down bars under the lower band go short from flat, each with its stop at the first bar's low / high and a 1:1 target from the signal close.
Port of FMZ strategy #482595 "Triple Candlestick Bollinger Bands Breakout Trend Following Strategy with High Low Point Confirmation" (Bollinger Band Strategy (Close Near High/Low Relative to Half Range)).

FMZ source id: 482595

Source
    https://www.fmz.com/strategy/482595 (PineScript v6, FMZ last modified 2025-02-19 11:05:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-182), BB 20 x 2.0; stop low[2] / high[2]; target 1 x risk; 200 % of equity; pyramiding 0
    close, close[1], close[2] > upper band and each bar closes up and above (high + low) / 2, and flat -> entry Buy + exit(stop = low[2], limit = close + (close - low[2]));  mirror and flat -> entry Sell + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries come only from flat; the levels are fixed at the signal close, so the loop follows the
      bracket on each bar's high / low to know when the position is flat again (as #449508; a level the
      fill opens through closes the trade at that open in the loop and one bar late in the engine, as
      #458256). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. Opposite entries cannot occur (entries only from flat). The 200 % of equity size is
      sizing. FREQ = "12h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; candle-sequence bracket as fractions of the fill.
    2 generic: PASS, three-bar band walks with a 1:1 bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482595_bb20_three_bar_band_walk_1r_bracket_flat_only"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
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


def _signals(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = mid + float(p["mult"]) * sd, mid - float(p["mult"]) * sd
    hl2 = (h + lo) / 2
    bull = (c > up) & (c > o) & (c > hl2)
    bear = (c < dn) & (c < o) & (c < hl2)
    lc = bull & bull.shift(1, fill_value=False) & bull.shift(2, fill_value=False)
    sc = bear & bear.shift(1, fill_value=False) & bear.shift(2, fill_value=False)
    rr = float(p["rr"])
    l_sl, s_sl = lo.shift(2), h.shift(2)
    lvl = {"l_sl": l_sl, "l_tp": c + (c - l_sl) * rr, "s_sl": s_sl, "s_tp": c - (s_sl - c) * rr}
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    a = {k: v.to_numpy(dtype=float) for k, v in lvl.items()}
    lcv, scv = lc.to_numpy(), sc.to_numpy()
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, sl, tp = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos, sl, tp = 1, a["l_sl"][i - 1], a["l_tp"][i - 1]
        elif pend == -1:
            pos, sl, tp = -1, a["s_sl"][i - 1], a["s_tp"][i - 1]
        pend = 0
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar (or at its open)
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        if pos == 0 and lcv[i]:
            le[i], pend = True, 1
        elif pos == 0 and scv[i]:
            se[i], pend = True, -1
    idx = c.index
    return pd.Series(le, index=idx), pd.Series(se, index=idx), lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
