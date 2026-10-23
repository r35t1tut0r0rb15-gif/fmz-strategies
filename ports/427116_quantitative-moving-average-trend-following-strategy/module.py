"""A fast and a slow elastic volume-weighted average (EVWMA over 5- and 11-bar volume sums), 2-hour bars: the fast one above the slow one goes long, below goes short, each with a 9 % stop from the entry; reversing.
Port of FMZ strategy #427116 "Quantitative Moving Average Trend Following Strategy" (EVWMA 6HR).

FMZ source id: 427116

Source
    https://www.fmz.com/strategy/427116 (PineScript v4, FMZ last modified 2023-09-18 13:23:52).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 177-275), EVWMA sums 5 / 11; stop type Fixed 9 % (ATR 20 x 1.5 alternative off); longs and shorts on
    evwma := ((sum(volume, n) - volume) x nz(evwma[1], close) + volume x close) / sum(volume, n)
    fast > slow -> entry L, exit("L SL", stop = avg x 0.91 while in a long signal);  fast < slow -> entry S, exit("S SL", stop = avg x 1.09)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are sent on every bar the condition holds (repeats ignored), so after a stop the next
      such bar re-enters. The fixed stop is 9 % of the fill (a scalar fraction); the ATR stop type is not
      selected. The EVWMA starts from the close (nz). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. The 100 % of equity size and commission
      are sizing / costs. FREQ = "2h" from the backtest header (the title's 6HR is not the header).

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop from the fill.
    2 generic: PASS, elastic volume-weighted average cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 10000, commission 0.075 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in both EVWMAs (volume weights and the rolling volume sums); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427116_evwma5_11_state_pct9_stop_reversal"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast_sum_length": [5, 10],
    "slow_sum_length": [11, 30],
}
DEFAULT_PARAMS = {"fast_sum_length": 5, "slow_sum_length": 11, "sl": 0.09}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _evwma(c, v, n):
    """The source's EVWMA: ((sum(v, n) - v) x nz(prev, close) + v x close) / sum(v, n)."""
    s = v.rolling(n).sum().to_numpy(dtype=float)
    cv, vv = c.to_numpy(dtype=float), v.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    prev = np.nan
    for i in range(len(cv)):
        base = cv[i] if np.isnan(prev) else prev
        out[i] = ((s[i] - vv[i]) * base + vv[i] * cv[i]) / s[i] if s[i] != 0 else np.nan
        prev = out[i]
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    fast = _evwma(c, v, int(p["fast_sum_length"]))
    slow = _evwma(c, v, int(p["slow_sum_length"]))
    le, se = fast > slow, fast < slow
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
