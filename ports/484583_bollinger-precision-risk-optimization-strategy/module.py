"""Bollinger re-entries at RSI extremes with a 4 % stop and an 8 % target, 1-hour bars: the close crossing back above the
lower band with RSI 14 below 30 goes long; crossing back below the upper band with RSI above 70 goes short; each trade
has a 4 % stop and an 8 % target from the signal close.
Port of FMZ strategy #484583 "布林带精准风险优化策略-Bollinger-Precision-Risk-Optimization-Strategy" (Bollinger Precision Strategy).

FMZ source id: 484583

Source
    https://www.fmz.com/strategy/484583 (PineScript v6, FMZ last modified 2025-03-03 10:07:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 189-251), BB 20 x 2, RSI 14 (30 / 70), SL 4 %, TP 8 %
    buy = crossover(close, lower) and rsi < 30 -> entry long, close short, exit(stop = close x 0.96, limit = close x 1.08)
    sell = crossunder(close, upper) and rsi > 70 -> entry short, close long, exit(stop x 1.04, limit x 0.92)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is from the signal close, re-based on the fill: sl_stop / tp_stop scalars. A same-side signal while
      held re-places it: mark trailing_stop_pending; the port keeps the entry's bracket.
    * The close after each entry is the reversal itself (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal close (re-placement marked).
    2 generic: PASS, bands, an oscillator and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_484583_bb_reentry_rsi_pct_bracket"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [4.0, 2.0],
    "tp_pct": [8.0, 4.0],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_mult": 2.0, "rsi_len": 14, "oversold": 30, "overbought": 70, "sl_pct": 4.0,
                  "tp_pct": 8.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((c > lo) & (c.shift(1) <= lo.shift(1)) & (rsi < p["oversold"])).astype(bool)
    short_e = ((c < up) & (c.shift(1) >= up.shift(1)) & (rsi > p["overbought"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
