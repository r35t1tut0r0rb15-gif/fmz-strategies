"""EMA 40 / 120 trend with the Bollinger basis, 1-minute bars: with the EMA 40 above the EMA 120, a close above the SMA 20 basis goes long; with the EMA 120 above, a close below the basis goes short; the EMA cross
against the position closes it; the per-bar ATR stop is not ported.
Port of FMZ strategy #439273 "Bollinger Bands Based Trend Following Strategy" (Trend Following with Bollinger Bands).

FMZ source id: 439273

Source
    https://www.fmz.com/strategy/439273 (PineScript v5, FMZ last modified 2024-01-18 16:37:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-223), Bollinger 20, mult 2; EMA 40 / 120; ATR (the code uses the Bollinger length 20); risk 0.01; pyramiding 4
    if close > basis and fast > slow: entry long, exit("exit sl", stop = close - 4 atr, trail_offset = that);  if crossunder(fast, slow) and slow > fast: close long
    if close < basis and slow > fast: entry short, exit("exit sl", stop = close + 4 atr);  if crossover(fast, slow) and fast > slow: close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-sent on every bar of the entry condition at that bar's close minus (plus) 4
      ATR(20), so it moves with the price (trail_offset without a trail price or points starts no
      trail): a level the house trail cannot express. Not ported: mark trailing_stop_pending (as #437036);
      the port keeps the entries and the EMA-cross closes. The closes act on the position held at the bar
      close; an opposite entry on a close bar reverses (as #438020). Pyramiding adds and the ATR-based
      quantity are sizing; one position is held. REVERSAL INTENDED. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-bar stop pending.
    2 generic: PASS, EMA trend, Bollinger basis and crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk, capital and ATR quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439273_ema40_120_trend_bb_basis_side"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [40, 20],
    "len2": [120, 60],
}
DEFAULT_PARAMS = {"len1": 40, "len2": 120, "length": 20}


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
    basis = c.rolling(int(p["length"])).mean()
    f = c.ewm(span=int(p["len1"]), adjust=False).mean()
    s = c.ewm(span=int(p["len2"]), adjust=False).mean()
    le = ((c > basis) & (f > s)).to_numpy()
    se = ((c < basis) & (s > f)).to_numpy()
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xu[i]:
            new = 0
        if pos == -1 and xo[i]:
            new = 0
        if le[i] and pos != 1:
            new = 1
        elif se[i] and pos != -1:
            new = -1
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
