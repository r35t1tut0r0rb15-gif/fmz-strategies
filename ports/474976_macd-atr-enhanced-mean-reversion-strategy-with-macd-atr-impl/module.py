"""Bollinger 20 / 2 re-entries with a MACD filter, 3-hour bars: a close crossing back over the lower band with MACD over its signal goes long, back under the upper band with MACD under it goes short; reversing. Each position has a 1.5 ATR stop and 3 ATR target from its fill price (the ATR of the bar before the fill; the source re-sends them with each bar's ATR, pending).
Port of FMZ strategy #474976 "均值回归增强型MACD-ATR策略Enhanced-Mean-Reversion-Strategy-with-MACD-ATR-Implementation" (Enhanced Mean Reversion with MACD and ATR).

FMZ source id: 474976

Source
    https://www.fmz.com/strategy/474976 (PineScript v5, FMZ last modified 2024-12-13 11:41:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-151), BB 20, 2 sd; MACD 12 / 26 / 9; ATR 14 x 1.5: stop 1 x, target 2 x from avg
    crossover(close, lower) and macd > signal -> entry Long;  crossunder(close, upper) and macd < signal -> entry Short;  long: exit(stop = avg - 1.5 atr, limit = avg + 3 atr) every bar;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent every bar from the fill price with the current ATR: ported with the ATR
      of the bar before the fill (as fractions of the fill), the moving part kept pending (mark
      trailing_stop_pending). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      3-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ATR bracket from the fill.
    2 generic: PASS, band re-entries with a MACD filter and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_474976_bb20_reentry_macd_filter_atr_bracket_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_length": [20, 50],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "atr_mult": 1.5, "bb_mult": 2.0}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (c > dn) & (c.shift(1) <= dn.shift(1)) & (macd > sig)
    se = (c < up) & (c.shift(1) >= up.shift(1)) & (macd < sig)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["atr_mult"]) * _atr(bars_df, 14).shift(1) / bars_df["open"]   # the ATR of the bar before the fill
    return {"sl_stop": a, "tp_stop": 2 * a}


def portfolio_kwargs(**params):
    return {}
