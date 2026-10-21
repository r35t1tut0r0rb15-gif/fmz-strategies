"""SMA 14 / 28 crossings with a break-even stop, 1-hour bars, long only: the cross up buys, the cross down closes; a stop 3 % under the entry moves to the entry price once a close is 3 % above it.
Port of FMZ strategy #438068 "Percentage Trailing Stop Loss Strategy" (Break even stop loss (% of instrument price)).

FMZ source id: 438068

Source
    https://www.fmz.com/strategy/438068 (PineScript v5, FMZ last modified 2024-01-08 17:12:46).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 135-170), trail long loss 3 %; SMA 14 / 28; long only
    crossover(sma 14, sma 28) -> entry Long;  crossunder -> close Long;  long: stop = entry x 0.97, raised to the entry once close > entry x 1.03 (never lowered);  exit(stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop starts 3 % under the entry fill and moves to the entry price once a close is 3 % in profit:
      the house sl_stop = 0.03 with a lock_in trail of gain 0.03 on closes (anchor close). The exit is
      sent from the first bar close inside the trade; the port starts it at the fill. Long only
      (allow_entry_in long). Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house lock-in trail.
    2 generic: PASS, SMA crossings; break-even stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438068_sma14_28_break_even_stop_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.03, 0.05],
    "fast": [14, 7],
}
DEFAULT_PARAMS = {"trail_pct": 0.03, "fast": 14, "slow": 28}


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
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = float(p["trail_pct"])
    return {"sl_stop": t, "trail": {"type": "lock_in", "gain": t, "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
