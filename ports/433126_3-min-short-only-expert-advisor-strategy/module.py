"""Triple red candle shorts above a T3 average, 10-minute bars, short only: after three red candles with each low lower and
the last close under the previous one (the source's exact pattern), with the close above the T3 (150, b 0.7) average, a
short opens with a 4-tick target and a 16-tick stop, which become ATR multiples.
Port of FMZ strategy #433126 "3 Min Short Only Expert Advisor Strategy" (ES 3m Short Only (Triple RED)).

FMZ source id: 433126

Source
    https://www.fmz.com/strategy/433126 (PineScript v5, FMZ last modified 2023-11-24 15:58:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 116-156), T3 150, b 0.7; take profit 4 ticks, stop 16 ticks (ES tick 0.25)
    pattern = red[2] and red[1] and red and close[1] <= high and close[1] > close and low[1] > low and high[2] > high[1] and low[2] <= low[1]
    sellSignal3 = close > T3(close, 150, 0.7);  pattern and sellSignal3 -> entry short, exit(profit = 4, loss = 16)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the short needs the close ABOVE the T3 (the variable is named sellSignal3).
    * Criterion 2: the bracket is in ticks of the symbol. The script is written for ES (tick 0.25:
      1 / 4 points, about 0.4 / 1.6 ATR of 3-minute ES); on the header's BTC_USDT (mintick 0.1) the
      same ticks would be 0.4 / 1.6 USD, inside the spread. The port uses tp_atr x Wilder ATR 14 of
      the signal bar and a stop of 4 x that (the source's 16 / 4), as fractions of its close, shifted
      one bar inside stops() and re-based on the fill.
    * A new pattern while short is ignored (pyramiding 1). Short only; Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). The title's 3-minute chart is not the header's
      period: FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR fractions (ES reading).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the account / ticker / quantity alert fields stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433126_triple_red_short_t3"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.4, 1.0],
    "t3_len": [150, 300],
}
DEFAULT_PARAMS = {"tp_atr": 0.4, "sl_mult": 4.0, "t3_len": 150, "b": 0.7, "atr_len": 14}


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
    n = int(p["t3_len"])
    e = [c.ewm(span=n, adjust=False).mean()]
    for _ in range(5):
        e.append(e[-1].ewm(span=n, adjust=False).mean())
    b = float(p["b"])
    t3 = (-b ** 3) * e[5] + (3 * b * b + 3 * b ** 3) * e[4] + (-6 * b * b - 3 * b - 3 * b ** 3) * e[3] \
        + (1 + 3 * b + b ** 3 + 3 * b * b) * e[2]
    red = c < o
    pat = (red.shift(2, fill_value=False) & red.shift(1, fill_value=False) & red & (c.shift(1) <= h)
           & (c.shift(1) > c) & (lo.shift(1) > lo) & (h.shift(2) > h.shift(1)) & (lo.shift(2) <= lo.shift(1)))
    se = (pat & (c > t3)).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return se, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, af = _signals(bars_df, p)
    tp = af * float(p["tp_atr"])
    return {"sl_stop": (tp * float(p["sl_mult"])).shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
