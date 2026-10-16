"""Two EMA pairs, hourly bars: EMA 82 crossing above EMA 95 goes long, EMA 59 crossing below EMA 96
goes short; each trade has a take-profit and a stop in ticks.
Port of FMZ strategy #428692 "Dual Moving Average Breakout Strategy" (OptimizedSisy4x).

FMZ source id: 428692

Source
    https://www.fmz.com/strategy/428692 (PineScript v2, FMZ last modified 2023-10-08 13:59:27).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 144-173), EMAs 59 / 82 / 96 / 95, TP 6250 / SL 3500 ticks
    crossover(ema82, ema95) -> entry long; crossunder(ema59, ema96) -> entry short
    exit(qty_percent 100, profit = 6250, loss = 3500) ticks per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * qty_percent 100 is a full exit. Criterion 2: the tick distances become tp_atr / sl_atr x Wilder
      ATR(14) of the signal bar (as fractions of its close, shifted one bar inside stops(), re-based
      on the fill). 625 / 350 USD on hourly BTC with a 0.1 tick is about 3 / 1.75 ATR (judgement
      before any backtest).
    * The cash quantity is sizing. Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash quantity stored; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_428692_two_ema_pairs_tick_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [3.0, 6.0],
    "sl_atr": [1.75, 3.5],
}
DEFAULT_PARAMS = {"fast": 59, "fast_l": 82, "slow": 96, "slow_l": 95, "tp_atr": 3.0, "sl_atr": 1.75, "atr_length": 14}


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
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    fl, sl_, f, s = e(p["fast_l"]), e(p["slow_l"]), e(p["fast"]), e(p["slow"])
    long_e = ((fl > sl_) & (fl.shift(1) <= sl_.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    pc = bars_df["close"].shift(1)
    tr = pd.concat([bars_df["high"] - bars_df["low"], (bars_df["high"] - pc).abs(),
                    (bars_df["low"] - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
