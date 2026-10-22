"""Stochastic 2 turns against the EMA 200, 2-hour bars: under the EMA 200, %K rising back to 20 or more goes long with a stop 1 and a target 16 price units from the signal close; over it, %K falling back to 80 or less goes short (mirrored levels); reversing.
Port of FMZ strategy #454145 "基于200日均线和随机振子的趋势追踪策略-Trend-Following-Strategy-Based-on-200-Day-Moving-Average-and-Stochastic-Oscillator" (WWCD Bot).

FMZ source id: 454145

Source
    https://www.fmz.com/strategy/454145 (PineScript v5, FMZ last modified 2024-06-14 15:32:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-129), EMA 200; stochastic 2 (its EMA 3 unused); stop 1.00 / target 16 price units; lot 1
    close < ema200 and k >= 20 and k[1] < 20 -> entry Buy, exit(stop = close - 1, limit = close + 16)
    close > ema200 and k <= 80 and k[1] > 80 -> entry Sell, exit(stop = close + 1, limit = close - 16)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 1 / 16 price units are read against BTC near 42000 like other price units (#440456): the
      port sets the stop and target at the fractions 1 / 42000 and 16 / 42000 of the fill. A repeat
      signal inside a trade re-issues the levels, which stops() cannot express: the opening levels are
      kept and the module is marked trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. The lot 1 is
      sizing. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the price-unit levels as fractions of 42000; re-issued levels pending (mark).
    2 generic: PASS, stochastic turns against the EMA 200.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot 1 stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_454145_stoch2_turn_vs_ema200_point_bracket_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stoch_len": [2, 5],
    "sl_frac": [2.38e-05, 0.01],
    "tp_frac": [0.000381, 0.02],
}
DEFAULT_PARAMS = {"stoch_len": 2, "sl_frac": 2.38e-05, "tp_frac": 0.000381, "ema_len": 200}


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
    n = int(p["stoch_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    k = 100 * (c - ll) / rng.where(rng > 0)
    k1 = k.shift(1)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = (c < ema) & (k >= 20) & (k1 < 20)
    se = (c > ema) & (k <= 80) & (k1 > 80)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
