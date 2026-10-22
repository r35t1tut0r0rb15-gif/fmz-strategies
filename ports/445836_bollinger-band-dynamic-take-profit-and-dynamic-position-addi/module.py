"""Bollinger band (12, 2) extremes with the script's entry flags, 1-hour bars: a close under the lower band goes long when no entry is flagged; a close over the upper band closes the long and goes short; a
close under the lower band closes the short (and a long follows only on a later such bar); the add-on entries never act.
Port of FMZ strategy #445836 "Bollinger Band Dynamic Take Profit and Dynamic Position Adding Strategy" (Bollinger Bands (BB dynamic take-profit and adding)).

FMZ source id: 445836

Source
    https://www.fmz.com/strategy/445836 (PineScript v5, FMZ last modified 2024-03-22 15:49:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 174-231), BB 12 / 2; add factor 0.98; qty initial_capital / 10000 (5)
    close < lower and not entryMade -> entry 롱, entryMade;  ... close > upper -> close 롱 / 추가롱, entryMade = false;  close > upper and not entryMade -> entry s, entryMade
    ... close < lower -> close s / 추가s, entryMade = false;  add-ons (추가롱 / 추가s) need basis / band crossings and close vs avg x 0.98

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy() sets no pyramiding, so a second entry in the same direction never fills: the add-on
      ids never act (while flat their test on the na average price is false). The flags run in the
      script's order on each bar, so a close over the upper band closes a long and opens the short on
      the same bar (one reversal), while a close under the lower band only closes a short (its flag
      was set at the short entry and is cleared after the long test). The upper / lower / basis
      crossing flags only gate the add-ons. REVERSAL INTENDED. The qty 5 is sizing. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band extremes with entry flags.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the qty (initial_capital / 10000) stored.
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

NAME = "fmz_445836_band_extreme_flag_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [12, 20],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 12, "mult": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    with np.errstate(invalid="ignore"):
        below = (c < basis - dev).to_numpy()
        above = (c > basis + dev).to_numpy()
    m = len(below)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, em = 0, False
    for i in range(m):
        new = pos
        if below[i] and not em:
            if new != 1:
                le[i], new = True, 1                # a held short reverses
            em = True
        if above[i]:
            if pos == 1 and new == 1:
                lx[i], new = True, 0
            em = False
        if above[i] and not em:
            if new != -1:
                se[i], lx[i], new = True, False, -1  # a close then the entry is one reversal
            em = True
        if below[i]:
            if pos == -1 and new == -1:
                sx[i], new = True, 0
            em = False
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
