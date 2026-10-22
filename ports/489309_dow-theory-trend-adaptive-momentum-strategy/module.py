"""Dow-theory trend from the last two confirmed 10 / 10 pivot highs and lows, 2-minute bars: a turn to higher highs and higher lows goes long, a turn to lower highs and lower lows goes short, each with a 100-tick stop and 200-tick target from the fill (read as 0.167 % / 0.333 %); reversing.
Port of FMZ strategy #489309 "Dow Theory Trend Adaptive Momentum Strategy" (Dow Theory Trend Strategy v3).

FMZ source id: 489309

Source
    https://www.fmz.com/strategy/489309 (PineScript v5, FMZ last modified 2025-04-03 13:05:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-220), pivots 10 / 10; mode Auto; SL 100 ticks, TP 200 ticks (on)
    new pivot high (value changed) -> previous := last, last := it;  same for lows
    HH and HL -> trend 1;  LH and LL -> trend -1;  else keep
    trend changes to 1 -> entry L + exit(loss = 100, profit = 200);  changes to -1 -> entry S + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is known at its confirmation bar, 10 bars after the extreme (strict on both sides); the
      pivot lists and trend are followed in a loop. loss / profit are tick distances from the entry price:
      read as percents at the header coin's price (BNB about 600 with tick 0.01: 100 ticks = 0.167 %, 200
      ticks = 0.333 %; C2 ADAPT, as #458242), fixed fractions of the fill, active from the fill bar (as
      #440797). The trend alternates, so a same-side signal cannot come while held. An entry on the other
      side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). No sizing code.
      FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick bracket from the fill.
    2 generic: ADAPT, tick bracket read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_489309_dow_pivot10_hh_hl_trend_change_tick_bracket_reversal"
FAMILY = "market_structure"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pivotLookback": [10, 5],
    "sl_pct": [0.1667, 0.5],
}
DEFAULT_PARAMS = {"pivotLookback": 10, "sl_pct": 0.1667}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["pivotLookback"])
    ph, pl = _pivot(h, 1, k), _pivot(lo, -1, k)
    hk, lk = h.shift(k).to_numpy(), lo.shift(k).to_numpy()
    m = len(c)
    tr_ = np.zeros(m)
    lh = ph_prev = ll = pl_prev = np.nan
    t = 0
    for i in range(m):
        if ph[i] and (np.isnan(lh) or hk[i] != lh):
            ph_prev, lh = lh, hk[i]
        if pl[i] and (np.isnan(ll) or lk[i] != ll):
            pl_prev, ll = ll, lk[i]
        if not (np.isnan(lh) or np.isnan(ph_prev) or np.isnan(ll) or np.isnan(pl_prev)):
            if lh > ph_prev and ll > pl_prev:
                t = 1
            elif lh < ph_prev and ll < pl_prev:
                t = -1
        tr_[i] = t
    trend = pd.Series(tr_, index=c.index)
    chg = trend != trend.shift(1)
    chg.iloc[0] = False
    le = chg & (trend == 1)
    se = chg & (trend == -1)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    q = float(p["sl_pct"]) / 100
    sl = pd.Series(q, index=idx).shift(1)
    tp = pd.Series(2 * q, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
