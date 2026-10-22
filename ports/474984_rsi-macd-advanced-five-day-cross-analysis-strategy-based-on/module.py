"""RSI extremes in the last 5 bars after the first MACD crossings, 2-hour bars: once a MACD cross up has ever happened, an RSI 14 over 70 within 5 bars goes short; once a cross down has ever happened, an RSI under 30 within 5 bars goes long (the long wins a bar with both); reversing. Each position has a 2 % stop and target from its fill.
Port of FMZ strategy #474984 "基于RSI和MACD的五日内交叉灵活入场策略优化版本研究-Advanced-Five-Day-Cross-Analysis-Strategy-Based-on-RSI-and-MACD-Integration" (MACD & RSI Strategy with SL/TP and Flexible Entry (5 bars)).

FMZ source id: 474984

Source
    https://www.fmz.com/strategy/474984 (PineScript v5, FMZ last modified 2024-12-13 12:01:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-165), RSI 14, 70 / 30; MACD 12 / 26 / 9; stop / target 2 % of avg (constants)
    var crossOverRecent, crossUnderRecent: set true by any cross in the last 5 bars, never reset;  highest(rsi, 5) > 70 and crossOverRecent -> entry Short;  lowest(rsi, 5) < 30 and crossUnderRecent -> entry Long;  position: exit(stop / limit = avg -/+ 2 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "recent" MACD flags are var and never reset, so after the first cross of each kind they stay
      true, as written. The long is sent after the short, so it wins a bar with both (#437773). The
      bracket is re-sent while in a position from strategy.position_avg_price, the fill price: fixed
      fractions, active from the fill (as #440797). Entries repeat while the tests hold (ignored while
      held). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the average-price bracket as fixed fractions.
    2 generic: PASS, RSI-extreme windows after MACD crossings with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474984_rsi5bar_extreme_after_macd_cross_pct_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {}
DEFAULT_PARAMS = {}


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


def simulate(bars_df, **params):
    c = bars_df["close"]
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    xo = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    xu = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    seen_xo = xo.cummax()                       # var flag set by any cross, never reset
    seen_xu = xu.cummax()
    le = (r.rolling(5).min() < 30) & seen_xu
    se = (r.rolling(5).max() > 70) & seen_xo & ~le    # the later long entry wins a bar with both
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    return {"sl_stop": 0.02, "tp_stop": 0.02}


def portfolio_kwargs(**params):
    return {}
