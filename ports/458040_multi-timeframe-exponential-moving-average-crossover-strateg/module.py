"""Pullback re-crosses of the EMA 21 in an EMA 9 / 21 trend confirmed by 4-hour EMAs, 3-hour bars: with the EMA 9 over the EMA 21 and the close over the 4-hour EMA 9, the close crossing over the EMA 21 goes long; the mirror (close under the 4-hour EMA 21) goes short; reversing. The average-price bracket is armed only by repeat signals and is not ported (pending).
Port of FMZ strategy #458040 "Multi Timeframe Exponential Moving Average Crossover Strategy with Risk Reward Optimization" (Simplified MTF Strategy with RR Ratio).

FMZ source id: 458040

Source
    https://www.fmz.com/strategy/458040 (PineScript v5, FMZ last modified 2024-07-29 14:20:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-211), EMA 9 / 21; 4-hour EMA 9 / 21 (security '240', lookahead off); ATR 14; stop 1.5 ATR, target 5R from the average price (signal bars only)
    ema9 > ema21 and close > ema9_4h and crossover(close, ema21) -> entry Long, exit(avg -+ 1.5 atr / 7.5 atr)
    ema9 < ema21 and close < ema21_4h and crossunder(close, ema21) -> entry Short, exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The '240' request is a HIGHER time frame without lookahead: each 3-hour bar reads the EMAs of the
      last 4-hour bar completed by its close (as #440503), built from the minutes on UTC-aligned
      4-hour bars. The exit is sent only on a signal bar from the average price, na while flat, so the
      opening signal arms nothing and a bracket appears only on a repeat signal inside the trade;
      stops() cannot express this, so it is not ported and the module is marked trailing_stop_pending
      (as #437800); positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "3h"
      from the backtest header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 4-hour EMAs from completed bars; the late-armed bracket pending (mark).
    2 generic: PASS, trend pullback re-crosses with a higher-time-frame filter.
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

NAME = "fmz_458040_ema21_recross_4h_ema_filter_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    bars = df.resample(FREQ, label="left", closed="left").agg(agg).dropna(how="all")
    h4 = df.resample("4h", label="left", closed="left").agg(agg).dropna(how="all")
    f4 = h4["close"].ewm(span=int(p["fast"]), adjust=False).mean().to_numpy()
    s4 = h4["close"].ewm(span=int(p["slow"]), adjust=False).mean().to_numpy()
    done4 = (h4.index + pd.Timedelta(hours=4)).asi8
    done3 = (bars.index + pd.Timedelta(hours=3)).asi8
    k = np.searchsorted(done4, done3, side="right") - 1          # last 4-hour bar closed by the chart bar's close
    ok = k >= 0
    kk = np.where(ok, k, 0)
    bars["ema_f_4h"] = np.where(ok, f4[kk], np.nan)
    bars["ema_s_4h"] = np.where(ok, s4[kk], np.nan)
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up_t = (f > s) & (c > bars_df["ema_f_4h"])
    dn_t = (f < s) & (c < bars_df["ema_s_4h"])
    c1, s1 = c.shift(1), s.shift(1)
    le = up_t & (c > s) & (c1 <= s1)
    se = dn_t & (c < s) & (c1 >= s1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
