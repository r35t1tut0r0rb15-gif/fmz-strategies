"""Oversold RSI with a rising MACD inside two agreeing custom SuperTrends, with an ATR bracket, hourly bars: RSI 14
below 35 with the MACD (5 / 13 / 9) above its signal and rising two bars, while both SuperTrend directions (factor 2
and 7) are up, goes long; the mirror (RSI above 65) goes short; each trade has a 1 ATR stop and a 2.5 ATR target.
Port of FMZ strategy #489294 "多指标趋势动量融合策略-RSI-MACD-双重超趋势跟踪系统-Multi-Indicator-Trend-Momentum-Fusion-Strategy-RSI-MACD-Dual-Supertrend-Tracking-System" (Enhanced RSI-MACD-Supertrend Strategy).

FMZ source id: 489294

Source
    https://www.fmz.com/strategy/489294 (PineScript v6, FMZ last modified 2025-04-03 11:03:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 177-240), RSI 14, MACD 5 / 13 / 9, ATR 14, SL 1 ATR, TP 2.5 ATR, SuperTrend 9 x 2 / 7
    supertrend(f, n): trend = na(trend[1]) ? up : (trend[1] > up ? max(up, trend[1]) : min(down, trend[1]));
    direction = trend == up ? 1 : -1   (up / down = hl2 -+ f x ATR(n))
    long = rsi < 35 and macd > signal and macd rising 2 bars and both directions 1;  short mirrored (rsi > 65)
    every bar: exit(stop = close -+ 1 ATR, limit = close +- 2.5 ATR, trail_points = 1 ATR) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend is the source's own function, as written (direction 1 only where the line equals the lower band).
    * The bracket follows every bar's close (a moving level): mark trailing_stop_pending. The port fixes it at the
      signal bar: sl_stop = 1 x ATR / close, tp_stop = 2.5 x ATR / close, shifted one bar inside stops(), re-based
      on the fill.
    * trail_points without trail_offset starts no trailing stop in Pine: inert, not emitted. The break-even level
      is computed but never used.
    * Every condition bar is an entry; entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (mark).
    2 generic: PASS, oscillators, ATR bands and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489294_rsi_macd_dual_supertrend_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_low": [35, 45],
    "tp_atr": [2.5, 1.5],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_low": 35, "rsi_high": 65, "macd_fast": 5, "macd_slow": 13, "macd_signal": 9,
                  "atr_len": 14, "sl_atr": 1.0, "tp_atr": 2.5, "st_factor1": 2.0, "st_factor2": 7.0, "st_len": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _st_direction(bars_df, factor, n):
    src = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    up, dn = src - factor * atr, src + factor * atr
    m = len(src)
    d = np.full(m, -1, dtype=np.int8)
    prev = np.nan
    for i in range(m):
        if np.isnan(prev):
            t = up[i]
        elif prev > up[i]:
            t = max(up[i], prev)
        else:
            t = min(dn[i], prev)
        d[i] = 1 if t == up[i] else -1
        prev = t
    return d


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = (c.ewm(span=int(p["macd_fast"]), adjust=False).mean()
            - c.ewm(span=int(p["macd_slow"]), adjust=False).mean())
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    rising = (macd > macd.shift(1)) & (macd.shift(1) > macd.shift(2))
    falling = (macd < macd.shift(1)) & (macd.shift(1) < macd.shift(2))
    d1 = _st_direction(bars_df, float(p["st_factor1"]), int(p["st_len"]))
    d2 = _st_direction(bars_df, float(p["st_factor2"]), int(p["st_len"]))
    long_e = ((rsi < p["rsi_low"]) & (macd > sig) & rising & (d1 == 1) & (d2 == 1)).astype(bool)
    short_e = ((rsi > p["rsi_high"]) & (macd < sig) & falling & (d1 == -1) & (d2 == -1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
