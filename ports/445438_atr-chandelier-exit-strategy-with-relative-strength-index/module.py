"""Chandelier-line crossings at RSI extremes, 1-minute bars, with an ATR bracket: the close crossing over the long chandelier line (8-bar high less 3 ATR) with the RSI 11 under 20 goes long, the close
crossing under the short line (8-bar low plus 3 ATR) with the RSI over 80 goes short; stop 2 ATR, target 1 ATR from the signal close; reversing.
Port of FMZ strategy #445438 "ATR Chandelier Exit Strategy with Relative Strength Index" (ATR Chandelier Exit Strategy with Stop Loss and Take Profit).

FMZ source id: 445438

Source
    https://www.fmz.com/strategy/445438 (PineScript v5, FMZ last modified 2024-03-19 14:05:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 191-229), ATR 8 x 3 (chandelier); RSI 11, levels 20 / 80; stop 2 ATR, target 1 ATR
    crossover(close, highest(high, 8) - 3 atr) and rsi < 20 -> entry Long, exit(stop = close - 2 atr, limit = close + 1 atr)
    crossunder(close, lowest(low, 8) + 3 atr) and rsi > 80 -> entry Short, exit(stop = close + 2 atr, limit = close - 1 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and ATR: sl_stop = 2 ATR / close and tp_stop
      = 1 ATR / close, shifted one bar inside stops() and re-based on the fill. A repeated signal inside
      the trade re-issues the levels: not expressible (mark trailing_stop_pending); the opening levels
      are kept. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar (re-sent levels marked).
    2 generic: PASS, chandelier-line crossings at RSI extremes with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_445438_chandelier_cross_rsi_extreme_atr_bracket_reversal"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [3.0, 2.0],
    "sl_atr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"atr_mult": 3.0, "sl_atr": 2.0, "tp_atr": 1.0, "atr_len": 8, "rsi_len": 11, "os": 20.0, "ob": 80.0}


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
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["atr_len"])
    atr = _atr(bars_df, n)
    cl = h.rolling(n).max() - atr * float(p["atr_mult"])
    cs = lo.rolling(n).min() + atr * float(p["atr_mult"])
    r = _rsi(c, int(p["rsi_len"]))
    c1 = c.shift(1)
    le = (c > cl) & (c1 <= cl.shift(1)) & (r < float(p["os"]))
    se = (c < cs) & (c1 >= cs.shift(1)) & (r > float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
