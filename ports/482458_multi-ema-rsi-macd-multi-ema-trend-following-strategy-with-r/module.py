"""EMA 5 / 14 / 34 / 55 stacks with a MACD zero-line crossing and RSI on the 50 side, 4-hour bars: a rising stack goes long, a falling stack goes short; the short's take-profit order is marketable at once, so each short is closed on its fill bar; the long's stop at EMA 34 is re-sent every bar (pending); reversing.
Port of FMZ strategy #482458 "Multi-EMA趋势追踪型RSI-MACD动量验证策略-Multi-EMA-Trend-Following-Strategy-with-RSI-MACD-Momentum-Validation" (EMA + MACD + RSI Strategy).

FMZ source id: 482458

Source
    https://www.fmz.com/strategy/482458 (PineScript v5, FMZ last modified 2025-02-18 15:13:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-138), EMA 5 / 14 / 34 / 55; RSI 14; MACD 12 / 26 / 9; stop = ema34, limit = 3 x ema34 for both sides
    ema5 > ema14 > ema34 > ema55 and (macd crosses 0 either way) and rsi > 50 -> entry Long;  falling stack, same cross, rsi < 50 -> entry Short
    every bar: exit Long (stop = ema34, limit = ema34 x 3);  exit Short (stop = ema34, limit = ema34 x 3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MACD condition is a crossing of zero in either direction, as written. The exits are re-sent on
      every bar with the latest EMA 34: for a short, the buy limit at three times EMA 34 is far above the
      price, so it is marketable as soon as the short fills; the short is closed on its fill bar (one bar
      late, as #458256), and a repeat short signal on that bar keeps it. For a long, the target at three
      times EMA 34 is out of reach and the stop follows EMA 34 bar by bar: stops() cannot express a level
      re-set every bar, so it is described here and kept pending (as #438034, mark trailing_stop_pending);
      longs end at a short entry until then. REVERSAL INTENDED. No sizing code. FREQ = "4h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the long's moving stop described (pending).
    2 generic: PASS, EMA stack with MACD zero crossings and RSI side.
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

NAME = "fmz_482458_ema_stack_macd_zero_cross_rsi50_short_closed_at_fill_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "macd_fast": [12, 8],
    "macd_slow": [26, 21],
}
DEFAULT_PARAMS = {"macd_fast": 12, "macd_slow": 26, "rsi_length": 14}


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
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    e5, e14, e34, e55 = ema(5), ema(14), ema(34), ema(55)
    r = _rsi(c, int(p["rsi_length"]))
    macd = ema(p["macd_fast"]) - ema(p["macd_slow"])
    zx = ((macd > 0) & (macd.shift(1) <= 0)) | ((macd < 0) & (macd.shift(1) >= 0))
    le = (e5 > e14) & (e14 > e34) & (e34 > e55) & zx & (r > 50)
    se = (e5 < e14) & (e14 < e34) & (e34 < e55) & zx & (r < 50)
    sx = se.shift(1, fill_value=False) & ~le & ~se        # the marketable take-profit at the fill
    false = pd.Series(False, index=c.index)
    return le, false, se, sx


def portfolio_kwargs(**params):
    return {}
