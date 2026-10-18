"""Span B breakouts with a percent bracket and a direction alternation filter, 1-hour bars: from flat the script sends BOTH a long and a short order (the short, sent last, stands) unless the
filter forbids the side of the last closed trade; a close crossing over the 52-bar channel midline reverses to long; each trade has a 1 % stop and a 2 % target.
Port of FMZ strategy #436114 "Floor Crossing Sawtooth Profit Stop Strategy Based on Moving Average" (Stairs Gain Strategy - MG).

FMZ source id: 436114

Source
    https://www.fmz.com/strategy/436114 (PineScript v5, FMZ last modified 2023-12-21 12:26:18).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 219-271), span B 52; filter on; stop 1 %, target 2 %; ATR 14 x 0.3 against 0.01 / 0.06
    buycross = crossover(close, leadLine2) ? atr 0.3 > 0.01 : flat;  sellcross = crossover(leadLine2, close) ? atr 0.3 < 0.06 : flat;  filter: no long right after a closed long, no short right after a closed short
    entry long (buycross and long filter), exit(limit = avg 1.02, stop = avg 0.99);  entry short (sellcross and short filter), exit(limit = avg 0.98, stop = avg 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ternaries make each cross flag true on EVERY flat bar (the else branch is "flat"), so a flat
      strategy sends the long and then the short entry, and the short stands unless the filter blocks it
      (the side of the last closed trade is refused, so trades alternate in direction). Criterion 2:
      the ATR limits 0.01 / 0.06 are price units; the port reads them as fractions of the close (0.01 and 0.06
      divided by a BTC price of 40000, i.e. inert on any real ATR: the upcross always passes, the downcross
      never does). The bracket is followed as the house stop (from the fill open) so that "flat" and the last
      closed side are known; it is a fraction of the fill price: sl_stop 0.01, tp_stop 0.02. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-hour bars: not coarse. REVERSAL INTENDED. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: REVIEW, ternary flags true on every flat bar; price-unit ATR limits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_436114_span_b_alternating_bracket"
FAMILY = "breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "span": [52, 26],
    "filter": [True, False],
}
DEFAULT_PARAMS = {"span": 52, "filter": True, "displacement": 1, "sl": 0.01, "tp": 0.02, "atr_mult": 0.3,
                  "atr_hi_frac": 2.5e-7, "atr_lo_frac": 1.5e-6}


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
    n = int(p["span"])
    lead = ((lo.rolling(n).min() + h.rolling(n).max()) / 2).shift(int(p["displacement"]) - 1)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr_frac = (tr.ewm(alpha=1 / 14, adjust=False).mean() * float(p["atr_mult"]) / c).to_numpy()
    cross_up = ((c > lead) & (c.shift(1) <= lead.shift(1))).fillna(False).to_numpy()
    cross_dn = ((lead > c) & (lead.shift(1) <= c.shift(1))).fillna(False).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    filt = bool(p["filter"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ei, e0 = 0, -1, np.nan
    last_dir = 0
    prev_end = 0
    pend = None
    for i in range(m):
        if pend is not None:                      # fills at this bar's open: long entry, then short entry
            eL, eS = pend
            if eL and pos <= 0:
                pos, ei, e0 = 1, i, ov[i]
            if eS and pos >= 0:
                pos, ei, e0 = -1, i, ov[i]
        pend = None
        if pos != 0 and i >= ei:                  # the house bracket from the fill price
            if pos == 1 and (lv[i] <= e0 * (1 - sl) or hv[i] >= e0 * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + sl) or lv[i] <= e0 * (1 - tp)):
                pos = 0
        if prev_end > 0 and pos == 0:
            last_dir = 1
        if prev_end < 0 and pos == 0:
            last_dir = -1
        prev_end = pos
        flat = pos == 0
        buycross = (atr_frac[i] > float(p["atr_hi_frac"])) if cross_up[i] else flat
        sellcross = (atr_frac[i] < float(p["atr_lo_frac"])) if cross_dn[i] else flat
        long_ok = (not (filt and last_dir == 1))
        short_ok = (not (filt and last_dir == -1))
        eL, eS = bool(buycross and long_ok), bool(sellcross and short_ok)
        if eL and eS:
            eL = False                            # long then short on one open: the short stands
        le[i], se[i] = eL, eS
        pend = (bool(buycross and long_ok), bool(sellcross and short_ok))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
