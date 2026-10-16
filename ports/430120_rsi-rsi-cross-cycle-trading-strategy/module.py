"""Smoothed-RSI turns with close-checked exits, 3-minute bars: the SMA 14 of RSI 14 crossing up through 30 goes long,
crossing down through 70 goes short (reversing an open position); a close 5 % beyond the signal close in profit, or 2 %
against it, closes the position.
Port of FMZ strategy #430120 "RSI跨周期交易策略RSI-Cross-Cycle-Trading-Strategy" (RSI KANNEMAN).

FMZ source id: 430120

Source
    https://www.fmz.com/strategy/430120 (PineScript v4, FMZ last modified 2023-10-25 11:20:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-238), RSI 14, SMA 14, levels 70 / 30, SL 2 %, TP 5 %
    mm = sma(rsi(close, 14), 14); buy = crossover(mm, 30); sell = crossunder(mm, 70)
    not long and buy  -> entry long;  SL = close x 0.98, TP = close x 1.05
    long: close >= TP or close <= SL or sell -> close long
    not short and sell -> entry short; SL = close x 1.02, TP = close x 0.95
    short: close <= TP or close >= SL or buy -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SL / TP are tested on bar closes with strategy.close (market exits at the next open): exit
      signals, not stop orders. The levels come from the signal bar's close and are tested from the
      bar after the signal (on the signal bar they cannot be met).
    * A sell signal while long both closes the long and enters a short: the bar reverses (the same for
      a buy while short). The SL / TP variables are shared by both sides in the source; on any bar
      they belong to the position just entered, so the port keeps one pair per position.
    * The date-filter inputs are unused (dateFilter = true). strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, RSI levels and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: equity / hlc3 per entry stored in original_sizing.txt.
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

NAME = "fmz_430120_smoothed_rsi_turn_pct_exits"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl_pct": [2.0, 1.0],
    "tp_pct": [5.0, 2.5],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ma_len": 14, "over_bought": 70, "over_sold": 30, "sl_pct": 2.0, "tp_pct": 5.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mm = _rsi(c, int(p["rsi_len"])).rolling(int(p["ma_len"])).mean()
    buy = ((mm > p["over_sold"]) & (mm.shift(1) <= p["over_sold"])).to_numpy()
    sell = ((mm < p["over_bought"]) & (mm.shift(1) >= p["over_bought"])).to_numpy()
    sl, tp = float(p["sl_pct"]) / 100, float(p["tp_pct"]) / 100
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, lo_lvl, hi_lvl = 0, np.nan, np.nan
    for i in range(m):
        if pos != 1 and buy[i]:
            pos, lo_lvl, hi_lvl = 1, cv[i] * (1 - sl), cv[i] * (1 + tp)
        elif pos != -1 and sell[i]:
            pos, lo_lvl, hi_lvl = -1, cv[i] * (1 - tp), cv[i] * (1 + sl)
        elif pos == 1 and (cv[i] >= hi_lvl or cv[i] <= lo_lvl):
            pos = 0
        elif pos == -1 and (cv[i] <= lo_lvl or cv[i] >= hi_lvl):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
