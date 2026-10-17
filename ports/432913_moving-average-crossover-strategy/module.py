"""EMA 26 / 51 crosses with an ATR bracket, 1-minute bars: the EMA 26 crossing above the EMA 51 goes long, crossing below
goes short; each trade carries a 1.5 ATR stop and a 1 ATR target (the source's FX tick factor).
Port of FMZ strategy #432913 "Moving Average Crossover Strategy" (MA cross strategy Vts).

FMZ source id: 432913

Source
    https://www.fmz.com/strategy/432913 (PineScript v3, FMZ last modified 2023-11-22 16:38:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 133-191), EMA 26 / 51, ATR 14, SL 1.5 ATR, TP 1 ATR (x 1e5 ticks; 1e3 for JPY / XAU)
    crossunder(ema51, ema26) -> entry long, exit(loss = 1.5 atr x 1e5, profit = 1 atr x 1e5 ticks);  crossunder(ema26, ema51) -> close long
    crossover(ema51, ema26) -> entry short, same exit;  crossover(ema26, ema51) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick counts are ATR x 1e5, i.e. exactly 1.5 / 1 ATR on a 5-digit FX symbol
      (tick 1e-5, the case the script is written for, with a JPY / XAU switch). Ported as sl_atr /
      tp_atr x Wilder ATR 14 of the signal bar as fractions of its close, shifted one bar inside
      stops() and re-based on the fill. (On the header's BTC_USDT the same ticks would be 15,000 ATR,
      i.e. no bracket.)
    * The closes of one side fall on the other side's entry bar; a close after an entry does not undo
      the reversal: REVERSAL INTENDED. The start year (2016) is dropped; qty 1 is sizing. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, FX tick-scaled ATR distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored; the exits quoted in original_sizing.txt.
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

NAME = "fmz_432913_ema_26_51_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 3.0],
    "tp_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 26, "slow": 51, "atr_len": 14, "sl_atr": 1.5, "tp_atr": 1.0}


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
    le = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
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
