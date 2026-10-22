"""RSI 14, MACD 12 / 26 / 9 and a stochastic all crossing up through their signals on one bar above the SMA 50, hourly bars, long only, with a 1.5 % stop and 3 % target from the fill and a trail of 5 ticks after 10 ticks of profit (read as percents).
Port of FMZ strategy #490042 "Multi Indicator Divergence Trading System with Advanced Risk Management" (Multi-Divergence Strategy - Verbeterd).

FMZ source id: 490042

Source
    https://www.fmz.com/strategy/490042 (PineScript v5, FMZ last modified 2025-04-11 09:22:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 210-268), RSI 14 / SMA 14; MACD 12 / 26 / 9; stoch(high, low, close, 14) / SMA 14; SMA 50; SL 1.5 %, TP 3 %; trail 10 / 5 ticks; 10 % of equity
    crossover(rsi, sma(rsi, 14)) and crossover(macd, signal) and crossover(stoch, sma(stoch, 14)) and close > sma50 -> entry Long
    every bar: exit(stop = avg x 0.985, limit = avg x 1.03, trail_points = 10, trail_offset = 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch is called with (high, low, close, 14), so its source is the high and its range the 14-bar
      high of lows and low of closes, as written. The exit is re-sent each bar from
      strategy.position_avg_price, so the stop and target are fixed percents of the fill, active from the
      fill bar (as #440797). The trail is in ticks, read as percents at the header coin's price (ETH about
      3000 with tick 0.01: 10 ticks = 0.0033 % activation, 5 ticks = 0.0017 % offset; C2 ADAPT, as
      #458242), as the house percent trail on highs (mark trailing_stop). The sell condition is only
      plotted. Long only. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill and a percent trail.
    2 generic: ADAPT, the tick trail read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_490042_rsi_macd_stoch_triple_cross_sma50_pct_bracket_trail_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stopLossPercent": [1.5, 3.0],
    "takeProfitPercent": [3.0, 6.0],
}
DEFAULT_PARAMS = {"stopLossPercent": 1.5, "takeProfitPercent": 3.0, "trail_activate": 3.3333e-05,
                  "trail_pct": 1.6667e-05, "maLength": 50}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    hh, ll = lo.rolling(14).max(), c.rolling(14).min()           # ta.stoch(high, low, close, 14) as written
    st = 100 * (h - ll) / (hh - ll).where(hh != ll)
    le = xo(r, r.rolling(14).mean()) & xo(macd, sig) & xo(st, st.rolling(14).mean())
    le = le & (c > c.rolling(int(p["maLength"])).mean())
    false = pd.Series(False, index=c.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stopLossPercent"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["takeProfitPercent"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp,
            "trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
