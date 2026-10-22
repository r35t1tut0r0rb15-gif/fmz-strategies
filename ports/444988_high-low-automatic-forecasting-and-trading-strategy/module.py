"""Breaks of the 09:00 UTC hourly bar's range with an RSI filter, 1-hour bars: a close above the latest 09:00 bar's high with the RSI 14 above 60 goes long, a close under its low with the RSI under 40 goes
short; reversing (the targets and stops only plot).
Port of FMZ strategy #444988 "High Low Automatic Forecasting and Trading Strategy" (9:15 AM High/Low with Automatic Forecasting).

FMZ source id: 444988

Source
    https://www.fmz.com/strategy/444988 (PineScript v5, FMZ last modified 2024-03-15 17:22:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-181), session 09:00-09:15 (start hour 9, minutes 0-15); RSI 14, levels 60 / 40; targets / stops +- 200 (plot only)
    hour == 9 and minute == 0 -> sessionHigh / sessionLow = high / low (var, kept until the next one);  close > sessionHigh and rsi > 60 -> entry Long;  close < sessionLow and rsi < 40 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour and minute are read on the bar's UTC open time (the exchange time zone, as #435514). On
      1-hour bars the 09:00-09:15 window is the 09:00 bar alone, so the range is that bar's high and
      low, kept until the next day's 09:00 bar (none before the first one). The +- 200 targets and
      stops are only plotted. A near-duplicate of #445477 in the corpus, ported under rule 7.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the range from the completed 09:00 bar.
    2 generic: PASS, breaks of a fixed-hour range with RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG444988 (2 members, best partner #445477, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:00 UTC hourly bar (the exchange time zone), no DST.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444988_0900_utc_bar_range_break_rsi_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "session_hour": [9, 13],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"session_hour": 9, "rsi_length": 14, "ob": 60.0, "os": 40.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ix = bars_df.index
    at = (ix.hour == int(p["session_hour"])) & (ix.minute == 0)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    sh, sl = np.full(m, np.nan), np.full(m, np.nan)
    a = b = np.nan
    for i in range(m):
        if at[i]:
            a, b = hv[i], lv[i]
        sh[i], sl[i] = a, b
    r = _rsi(c, int(p["rsi_length"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        le = (cv > sh) & (r > float(p["ob"]))
        se = (cv < sl) & (r < float(p["os"]))
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
