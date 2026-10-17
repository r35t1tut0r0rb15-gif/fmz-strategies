"""Alternating Bollinger band entries with a close-checked stop, 5-minute bars: a close crossing up through the lower band
(SMA 20, 2 sd) goes long and a close crossing down through the upper band goes short, strictly alternating; a stop
level 1 % from the entry close, set only when an entry reverses a position, closes the trade on a close beyond it.
Port of FMZ strategy #433013 "The Bollinger Bands Stop Loss Strategy" (Bollinger Bands Strategy (BBS)).

FMZ source id: 433013

Source
    https://www.fmz.com/strategy/433013 (PineScript v5, FMZ last modified 2023-11-23 15:49:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 125-169), BB 20 / 2, stop loss 1 %, nextExpectedIsLong starts true
    crossover(close, lower) and nextExpectedIsLong -> entry long, nextExpectedIsLong := false; if position_size[1] < 0: lastTradePrice := close, stops at +/- 1 %
    crossunder(close, upper) and not nextExpectedIsLong -> entry short, nextExpectedIsLong := true; if position_size[1] > 0: the same
    close < stopLossLow -> close long;  close > stopLossHigh -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries alternate (a long can follow only a short entry, and vice versa), also after a stop.
      The stop levels are refreshed only when an entry reverses a position (position_size[1] on the
      signal bar, i.e. the position held two bars before the fill), so an entry from flat keeps the
      old levels and the very first trade has none: as written.
    * The stop is a close-checked exit signal (strategy.close on close beyond the level), not a broker
      stop. A stop close on the bar of an opposite entry is left to the entry.
    * REVERSAL INTENDED. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked stop.
    2 generic: PASS, band crosses and a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commission setting stored.
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

NAME = "fmz_433013_bb_alternating_close_stop"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "sl_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "sl_pct": 1.0}


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
    up, dn = basis + dev, basis - dev
    buy = ((c > dn) & (c.shift(1) <= dn.shift(1))).to_numpy()
    sell = ((c < up) & (c.shift(1) >= up.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    f = float(p["sl_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    next_long = True
    sll = slh = np.nan
    for i in range(m):
        pos = tgt[i - 1] if i >= 1 else 0          # position held during bar i
        pos1 = tgt[i - 2] if i >= 2 else 0         # position_size[1]
        new = pos
        entered = False
        if buy[i] and next_long:
            new, next_long, entered = 1, False, True
            if pos1 < 0:
                sll, slh = cv[i] * (1 - f), cv[i] * (1 + f)
        if sell[i] and not next_long:
            new, next_long, entered = -1, True, True
            if pos1 > 0:
                sll, slh = cv[i] * (1 - f), cv[i] * (1 + f)
        if not entered:
            if pos == 1 and cv[i] < sll:
                new = 0
            elif pos == -1 and cv[i] > slh:
                new = 0
        tgt[i] = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
