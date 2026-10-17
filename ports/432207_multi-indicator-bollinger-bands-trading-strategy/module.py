"""One-sigma band breakouts with basis exits, 2-hour bars: the close crossing above the SMA 34 + 1 standard deviation goes
long, crossing below the SMA 34 - 1 standard deviation goes short; a close back across the SMA closes the trade, and a
repeated breakout in the trade's own direction closes it too. The RSI / MACD layers are inert as written.
Port of FMZ strategy #432207 "Multi Indicator Bollinger Bands Trading Strategy" (MBB (Bollinger Bands, Madrid)).

FMZ source id: 432207

Source
    https://www.fmz.com/strategy/432207 (PineScript v5, FMZ last modified 2023-11-15 15:30:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 193-278), SMA 34, 1 sd (the 2 sd band is drawn only), RSI 14, MACD 12 / 26 / 9
    crossover(close, basis + sd) -> entry long;  crossunder(close, basis - sd) -> entry short
    long_entry or close < basis -> close("Long");  short_entry or close > basis -> close("Short")
    later: entry("Long") when long_entry and rsi > 70 [and crossover(close, 9)]; close("Long Exit") / close("Short Exit") when ...

Interpretation choices (Pine rules in SURVEY_README.md)
    * The later entries repeat the "Long" / "Short" ids under a stricter condition that implies the
      first one: a same-direction entry adds nothing (pyramiding 0). The closes of "Long Exit" /
      "Short Exit" name ids no entry uses: inert. macdLong / macdShort compare the price with the
      number 9 and feed only those inert lines; ta.macd's result is not used.
    * strategy.close("Long", "Long") passes "Long" as the comment. Its condition includes long_entry:
      a breakout while already long closes the long (the same-side entry is an ignored add), so that
      bar ends flat; an opposite entry reverses and a later close of the other side does not undo it
      (C31-C39 convention): REVERSAL INTENDED.
    * ta.stdev is the population deviation (ddof 0); the window includes the current bar. FREQ = "2h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band and basis crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432207_one_sigma_band_breakout_basis_exit"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20, 50],
}
DEFAULT_PARAMS = {"length": 34}


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
    sd = c.rolling(n).std(ddof=0)
    up1, lo1 = basis + sd, basis - sd
    le = ((c > up1) & (c.shift(1) <= up1.shift(1))).to_numpy()
    se = ((c < lo1) & (c.shift(1) >= lo1.shift(1))).to_numpy()
    xl = le | (c < basis).to_numpy()
    xs = se | (c > basis).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if le[i]:
            pos = 1
        if se[i]:
            pos = -1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    lx = (prev == 1) & (tgt == 0)                      # a reversal is the opposite entry alone
    sx = (prev == -1) & (tgt == 0)
    l_e = (tgt == 1) & (prev != 1)
    s_e = (tgt == -1) & (prev != -1)
    return tuple(pd.Series(a, index=bars_df.index) for a in (l_e, lx, s_e, sx))


def portfolio_kwargs(**params):
    return {}
