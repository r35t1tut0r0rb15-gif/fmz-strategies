"""Hourly bars against the running London-session (02:00-08:20 UTC) high and low kept since the data start: in New York hours (08:20-16:00) a red candle reaching the London high goes short with a stop just over its high and a target just under its low; between 10:30 and 13:00 a close under the London low goes long with a target just over the close and a stop just under its low.
Port of FMZ strategy #488283 "多时段价格行为机构交易策略基于ICT理念的日内做空系统-Multi-Session-Price-Action-Institutional-Trading-Strategy-ICT-Based-Intraday-Short-System" (ICT Bread and Butter Sell-Setup).

FMZ source id: 488283

Source
    https://www.fmz.com/strategy/488283 (PineScript v5, FMZ last modified 2025-03-26 15:40:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-243), sessions London 02:00 / NY 08:20-16:00 / Asia 19:00; ticks 10 / 20 / 15
    var londonHigh / londonLow = first bar's high / low, widened by every London-session bar (never reset)
    high >= londonHigh and NY hours and close < open -> entry Short + exit(limit = low - 20 ticks, stop = high + 10 ticks)
    10:30 <= time <= 13:00 and close < londonLow -> entry Buy + exit(limit = close + 20 ticks, stop = low - 10 ticks)
    19:00 <= time < 02:00 (same day) and close > asiaHigh -> entry Asia Short (never true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * timestamp() on the Binance header reads UTC; each bar is tested at its opening time. The session
      ranges are var values that are never reset, so the London high / low are the extremes of every
      London bar since the first bar of the data (that first bar included), as written. The Asia window
      runs from 19:00 to 02:00 of the same date, which no time meets, so the Asia short never trades. The
      tick distances are read as percents at the header coin's price (ETH about 3000 with tick 0.01: 10
      ticks = 0.0033 %; C2 ADAPT, as #458242), scaled by the signal close. The brackets are set on the
      signal bar and sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late, as #458256). A later same-side signal while held re-sends the bracket; the port keeps
      the opening levels, mark trailing_stop_pending (as #434428). When both entries fire on one bar the
      Buy, placed later, reverses the short (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver
      D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick brackets as fractions of the fill.
    2 generic: ADAPT, tick brackets read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: London 02:00-08:20, New York 08:20-16:00, buy window 10:30-13:00 UTC (bar opening times).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488283_london_range_judas_short_london_low_buy_tick_bracket"
FAMILY = "session_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_ticks": [10, 30],
    "tp_ticks": [20, 60],
}
DEFAULT_PARAMS = {"sl_ticks": 10, "tp_ticks": 20, "tick_frac": 3.3333e-06}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    idx = c.index.tz_convert("UTC")
    mins = np.asarray(idx.hour * 60 + idx.minute)
    london = (mins >= 120) & (mins < 500)
    ny = (mins >= 500) & (mins < 960)
    buy_win = (mins >= 630) & (mins <= 780)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    lh = np.where(london, hv, -np.inf)
    ll = np.where(london, lv, np.inf)
    if len(hv):
        lh[0], ll[0] = max(lh[0], hv[0]), min(ll[0], lv[0])     # var: the first bar's values
    lon_hi = pd.Series(np.maximum.accumulate(lh), index=c.index)
    lon_lo = pd.Series(np.minimum.accumulate(ll), index=c.index)
    se = (h >= lon_hi) & ny & (c < o)
    le = buy_win & (c < lon_lo)
    t = c * float(p["tick_frac"])
    a, b = t * float(p["sl_ticks"]), t * float(p["tp_ticks"])
    lvl = {"l_sl": lo - a, "l_tp": c + b, "s_sl": h + a, "s_tp": lo - b}
    return le, se & ~le, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
