"""SMA 14 / 28 golden crosses with a stepped stop, 3-minute bars, long only: the SMA 14 crossing above the SMA 28 goes long
with a 100-tick stop and a 300-tick target; after 100 ticks of profit the stop moves to the entry and after 200 ticks to
100 ticks of profit. The tick distances become ATR multiples.
Port of FMZ strategy #433572 "Stepped Trailing Stop with Partial Profit Taking Strategy" (Stepped trailing strategy example).

FMZ source id: 433572

Source
    https://www.fmz.com/strategy/433572 (PineScript v4, FMZ last modified 2023-11-28 16:05:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 144-201), SMA 14 / 28; sl 100, tp1 100, tp2 200, tp3 300 ticks
    crossover(sma14, sma28) -> entry long
    stage 1: exit(loss = 100, profit = 300);  stage 2 (high - avg >= 100 ticks): stop = avg;  stage 3 (>= 200 ticks): stop = avg + 100 ticks

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the ticks are price units (10 / 30 USD on the header's BTC_USDT, mintick 0.1, about
      0.4 / 1.2 ATR of 3-minute BTC, ATR about 25 USD). The stop and target become sl_atr / tp_atr x
      Wilder ATR 14 of the signal bar as fractions of its close (shifted one bar, re-based on the fill).
    * The two-step stop ladder (break-even after 100 ticks, +100 ticks after 200) moves the stop in
      ATR-scaled steps, which stops() cannot express (lock_in takes one fixed gain): mark
      trailing_stop_pending. The port keeps the stage-1 stop and the 300-tick target.
    * There is no exit signal; a new golden cross while long is ignored (pyramiding 1). Long only;
      Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). FREQ = "3min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (the stop ladder pending).
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick ladder quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_433572_golden_cross_stepped_stop"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.4, 1.0],
    "tp_atr": [1.2, 3.0],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28, "atr_len": 14, "sl_atr": 0.4, "tp_atr": 1.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _af(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _af(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
