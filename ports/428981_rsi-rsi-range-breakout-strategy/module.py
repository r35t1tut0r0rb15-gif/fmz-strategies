"""Smoothed RSI(3) dip buyer, long only, hourly bars: the 3-bar average of RSI 3 under 35 with its 5-bar
average turning up goes long; the mirror condition at 80 closes it; each long has a 2.6 % stop and a target.
Port of FMZ strategy #428981 "RSI区间突破策略RSI-Range-Breakout-Strategy" (Strategy RSI | Fadior).

FMZ source id: 428981

Source
    https://www.fmz.com/strategy/428981 (PineScript v4, FMZ last modified 2023-10-11 15:54:11).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 133-169), RSI 3, smoothing 3 / 5, 35 / 80, stop 2.6 %, target 300 ticks, long only
    longCondition = sma(rsi,3) < 35 and sma(rsi,5) > sma(rsi,5)[1] -> entry long; exit(stop = close - close x 0.026, profit = 300)
    shortCondition = sma(rsi,3) > 80 and sma(rsi,5) < sma(rsi,5)[1] -> entry short (allow_entry_in long: closes the long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.risk.allow_entry_in(long) (Long only defaults to true) turns the short entry into an
      exit of the long: a close signal. Long only.
    * The stop is 2.6 % below the signal bar's close; the house sl_stop is 2.6 % of the fill (the
      next open). Criterion 2: the 300-tick target becomes tp_atr x Wilder ATR(14) of the signal bar
      (shifted one bar inside stops(), re-based on the fill): 30 USD on hourly BTC is about 0.2 ATR.
    * The source re-places its exit on every later long signal while the long is open (a new stop 2.6 %
      under that bar's close): a stop that moves after entry, which stops() cannot express (rule 2). The
      port keeps the entry's bracket; the re-placement is pending: mark trailing_stop_pending.
    * The strategy() line is commented out (pyramiding 0 by default). Stop module: portfolio_kwargs {}
      (driver D4); Opposite entries cannot occur (long only). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (re-placement pending).
    2 generic: ADAPT, the tick target -> an ATR multiple; the stop is a percentage.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_428981_smoothed_rsi3_dip_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "thresh_low": [35, 25],
    "tp_atr": [0.2, 1.0],
}
DEFAULT_PARAMS = {"length": 3, "thresh_low": 35, "thresh_high": 80, "smooth1": 3, "smooth2": 5,
                  "sl": 0.026, "tp_atr": 0.2, "atr_length": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.diff()
    n = int(p["length"])
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn))), index=c.index)
    rsi = rsi.where(up.notna() & dn.notna())
    s1, s2 = rsi.rolling(int(p["smooth1"])).mean(), rsi.rolling(int(p["smooth2"])).mean()
    long_e = ((s1 < p["thresh_low"]) & (s2 > s2.shift(1))).astype(bool)
    long_x = ((s1 > p["thresh_high"]) & (s2 < s2.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / c
    return {"sl_stop": float(p["sl"]), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
