"""CROSS_ALGO: EMA 13 crossing above EMA 50 goes long, crossing below goes short (each cross closes
the other side and opens the new one).
Port of FMZ strategy #427348 "Crossover Trading Strategy Based on Dual EMA System".

FMZ source id: 427348

Source
    https://www.fmz.com/strategy/427348 (PineScript v4, FMZ last modified 2023-09-20 11:39:40).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 123-153), EMA 13 / 50
    crossover(ema13, ema50) -> entry long and close short; crossunder -> entry short and close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes fire on the same crosses as the opposite entries: one-bar reversals,
      REVERSAL INTENDED.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import pandas as pd

NAME = "fmz_427348_cross_algo_ema_13_50"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [13, 8],
    "long_len": [50, 26, 100],
}
DEFAULT_PARAMS = {"short_len": 13, "long_len": 50}


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
    c = bars_df["close"]
    s = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    lg = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    up = ((s > lg) & (s.shift(1) <= lg.shift(1))).astype(bool)
    dn = ((s < lg) & (s.shift(1) >= lg.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false.copy(), dn, false.copy()


def portfolio_kwargs(**params):
    return {}
