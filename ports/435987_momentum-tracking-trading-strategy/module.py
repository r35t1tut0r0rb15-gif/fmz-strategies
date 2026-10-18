"""Candle-colour trades with a bracket, 30-minute bars: every green candle goes long and every red candle goes short (reversing), each with a 100-tick
target and stop re-expressed as ATR multiples. The anchor-hour inputs are not used by the orders; "Inverse" trades the opposite colour.
Port of FMZ strategy #435987 "Momentum Tracking Trading Strategy" (Mechanical).

FMZ source id: 435987

Source
    https://www.fmz.com/strategy/435987 (PineScript v5, FMZ last modified 2023-12-20 16:06:26).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 231-340), anchor hour 11 (shifted by 4 or 5 hours); TP and SL 10 pips = 100 ticks; direction Forward
    isTradeTime = true and isStratTime = true (the hour tests are never applied);  Forward: longCondition = close > open, shortCondition = close < open;  entry long / short with exit(profit = 100 ticks, loss = 100 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The anchor hour only feeds the unused background range: the candle test runs on every bar.
      Criterion 2: the 100-tick bracket (10 pips) is re-expressed as tp_stop = sl_stop = k_atr x ATR /
      close of the signal bar, shifted one bar inside stops() (re-based on the fill); 0.1 is the reading
      (10 USD on BTC against a 30-minute ATR near 100), 1.0 a volatility-sized bracket. The direction input is in
      the grid. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 30-minute bars: not coarse. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: REVIEW, clock inputs unused; tick bracket -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick-bracket inputs quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the anchor-hour and time-zone offset inputs only draw a background).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435987_candle_colour_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "direction": ["Forward", "Inverse"],
    "k_atr": [0.1, 1.0],
}
DEFAULT_PARAMS = {"direction": "Forward", "k_atr": 0.1, "atr_len": 14}


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
    o, c = bars_df["open"], bars_df["close"]
    green, red = (c > o), (c < o)
    le, se = (green, red) if p["direction"] == "Forward" else (red, green)
    false = pd.Series(False, index=bars_df.index)
    return le.astype(bool), false, se.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f.copy()}


def portfolio_kwargs(**params):
    return {}
