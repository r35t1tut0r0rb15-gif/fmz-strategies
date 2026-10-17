"""EMA 10 / 20 crosses with a tick bracket, 2-hour bars: the EMA 10 crossing above the EMA 20 goes long, crossing below goes
short; the source's 600-tick target and 200-tick stop become ATR fractions.
Port of FMZ strategy #431400 "海龟突破EMA交叉策略Turtle-Breakout-EMA-Cross-Strategy" (XXXquang).

FMZ source id: 431400

Source
    https://www.fmz.com/strategy/431400 (PineScript v5, FMZ last modified 2023-11-07 15:40:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-180), EMA 10 / 20, lot 1, TP 600 / SL 200 (ticks / pointvalue)
    crossover(ema10, ema20) -> (close_all on the first cross only) entry long, exit(profit 600, loss 200 ticks)
    crossunder(ema10, ema20) -> entry short, same exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: profit = 600 / pointvalue and loss = 200 / pointvalue ticks (60 / 20 USD on BTC_USDT,
      pointvalue 1, mintick 0.1); they become tp_atr / sl_atr x the Wilder ATR 14 of the signal bar,
      as fractions of its close (about 0.15 and 0.05 ATR on 2-hour BTC), fixed at entry.
    * lastCrossTime := timenow makes the close_all fire on the first cross only; the entry reverses
      anyway, so it changes nothing. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick target / stop -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot size 1 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431400_ema_10_20_tick_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.05, 1.0],
    "tp_atr": [0.15, 3.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20, "atr_len": 14, "sl_atr": 0.05, "tp_atr": 0.15}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    lg = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    sh = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return lg, sh, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
