"""Stochastic (14, 3, 3) extremes in the direction of the SMA 9 slope, 1-minute bars, with a 2 % stop: %K crossing under 20 with a rising SMA goes long, %K crossing over 80 with a falling SMA goes short;
reversing (the exit tests can never be true).
Port of FMZ strategy #449958 "Stochastic Oscillator and Moving Average Strategy" (Estrategia Stoch + MA c/ SL).

FMZ source id: 449958

Source
    https://www.fmz.com/strategy/449958 (PineScript v5, FMZ last modified 2024-04-30 16:45:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-159), stochastic 14 / 3 / 3, levels 20 / 80; SMA 9; stop 2 % of the signal close; qty 1
    crossunder(k, 20) and sma rising -> entry Long, exit(stop = close x 0.98);  crossover(k, 80) and sma falling -> entry Short, exit(stop = close x 1.02)
    crossover(k, sma) and sma falling -> close Long;  crossunder(k, sma) and sma rising -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rules of #449526 without its (never-true) filter branch, on 1-minute bars; a near-duplicate
      in the corpus, ported under rule 7. %K (0 to 100) never crosses a price average, so both closes
      never act, as written. The stop is a fixed 2 % of the signal close, ported as a fraction of the
      fill (sl_stop 0.02, as #437751); a repeated signal inside the trade re-issues it: not expressible
      (mark trailing_stop_pending). strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The qty 1 is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry (re-sent levels marked).
    2 generic: PASS, stochastic extremes with an SMA slope filter, percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the qty 1 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND449526 (2 members, best partner #449526, Jaccard 0.707); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_449958_stoch_extreme_sma9_slope_2pct_stop_1m_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 9],
    "sl": [0.02, 0.01],
}
DEFAULT_PARAMS = {"length": 14, "sl": 0.02, "smooth_k": 3, "oversold": 20.0, "overbought": 80.0, "ma_len": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).where(hh > ll)).rolling(int(p["smooth_k"])).mean()
    ma = c.rolling(int(p["ma_len"])).mean()
    up, dn = ma > ma.shift(1), ma < ma.shift(1)
    os_, ob = float(p["oversold"]), float(p["overbought"])
    le = (k < os_) & (k.shift(1) >= os_) & up
    se = (k > ob) & (k.shift(1) <= ob) & dn
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
