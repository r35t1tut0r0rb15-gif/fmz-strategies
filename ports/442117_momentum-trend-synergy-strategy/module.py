"""RMI strength with the SMA 5 side, 1-hour bars: the RMI (21) above 60 with the close above the SMA 5 goes long, under 40 with the close under it goes short; reversing; the author's stop at the
SMA 5 -+ 4 ATR(5), re-sent on every entry-signal bar, is described, not emitted.
Port of FMZ strategy #442117 "Momentum Trend Synergy Strategy" (PresentTrend RMI Synergy - Strategy [presentTrading]).

FMZ source id: 442117

Source
    https://www.fmz.com/strategy/442117 (PineScript v5, FMZ last modified 2024-02-19 14:48:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 209-253), direction Both; RMI 21; presentTrend length 5, multiplier 4
    rmi = 100 - 100 / (1 + rma(up, 21) / rma(down, 21));  long = rmi > 60 and close > sma5 -> entry Long Entry, exit(stop = sma5 - 4 atr5);  short = rmi < 40 and close < sma5 -> entry Short Entry, exit(stop = sma5 + 4 atr5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-sent on every bar the (level) entry condition holds, from that bar's SMA 5 and ATR,
      so it moves with the bars while the condition lasts: a moving stop the house stops (fixed at the
      fill) cannot express. It is kept pending (mark trailing_stop_pending, as #437036) and positions end
      at the opposite entry until the project decides. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, RMI and SMA side; the moving stop is pending.
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

NAME = "fmz_442117_rmi_sma5_side_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_rmi": [21, 14],
    "length_st": [5, 10],
}
DEFAULT_PARAMS = {"length_rmi": 21, "length_st": 5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    k = int(p["length_rmi"])
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), k), _rma((-d).clip(lower=0), k)
    with np.errstate(divide="ignore", invalid="ignore"):
        rmi = 100 - 100 / (1 + up / dn)
    sma = c.rolling(int(p["length_st"])).mean()
    le = (rmi > 60) & (c > sma)
    se = (rmi < 40) & (c < sma)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
