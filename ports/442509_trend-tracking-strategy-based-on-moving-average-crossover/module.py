"""Six SMA crossings named as chart patterns, 1-hour bars: SMA 50 over 200, 10 over 30 and 20 over 50 enter longs under their own ids, SMA 10 under 20 enters a short; SMA 50 under 200 closes only the
first long id and SMA 30 under 60 closes only the short; reversing.
Port of FMZ strategy #442509 "Trend Tracking Strategy Based on Moving Average Crossover" (Grafik Formasyonlari Alim-Satim Stratejisi).

FMZ source id: 442509

Source
    https://www.fmz.com/strategy/442509 (PineScript v5, FMZ last modified 2024-02-22 14:02:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-160), no inputs; default pyramiding
    crossover(sma50, sma200) -> entry IHS_Long;  crossunder(sma50, sma200) -> close IHS_Long;  crossover(sma10, sma30) -> entry Flag_Long;  crossover(sma20, sma50) -> entry Triangle_Long
    crossunder(sma10, sma20) -> entry Pennant_Short;  crossunder(sma30, sma60) -> close Pennant_Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported in call order with one position at a time (default pyramiding): an entry in the held
      direction under another id does nothing, each close names its own id and acts only on the held
      position (as #442342), so the Flag and Triangle longs end only on the short entry's reversal. The
      pattern names are the author's; every condition is an SMA crossing. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
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

NAME = "fmz_442509_six_sma_cross_named_ids_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [200, 100],
    "short_slow": [20, 40],
}
DEFAULT_PARAMS = {"slow": 200, "short_slow": 20}


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
    sm = {n: c.rolling(n).mean() for n in {10, 20, 30, 50, 60, int(p["slow"]), int(p["short_slow"])}}

    def over(a, b):
        return ((sm[a] > sm[b]) & (sm[a].shift(1) <= sm[b].shift(1))).to_numpy()

    def under(a, b):
        return ((sm[a] < sm[b]) & (sm[a].shift(1) >= sm[b].shift(1))).to_numpy()

    sl, ss = int(p["slow"]), int(p["short_slow"])
    ihs, hs = over(50, sl), under(50, sl)
    flag, tri = over(10, 30), over(20, 50)
    pen, inv = under(10, ss), under(30, 60)
    side = {None: 0, "IHS": 1, "Flag": 1, "Tri": 1, "Pen": -1}
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = None
    for i in range(m):
        new = held
        if ihs[i] and side[new] != 1:
            new = "IHS"
        if hs[i] and held == "IHS" and new == "IHS":
            new = None
        if flag[i] and side[new] != 1:
            new = "Flag"
        if tri[i] and side[new] != 1:
            new = "Tri"
        if pen[i] and side[new] != -1:
            new = "Pen"
        if inv[i] and held == "Pen" and new == "Pen":
            new = None
        tgt[i] = side[new]
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
