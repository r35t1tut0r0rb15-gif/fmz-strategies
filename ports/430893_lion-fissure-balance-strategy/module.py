"""Jaws mean reversion (TraderHalai), 1-hour bars, long only: the SMA 2 crossing under 99 % of the SMA 8 goes long; a close
1 % above the entry price, or 7 bars after the last signal, closes the long.
Port of FMZ strategy #430893 "Lion Fissure Balance Strategy" (Jaws Mean Reversion (TraderHalai demo)).

FMZ source id: 430893

Source
    https://www.fmz.com/strategy/430893 (PineScript v5, FMZ last modified 2023-11-02 16:55:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 183-204), SMA 2 / 8, 1 % below, 1 % target, 7-bar time exit
    buy = crossunder(sma(close, 2), 0.99 x sma(close, 8)) -> entry "BUY" long
    openprofit >= position_avg_price x 0.01 -> close "BUY";  barssince(buy) >= 7 -> close "BUY"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out in the corpus copy: orders read as written with the
      default size of 1 contract (as #429505), so openprofit >= 1 % of the average price is a close
      1 % above the entry price (the fill at the open after the signal), checked on bar closes: an
      exit signal, not a limit order.
    * barssince(buy) counts from the last signal bar, also one that came while already long. The
      closes are written after the entry and act on the position held at the bar's start. Long only;
      Opposite entries cannot occur. The commented-out tester code is display-only. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, SMA ratio, percentage target and a bar count.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out 5 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430893_jaws_mean_reversion_long"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "big_len": [8, 20],
    "pct_below": [1.0, 2.0],
}
DEFAULT_PARAMS = {"small_len": 2, "big_len": 8, "pct_below": 1.0, "target_pct": 1.0, "max_bars": 7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    small = c.rolling(int(p["small_len"])).mean()
    buy_ma = (100 - float(p["pct_below"])) / 100 * c.rolling(int(p["big_len"])).mean()
    buy = ((small < buy_ma) & (small.shift(1) >= buy_ma.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tgt_pct, mb = float(p["target_pct"]) / 100, int(p["max_bars"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, entry_i, last_buy = 0, -1, -1
    for i in range(m):
        start = pos
        if buy[i]:
            last_buy = i
            if pos == 0:
                pos, entry_i = 1, i + 1
        if start == 1:
            hit = cv[i] - ov[entry_i] >= ov[entry_i] * tgt_pct
            if hit or (last_buy >= 0 and i - last_buy >= mb):
                pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
