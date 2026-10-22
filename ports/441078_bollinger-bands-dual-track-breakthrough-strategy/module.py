"""Bollinger band touches, 30-minute bars: the close at or under the lower band (20, 2) goes long, at or over the upper band goes short; a long also closes when the close is 1 % under the basis, a
short when the close touches the lower band; reversing.
Port of FMZ strategy #441078 "Bollinger Bands Dual track Breakthrough Strategy" (Bollinger Bands Strategy by Royce Mars).

FMZ source id: 441078

Source
    https://www.fmz.com/strategy/441078 (PineScript v5, FMZ last modified 2024-02-05 14:05:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-163), basis SMA 20 on close; stdev 2; stop loss 1 % under the basis
    buy = close <= lower -> entry Buy;  sell = close >= upper or close < basis (1 - 1 %) -> close Buy;  sell = close >= upper -> entry Sell;  buy -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position, in call order: a held long closes on any bar with the close
      1 % under the basis (often also a buy bar, so a long can close and re-open on alternate bars); a
      flat buy bar opens the long. Pine's stdev is the population deviation. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger touches and the basis test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_441078_bb_touch_basis_stop_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "stop_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "stop_pct": 1.0, "mult": 2.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    buy = (c <= basis - dev).to_numpy()
    sell = (c >= basis + dev).to_numpy()
    sl = (c < basis * (1 - float(p["stop_pct"]) / 100)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if buy[i] and new != 1:
            new = 1
        if (sell[i] or sl[i]) and held == 1 and new == 1:
            new = 0
        if sell[i] and new != -1:
            new = -1
        if buy[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
