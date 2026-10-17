"""Spinning-top colour changes after three same-colour candles with a bar-extreme stop and a 1.5 R target, 3-hour bars:
a green spinning top after three red candles goes long with the stop just under its low; a red spinning top after
three green candles goes short with the stop just over its high; the target is 1.5 times the stop distance.
Port of FMZ strategy #488382 "多因子顶部旋转反转策略与风险收益优化系统-Multi-Factor-Spinning-Top-Reversal-Strategy-with-Risk-Reward-Optimization" (Strategy Spinning Top with SL & TP).

FMZ source id: 488382

Source
    https://www.fmz.com/strategy/488382 (PineScript v5, FMZ last modified 2025-03-27 09:54:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 187-227), body < 30 % of the range, |upper - lower wick| <= 20 % of the range
    colorChangeBullish = three red candles then a green one;  isSpinningTop = small body and balanced wicks
    bullish and spinning top -> entry long + exit(stop = low - 4, limit = close + 1.5 x (close - stop))
    bearish and spinning top -> entry short + exit(stop = high + 4, limit = close - 1.5 x (stop - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 4-price-unit buffer on the author's 3-hour ETH_USDT (3-hour ATR about 40 in early 2025) is
      about 0.1 Wilder ATR(14) (judgement before any backtest): buffer_atr x ATR of the signal bar.
    * The bracket is fixed at the signal bar and picked by the signal's side: long sl = (close - low + buffer) /
      close, short sl = (high - close + buffer) / close, tp = rr x sl, shifted one bar inside stops() and re-based on
      the fill (house rule).
    * A same-side signal while held re-places the bracket from the new bar: mark trailing_stop_pending; the port keeps
      the entry's bracket.
    * Entries reverse (REVERSAL INTENDED); the two colour changes cannot fall on one bar. Stop module:
      portfolio_kwargs {} (D4). FREQ = "3h" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: ADAPT, the price-unit buffer -> an ATR multiple; candle proportions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488382_spinning_top_colour_change_bracket"
FAMILY = "candlestick_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "buffer_atr": [0.1, 0.5],
    "rr": [1.5, 2.0],
}
DEFAULT_PARAMS = {"body_frac": 0.3, "wick_frac": 0.2, "buffer_atr": 0.1, "rr": 1.5, "atr_len": 14}


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
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    green, red = c > o, c < o
    three_red = red.shift(1, fill_value=False) & red.shift(2, fill_value=False) & red.shift(3, fill_value=False)
    three_green = (green.shift(1, fill_value=False) & green.shift(2, fill_value=False)
                   & green.shift(3, fill_value=False))
    rng = h - lo
    upper = h - np.maximum(c, o)
    lower = np.minimum(c, o) - lo
    spin = ((c - o).abs() < rng * p["body_frac"]) & ((upper - lower).abs() <= rng * p["wick_frac"])
    return (three_red & green & spin).astype(bool), (three_green & red & spin).astype(bool)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    buf = p["buffer_atr"] * _atr(bars_df, int(p["atr_len"]))
    sl_l = (c - lo + buf) / c
    sl_s = (h - c + buf) / c
    sl = sl_l.where(long_e, sl_s.where(short_e)).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
