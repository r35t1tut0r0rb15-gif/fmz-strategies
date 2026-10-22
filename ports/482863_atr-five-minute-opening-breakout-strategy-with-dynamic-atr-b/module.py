"""Breaks of the 09:30 UTC opening 5-minute candle, 5-minute bars: the close crossing over its high goes long with the stop 1 ATR 14 under its low and a target 1.5 ranges over its high, the close crossing under its low goes short with the mirror; reversing.
Port of FMZ strategy #482863 "五分钟开盘突破ATR动态止盈止损量化交易策略-Five-Minute-Opening-Breakout-Strategy-with-Dynamic-ATR-Based-Stop-Loss-and-Take-Profit" (5-Min Open Candle Breakout).

FMZ source id: 482863

Source
    https://www.fmz.com/strategy/482863 (PineScript v5, FMZ last modified 2025-02-27 17:33:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-149), opening candle at 09:30 (timestamp() in the exchange's time); ATR 14; stop factor 1.0; target factor 1.5
    time in [09:30, 09:35) -> openPrice / highPrice / lowPrice := that bar's open / high / low
    crossover(close, highPrice) -> entry Long;  every bar: exit Long (stop = lowPrice - atr, limit = highPrice + 1.5 (highPrice - lowPrice))
    crossunder(close, lowPrice) -> entry Short;  every bar: exit Short (stop = highPrice + atr, limit = lowPrice - 1.5 range)

Interpretation choices (Pine rules in SURVEY_README.md)
    * timestamp(year, month, day, 9, 30) reads the chart exchange's time zone; for the header's Binance
      pair that is UTC, so the capture bar is the 5-minute bar opening at 09:30 UTC (fixed UTC, no DST,
      as 478700); the comment's NYSE is not applied. The levels keep the last capture (var).
    * The exit is re-sent every bar with the current ATR (and new levels after the next capture); the port
      fixes the bracket at the signal bar's levels and sends it as fractions of the fill open (a level at
      or through it is marketable and closed one bar late, as #458256), mark trailing_stop_pending. An
      entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4).
      No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; opening-candle bracket as fractions of the fill.
    2 generic: PASS, opening-candle breakouts with an ATR stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: capture bar 09:30 UTC (fixed UTC, no DST; the header exchange's time zone).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482863_open_0930utc_5min_candle_break_atr_range_bracket_reversal"
FAMILY = "opening_range"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
SESSION_TZ = "UTC"  # timestamp() reads the chart exchange's zone: UTC for the header's Binance pair

GRID = {
    "sl_factor": [1.0, 2.0],
    "tp_factor": [1.5, 1.0],
}
DEFAULT_PARAMS = {"sl_factor": 1.0, "tp_factor": 1.5, "atr_length": 14, "capture_minute": 570}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    loc = bars_df.index.tz_convert(SESSION_TZ)
    mod = np.asarray(loc.hour * 60 + loc.minute)
    cap = (mod >= int(p["capture_minute"])) & (mod < int(p["capture_minute"]) + 5)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    hp, lp = np.full(m, np.nan), np.full(m, np.nan)
    a = b = np.nan
    for i in range(m):
        if cap[i]:
            a, b = hv[i], lv[i]
        hp[i], lp[i] = a, b
    hp, lp = pd.Series(hp, index=c.index), pd.Series(lp, index=c.index)
    le = (c > hp) & (c.shift(1) <= hp.shift(1))
    se = (c < lp) & (c.shift(1) >= lp.shift(1))
    atr = _atr(bars_df, int(p["atr_length"]))
    rng = hp - lp
    k, t = float(p["sl_factor"]), float(p["tp_factor"])
    lvl = {"l_sl": lp - atr * k, "l_tp": hp + rng * t, "s_sl": hp + atr * k, "s_tp": lp - rng * t}
    return le & ~se, se, lvl


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
