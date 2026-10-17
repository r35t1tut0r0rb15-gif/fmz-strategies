"""EMA 21 / 55 crosses with an ATR bracket, 1-hour bars: the EMA 21 crossing above the EMA 55 goes long, crossing below
goes short; each trade carries a 1.5 ATR stop and a 1 ATR target set from the signal bar's open (re-based on the fill).
Port of FMZ strategy #432789 "双EMA黄金交叉趋势追踪策略Dual-EMA-Golden-Cross-Trend-Tracking-Strategy" (VP Backtester).

FMZ source id: 432789

Source
    https://www.fmz.com/strategy/432789 (PineScript v3, FMZ last modified 2023-11-21 15:10:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 128-223), EMA 21 / 55, ATR 14, stop 1.5 ATR, target 1 ATR; sessions Asia / Europe / US all on, close-out on
    crossover(ema21, ema55) -> entry long, exit(stop = open - 1.5 atr, limit = open + 1 atr);  crossunder -> entry short, mirror
    not can_trade and ses_cls -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_atr / tp_atr x ATR / open of the signal bar, shifted
      one bar inside stops() and re-based on the fill (the source measures from the signal bar's
      open). The fixed-percent stop is off.
    * The three sessions (17:00-03:00, 02:00-12:00 and 08:00-17:00 in the exchange time zone)
      together cover the whole day, so can_trade is always true and the close-out never fires.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA crosses and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the three session windows together cover the whole day, so the session close-out never fires).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432789_ema_21_55_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 3.0],
    "tp_atr": [1.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 55, "atr_len": 14, "sl_atr": 1.5, "tp_atr": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / o
    return le, se, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
