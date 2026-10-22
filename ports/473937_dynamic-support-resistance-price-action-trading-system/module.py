"""Candle patterns at the 16-bar range edges, hourly bars, entries only from flat: a hammer, doji or pin bar closing within 1.8 % over the 16-bar low buys; a shooting star, doji or pin bar closing within 1.8 % under the 16-bar high sells (the sell wins a bar with both). Each trade has a 16 % stop and 9.5 % target from its fill price.
Port of FMZ strategy #473937 "Dynamic-Support-Resistance-Price-Action-Trading-System-动态支阻价格行为交易系统" (Price Action Strategy).

FMZ source id: 473937

Source
    https://www.fmz.com/strategy/473937 (PineScript v5, FMZ last modified 2024-12-04 15:19:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-183), range length 16; sensitivity 0.018; stop 16 %, target 9.5 % of avg
    (hammer or doji or pin) and close <= lowest(low, 16) x 1.018 and no open trade -> entry Buy;  (star or doji or pin) and close >= highest(high, 16) x 0.982 and no open trade -> entry Sell;  open trade: exit(stop / limit from avg x (1 -/+ 16 % / 9.5 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The patterns are as written (the pin-bar test uses the signed body, so a black candle is never a
      pin bar). Both entries can be sent from flat on one bar; the later one (the short) wins
      (#437773). The bracket is from strategy.position_avg_price, the fill price: fixed fractions,
      active from the fill (as #440797). Entries only from flat: a loop follows the bracket on the
      bar's high / low so the flat gate lines up (as 449508). Opposite entries cannot occur. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the average-price bracket as fixed fractions.
    2 generic: PASS, range-edge candle patterns with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473937_range_edge_candle_patterns_avg_bracket_from_flat"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [16, 32],
    "sensitivity": [0.018, 0.005],
}
DEFAULT_PARAMS = {"length": 16, "sensitivity": 0.018, "sl_pct": 0.16, "tp_pct": 0.095}


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
    rng = h - lo
    b = c - o
    hammer = (b > 0) & ((o - lo) > b * 2) & ((h - c) < b * 0.5) & (rng > 0)
    star = ((o - c) > 0) & ((h - o) > (o - c) * 2) & ((c - lo) < (o - c) * 0.5) & (rng > 0)
    doji = b.abs() < rng * 0.1
    pin = (((h - c) > b * 2) & ((o - lo) < b * 0.5)) | (((o - lo) > b * 2) & ((h - c) < b * 0.5))
    n, sens = int(p["length"]), float(p["sensitivity"])
    lc = ((hammer | doji | pin) & (c <= lo.rolling(n).min() * (1 + sens))).to_numpy()
    sc = ((star | doji | pin) & (c >= h.rolling(n).max() * (1 - sens))).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    slp, tpp = float(p["sl_pct"]), float(p["tp_pct"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, sl, tp = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend != 0:
            pos, pend = pend, 0
            sl = ov[i] * (1 - slp) if pos == 1 else ov[i] * (1 + slp)
            tp = ov[i] * (1 + tpp) if pos == 1 else ov[i] * (1 - tpp)
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        if pos != 0:
            continue
        if sc[i]:                                # the later short entry wins a bar with both
            se[i], pend = True, -1
        elif lc[i]:
            le[i], pend = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
