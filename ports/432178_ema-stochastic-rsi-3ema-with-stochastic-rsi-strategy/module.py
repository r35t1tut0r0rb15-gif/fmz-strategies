"""EMA 8 / 14 / 50 stack with stochastic-RSI crosses, long only, 1-hour bars: the EMAs stacked upwards and the stochastic
RSI K (14 / 14, smoothed 3) crossing above its D go long; a 3 ATR stop and a 2 ATR target are fixed at the fill.
Port of FMZ strategy #432178 "三EMA叉加Stochastic-RSI策略3EMA-with-Stochastic-RSI-Strategy" (3 x EMA + Stochastic RSI + ATR).

FMZ source id: 432178

Source
    https://www.fmz.com/strategy/432178 (PineScript v4, FMZ last modified 2023-11-15 10:47:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-172), EMA 8 / 14 / 50, stoch RSI 14 / 14 / 3 / 3, ATR 14 (previous bar), TP 2, SL 3
    ema8 > ema14 and ema14 > ema50 and crossover(k, d) -> entry long
    in position, first bar: stop = avg price - 3 x atr(14)[1], target = avg price + 2 x atr(14)[1], kept for the trade

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are set from the fill price with the ATR of the bar before the first in-position
      bar, i.e. the signal bar's ATR: sl_stop / tp_stop = k x ATR / close of the signal bar, shifted
      one bar inside stops() and re-based on the fill. Pine places the exit at the fill bar's close,
      so it is live from the next bar; the house stop is live on the fill bar too (stated).
    * Long only; with pyramiding 0 a repeated signal while long is ignored. Opposite entries cannot
      occur. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432178_three_ema_stoch_rsi_atr_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [3.0, 1.5],
    "tp_atr": [2.0, 4.0],
}
DEFAULT_PARAMS = {"e1": 8, "e2": 14, "e3": 50, "rsi_len": 14, "stoch_len": 14, "smooth_k": 3, "smooth_d": 3,
                  "atr_len": 14, "sl_atr": 3.0, "tp_atr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e1, e2, e3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("e1", "e2", "e3"))
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    lo_r, hi_r = r.rolling(n).min(), r.rolling(n).max()
    st = 100 * (r - lo_r) / (hi_r - lo_r)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    le = ((e1 > e2) & (e2 > e3) & (k > d) & (k.shift(1) <= d.shift(1))).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
