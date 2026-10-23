"""Doji or morning-doji-star candles above the EMA 60, 45-minute bars, long only: either pattern goes long; a stop at the 100-bar lowest low, a 9 % target and a trailing stop that starts after 1 % and trails 0.5 % close it.
Port of FMZ strategy #426804 "晨星K线突破策略Morning-Star-Breakout-Strategy" (PURE MORNING 2.0).

FMZ source id: 426804

Source
    https://www.fmz.com/strategy/426804 (PineScript v5, FMZ last modified 2023-09-14 16:36:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 134-247), MDS tolerance 0.09 %, doji tolerance 0.05 %; EMA 60; TP 9 %; SL lowest low 100 (type lowest low); trail 1 % / 0.5 % of the close in ticks; max-loss filter off
    el_cond = doji (|open - close| within 0.05 % of the close) and close > ema(60);  el_cond_02 = morning doji star and close > ema(60) -> entry EL
    exit("XL+SL/TP", "EL", stop = lowest(low, 100), limit = avg x 1.09, trail_points = 1 % of close, trail_offset = 0.5 % of close);  crossover(mfi, 90) -> close "XL" (no such entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop level is the 100-bar lowest low re-sent every bar; the port fixes it at the signal bar as a
      fraction of the fill (it may move up afterwards there: mark trailing_stop_pending). The trail is the
      house percent trail {"pct": 0.005, "anchor": "high_low", "activate_after": 0.01} (the source's tick
      distances are 1 % / 0.5 % of the latest close; stated approximation, mark trailing_stop). "and"
      binds before "or" in the doji-star middle candle, as written. The MFI close names the id "XL",
      which is never entered, so it never acts and volume does not reach the orders: ported as not using
      volume (check 8). Long only (one entry id, pyramiding 1). Stop module: portfolio_kwargs {} (driver
      D4). The 10 % of equity size, slippage and commission are sizing / costs. FREQ = "45min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; lowest-low stop, percent target and a house trail.
    2 generic: PASS, doji / morning-star candles in an EMA 60 up-trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, capital 10000, commission 0.075 %, slippage 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426804_doji_morning_star_ema60_lowest_low_stop_trail_long"
FAMILY = "candle_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_len": [100, 50],
    "tp": [0.09, 0.05],
}
DEFAULT_PARAMS = {"sl_len": 100, "tp": 0.09, "mds_tol": 0.09, "doji_tol": 0.05, "trail_on": 0.01, "trail_off": 0.005}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = h - lo
    tol, tol1 = float(p["mds_tol"]) / 100, float(p["doji_tol"]) / 100
    with np.errstate(divide="ignore", invalid="ignore"):
        c1 = ((c.shift(2) - o.shift(2)).abs() / rng.shift(2) > 0.6) & (c.shift(2) < o.shift(2))
    o1, cl1 = o.shift(1), c.shift(1)
    c2 = ((o1 > cl1) & (o1 < cl1 * (1 + tol))) | ((o1 < cl1) & (o1 > cl1 * (1 - tol)) & (cl1 < c.shift(2) + rng.shift(2)))
    c3 = (c > o) & (c > c.shift(2) + rng.shift(2))
    mds = c1 & c2 & c3
    doji = ((o > c) & (o < c * (1 + tol1))) | ((o < c) & (o > c * (1 - tol1)))
    up = c > c.ewm(span=60, adjust=False).mean()
    le = (doji & up) | (mds & up)
    false = pd.Series(False, index=c.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, lo = bars_df["open"], bars_df["low"]
    ll = lo.rolling(int(p["sl_len"])).min().shift(1)    # the stop sent at the signal bar's close
    sl_f = 1 - ll / o
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": float(p["tp"]),
            "trail": {"type": "percent", "pct": float(p["trail_off"]), "anchor": "high_low",
                      "activate_after": float(p["trail_on"])}}


def portfolio_kwargs(**params):
    return {}
