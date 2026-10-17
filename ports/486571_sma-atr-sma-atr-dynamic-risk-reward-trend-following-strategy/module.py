"""SMA 7 / 25 crosses on the SMA 99 side with a bar-extreme ATR stop and a 2 ATR target, 1-hour bars: SMA 7 crossing above
SMA 25 with the close above SMA 99 goes long, stop one ATR under the bar's low, target 2 ATR over the close; the
mirror goes short.
Port of FMZ strategy #486571 "SMA-ATR动态风险回报比趋势跟踪策略-SMA-ATR-Dynamic-Risk-Reward-Trend-Following-Strategy" (TRH Backtest SMA ATR Variable RR).

FMZ source id: 486571

Source
    https://www.fmz.com/strategy/486571 (PineScript v5, FMZ last modified 2025-03-14 09:45:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 246-281), SMA 7 / 25 / 99, ATR 14 x 1, RR 2 (6 on crosses, see below)
    long = crossover(sma7, sma25) and close > sma99;  short = crossunder(sma7, sma25) and close < sma99
    riskRewardRatio = 2.0; if longCross or shortCross: riskRewardRatio = 6.0 (a new local variable)
    every bar: exit(long: stop = low - atr, limit = close + atr x RR; short: stop = high + atr, limit = close - atr x RR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * `riskRewardRatio = 6.0` inside the if declares a new local variable (= not :=), so the ratio is always 2 as
      written.
    * The bracket is re-issued every bar from the current bar (moving): fixed at the signal bar, mark
      trailing_stop_pending: long sl = (close - low + ATR) / close, tp = rr x ATR / close, short mirrored, picked by the
      signal's side, shifted one bar inside stops() and re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED); the two crosses cannot fall on one bar. Stop module: portfolio_kwargs {}
      (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar (re-issue marked).
    2 generic: PASS, moving averages and ATR multiples.
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

NAME = "fmz_486571_sma7_25_cross_bar_extreme_atr"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.0, 1.5],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "atr_mult": 1.0, "rr": 2.0}


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


def _signals(bars_df):
    c = bars_df["close"]
    s7, s25, s99 = (c.rolling(n).mean() for n in (7, 25, 99))
    long_e = ((s7 > s25) & (s7.shift(1) <= s25.shift(1)) & (c > s99)).astype(bool)
    short_e = ((s7 < s25) & (s7.shift(1) >= s25.shift(1)) & (c < s99)).astype(bool)
    return long_e, short_e


def simulate(bars_df, **params):
    long_e, short_e = _signals(bars_df)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df)
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = p["atr_mult"] * _atr(bars_df, int(p["atr_len"]))
    sl = ((c - lo + atr) / c).where(long_e, ((h + atr - c) / c).where(short_e)).shift(1)
    tp = (p["rr"] * atr / c).where(long_e | short_e).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
