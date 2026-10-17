"""Eight-bar shorts after a close crosses under its SMA 45, 5-minute bars, short only: a close crossing below the SMA 45
starts a short that is closed 8 bars after its signal.
Port of FMZ strategy #433949 "Moving Average Line Reverse Crossover Strategy" (Moving Average Reverse Crossover Strategy).

FMZ source id: 433949

Source
    https://www.fmz.com/strategy/433949 (PineScript v5, FMZ last modified 2023-12-01 16:52:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 193-221), SMA 45; hold 8 bars
    not in_short and crossunder(close, ma) and close[1] > ma[1] -> in_short, entry_bar := bar_index
    in_short and bar_index - entry_bar >= 8 -> in_short := false
    (a second entry clause needs close[1] < ma[1] together with a crossunder, which cannot happen)
    in_short -> entry short;  not in_short -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar-count exit is an explicit exit signal (a time exit, not a time stop). The second entry
      clause can never be true (a crossunder needs close[1] at or above the SMA) and is dropped.
    * Short only; Opposite entries cannot occur. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-count exit signal.
    2 generic: PASS, an SMA cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_433949_sma_cross_down_8bar_short"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [45, 90],
    "hold": [8, 16],
}
DEFAULT_PARAMS = {"ma_len": 45, "hold": 8}


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
    ma = c.rolling(int(p["ma_len"])).mean()
    xd = ((c < ma) & (c.shift(1) > ma.shift(1))).to_numpy()
    hold = int(p["hold"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    ins, eb = False, -1
    for i in range(m):
        if not ins and xd[i]:
            ins, eb = True, i
        if ins and i - eb >= hold:
            ins = False
        tgt[i] = -1 if ins else 0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (false, false.copy(), pd.Series((tgt == -1) & (prev == 0), index=ix),
            pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
