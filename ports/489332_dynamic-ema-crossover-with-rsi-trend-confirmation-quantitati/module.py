"""EMA 50 / 200 crossings with RSI 14 over (under) 50, hourly bars: the up-cross goes long with a 50-tick stop and 100-tick target (read as 0.012 % / 0.024 %), the down-cross goes short with the same long-side levels, which close it at once; reversing.
Port of FMZ strategy #489332 "Dynamic EMA Crossover with RSI Trend Confirmation Quantitative Trading Strategy" (Estrategia EMA + RSI).

FMZ source id: 489332

Source
    https://www.fmz.com/strategy/489332 (PineScript v5, FMZ last modified 2025-04-03 15:05:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 246-301), EMA 50 / 200; RSI 14 / 50; SL 50 pips (mintick), RR 2; valid on 15 / 60 / 240 / D charts; 10 % of equity
    crossover(ema50, ema200) and rsi > 50 -> entry Compra + exit(stop = close - 50 ticks, limit = close + 100 ticks)
    crossunder and rsi < 50 -> entry Venta + exit(stop = close - 50 ticks, limit = close + 100 ticks) (the long formulas)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The hourly header chart passes the time-frame test. The tick distances are read as percents at the
      header coin's price (BTC 42000 with tick 0.1: 50 ticks = 0.012 %; C2 ADAPT, as #458242). The short
      reuses the long's levels, a buy stop under and a buy limit over the market: both are marketable at the
      fill, so the short is closed one bar late (as #458256), as written. The bracket is sent as fractions of
      the fill open. An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick bracket as fractions of the fill.
    2 generic: ADAPT, tick bracket read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_489332_ema50_200_cross_rsi50_tick_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.0119, 0.5],
    "tf_take_profit_ratio": [2.0, 3.0],
}
DEFAULT_PARAMS = {"sl_pct": 0.0119, "tf_take_profit_ratio": 2.0}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.ewm(span=50, adjust=False).mean()
    s = c.ewm(span=200, adjust=False).mean()
    r = _rsi(c, 14)
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r > 50)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r < 50)
    q = float(p["sl_pct"]) / 100
    lo_lvl, hi_lvl = c * (1 - q), c * (1 + q * float(p["tf_take_profit_ratio"]))
    lvl = {"l_sl": lo_lvl, "l_tp": hi_lvl, "s_sl": lo_lvl, "s_tp": hi_lvl}    # the short reuses the long's levels
    return le, se, lvl


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
