"""Share of green bars over 13 bars, 1-minute bars: 70 % or more green bars goes long, 30 % or fewer goes short; reversing; each position has an ATR stop (10 x ATR 14) and a target 1.6 times the stop distance.
Port of FMZ strategy #438012 "Positive Bars Percentage Breakout Strategy" (Positive Bars % Strat).

FMZ source id: 438012

Source
    https://www.fmz.com/strategy/438012 (PineScript v4, FMZ last modified 2024-01-08 10:32:25).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 175-267), direction all; lookback 13, upper 70, lower 30; stops on, type ATR Stop (ATR 14 x 10), reward 1.6; direct reverse on, reverse trades off
    positiveBarsPercent = count(close > open over 13 bars) / 13 x 100;  >= 70 -> entry long;  <= 30 -> entry short
    ATR stop: at the bar the position changes, ohlc4 -/+ 10 ATR(14);  target = avg price +/- 1.6 x (avg price - stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR stop is taken at the bar the position changes (the fill bar), from that bar's ohlc4 and
      ATR, known only at its close, and the bracket works from the next bar. The house reads a stop at the
      fill's open: sl_stop = k_atr x ATR(14) / close of the signal bar (shifted one bar inside stops(),
      re-based on the fill), tp_stop = 1.6 x sl_stop. The Swing and Strategy stop types are not selected.
      strategy.entry reverses (direct reverse on): REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). The size, capital and commission are sizing / costs. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, green-bar share and ATR distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438012 (2 members, best partner #441962, Jaccard 0.687); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438012_positive_bars_pct_atr_bracket"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [13, 26],
    "k_atr": [10.0, 5.0],
}
DEFAULT_PARAMS = {"lookback": 13, "k_atr": 10.0, "upper": 70.0, "lower": 30.0, "atr_len": 14, "rr": 1.6}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["lookback"])
    pct = (c > o).astype(float).rolling(n).sum() / n * 100.0
    false = pd.Series(False, index=bars_df.index)
    return pct >= float(p["upper"]), false, pct <= float(p["lower"]), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["rr"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
