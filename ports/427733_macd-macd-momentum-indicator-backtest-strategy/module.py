"""MACD cross after an RSI turn: the MACD histogram turning positive within 7 bars after RSI 14 crossed
back above 30 goes long; turning negative within 7 bars after RSI crossed back below 70 goes short.
Each position has a 15 % stop.
Port of FMZ strategy #427733 "MACD Momentum Indicator Backtest Strategy".

FMZ source id: 427733

Source
    https://www.fmz.com/strategy/427733 (PineScript v5, FMZ last modified 2023-09-24 13:21:54).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-250), RSI 14 (30 / 70, look-back 7), MACD 12/26/9 EMA, stops 15 %
    coCheck = crossover(rsi, 30) on any of the previous 7 bars (not the current one); cuCheck mirrors
    crossover(macd - signal, 0) and coCheck -> entry long; crossunder and cuCheck -> entry short
    exit(stop = position_avg_price x (1 -+ 15 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: Pine defaults (one position).
    * The stop is a percentage of the entry price: sl_stop 0.15 (FMZ-C rule; percent-of-entry stops
      stay fractions).
    * The date range is dropped (inDateRange is true).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, oscillator levels and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() sizing stored; the stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427733_macd_cross_after_rsi_turn"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_lookback": [7, 14],
    "loss_pct": [15.0, 5.0],
}
DEFAULT_PARAMS = {"length": 14, "over_sold": 30, "over_bought": 70, "rsi_lookback": 7,
                  "fast": 12, "slow": 26, "signal": 9, "loss_pct": 15.0}


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
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = 100 - 100 / (1 + up / dn)
    co = ((rsi > p["over_sold"]) & (rsi.shift(1) <= p["over_sold"])).astype(int)
    cu = ((rsi < p["over_bought"]) & (rsi.shift(1) >= p["over_bought"])).astype(int)
    lb = int(p["rsi_lookback"])
    co_chk = co.shift(1).rolling(lb, min_periods=1).max() > 0
    cu_chk = cu.shift(1).rolling(lb, min_periods=1).max() > 0
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    valid = rsi.notna()
    long_e = (valid & (delta > 0) & (delta.shift(1) <= 0) & co_chk).astype(bool)
    short_e = (valid & (delta < 0) & (delta.shift(1) >= 0) & cu_chk).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["loss_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
