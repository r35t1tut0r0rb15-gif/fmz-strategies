"""MACD signal crossings within 10 bars of an RSI extreme, 1-hour bars: a cross up within 10 bars of the RSI 14 at 30 or less goes long, a cross down within 10 bars of the RSI at 70 or more goes short;
reversing (the 50 % bracket from the average price is armed only by a repeated signal and is not ported).
Port of FMZ strategy #449815 "MACD与RSI结合的长线交易策略-MACD-and-RSI-Combined-Long-term-Trading-Strategy" (spl Long Strategy (MACD and RSI)).

FMZ source id: 449815

Source
    https://www.fmz.com/strategy/449815 (PineScript v5, FMZ last modified 2024-04-29 14:31:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-199), RSI 14 (30 / 70); MACD 12 / 26 / 9; stop / target 50 % of the average price; long and short on; dates (always true); 100 % of equity
    barssince(rsi <= 30) <= 10 and crossover(macd, signal) -> entry Long, exit(stop = avg x 0.5, limit = avg x 1.5);  barssince(rsi >= 70) <= 10 and crossunder -> entry Short, exit(avg x 1.5 / 0.5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is called only on a signal bar, with levels from the average price, which is na
      while flat (and the old position's price when reversing): a bracket for the new trade appears
      only if the same signal repeats inside it, so it is not ported (mark trailing_stop_pending, as
      #437800; 50 % levels are rarely reached). Positions end at the opposite entry. strategy.entry
      reverses: REVERSAL INTENDED. The 100 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket not ported (mark).
    2 generic: PASS, MACD crossings after RSI extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored; the percent bracket quoted in original_sizing.txt.
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

NAME = "fmz_449815_macd_cross_after_rsi_extreme_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "window": [10, 5],
}
DEFAULT_PARAMS = {"rsi_len": 14, "window": 10, "os": 30.0, "ob": 70.0}


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


def _since(cond):
    """ta.barssince: bars since the condition was last true, na before the first time."""
    v = cond.to_numpy()
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    w = int(p["window"])
    with np.errstate(invalid="ignore"):
        was_os = _since(r <= float(p["os"])) <= w
        was_ob = _since(r >= float(p["ob"])) <= w
    xo = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    xu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(was_os & xo, index=ix), false, pd.Series(was_ob & xu, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
