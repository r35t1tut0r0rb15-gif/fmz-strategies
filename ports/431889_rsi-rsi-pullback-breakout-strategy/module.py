"""RSI 5 pull-back breakouts, 45-minute bars, long only: RSI 5 jumping from under 50 on the previous bar to over 60 goes
long; the first RSI fall closes the long.
Port of FMZ strategy #431889 "RSI回调突破策略RSI-Pullback-Breakout-Strategy" (*RSI 5 - Long only- Daily charts & above*).

FMZ source id: 431889

Source
    https://www.fmz.com/strategy/431889 (PineScript v5, FMZ last modified 2023-11-13 10:15:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 167-194), RSI 5, 50 / 60
    rsi[1] < 50 and rsi > 60 -> entry long;  rsi < rsi[1] -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close of "LongExit" names no entry (no effect). Entry and exit cannot meet on one bar (a
      jump above 60 from under 50 is a rise). Long only; Opposite entries cannot occur. FREQ = "45min"
      from the backtest header (the title's daily charts are not the header's).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG431889 (2 members, best partner #439598, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431889_rsi5_jump_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [5, 10],
    "jump_to": [60, 55],
}
DEFAULT_PARAMS = {"rsi_len": 5, "jump_to": 60}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    entry = ((r.shift(1) < 50) & (r > p["jump_to"])).astype(bool)
    out = (r < r.shift(1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return entry, out, false, false.copy()


def portfolio_kwargs(**params):
    return {}
