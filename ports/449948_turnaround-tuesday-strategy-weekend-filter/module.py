"""Monday weakness bought for Tuesday, 2-hour bars, long only: on a Monday bar (UTC) after a close under the SMA 30, with the previous RSI 3 under 51 and outside May, go long; the first Wednesday bar closes.
Port of FMZ strategy #449948 "Turnaround Tuesday Strategy Weekend Filter" (Turnaround Tuesday).

FMZ source id: 449948

Source
    https://www.fmz.com/strategy/449948 (PineScript v5, FMZ last modified 2024-04-30 16:07:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-148), SMA 30; RSI 3 filter (< 51) on; ATR 10 filter (close / atr < 95) on; exclude May on; dates (always true); 100 % of equity, commission 0.035 %
    dayofweek == monday and close[1] < sma30[1] and rsi3[1] < 51 and close[1] / atr10[1] < 95 and month != 5 -> entry Buy;  dayofweek == wednesday and long -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * dayofweek and month are read on the bar's UTC open time (the exchange time zone, as #435514);
      on 2-hour bars every Monday bar can signal and the first Wednesday bar closes. A repeated entry
      while long is ignored. Long only. The 100 % of equity size is sizing; the commission is a cost
      (not ported). FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; filters from the previous bar.
    2 generic: PASS, weekday seasonality with trend, RSI and ATR filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored; the commission is a cost, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC weekdays and months (exchange time zone, no DST).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449948_turnaround_tuesday_monday_buy_wednesday_exit_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_period": [30, 50],
    "rsi_max": [51.0, 40.0],
}
DEFAULT_PARAMS = {"ma_period": 30, "rsi_max": 51.0, "atr_max": 95.0}


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
    ma = c.rolling(int(p["ma_period"])).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, 10)
    r3 = _rsi(c, 3)
    dow = np.asarray(ix.dayofweek)
    mon = dow == 0
    wed = dow == 2
    not_may = np.asarray(ix.month) != 5
    with np.errstate(invalid="ignore"):
        cond = ((pc < ma.shift(1)) & (r3.shift(1) < float(p["rsi_max"]))
                & (pc / atr.shift(1) < float(p["atr_max"]))).to_numpy()
    le = pd.Series(mon & not_may & cond, index=ix)
    lx = pd.Series(wed, index=ix)
    false = pd.Series(False, index=ix)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
