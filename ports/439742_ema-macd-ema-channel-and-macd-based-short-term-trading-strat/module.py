"""Close side of the EMA 21 with EMA 5 / 21 MACD crossings, 1-hour bars: a close above the EMA 21 (or an EMA 5 cross up with a positive MACD 18 / 34 / 12 histogram) holds a long, a close below it (or the mirror
cross) holds a short; reversing; the tiny bracket re-sent every bar is not ported.
Port of FMZ strategy #439742 "基于EMA通道和MACD的短线交易策略EMA-Channel-and-MACD-Based-Short-term-Trading-Strategy" (Scalping with EMA channel and MACD).

FMZ source id: 439742

Source
    https://www.fmz.com/strategy/439742 (PineScript v5, FMZ last modified 2024-01-23 14:30:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-143), EMA 5 / 21; MACD 18 / 34 / 12; stop 8, target 15 (price units)
    buy = crossover(ema5, ema21) and hist > 0;  reBuy = close > ema21;  sell / reSell mirror;  each true condition: entry (Buy / Re-Enter Buy / Sell / Re-Enter Sell) and exit(stop = close -/+ 8, limit = close +/- 15)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The re-entry tests hold on every bar of their side, so the bracket (8 / 15 price units from that
      bar's close, all four exits under one id) is re-sent every bar and moves with the price: not
      ported, mark trailing_stop_pending (as #437036); the port keeps the entries. The long entries come
      before the short ones, so a bar meeting both ends short (as #437773). One position is held
      (pyramiding 1). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-bar bracket pending.
    2 generic: PASS, EMA side, EMA crossings and the MACD histogram.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_439742_ema21_side_macd_scalp_entries"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [21, 50],
    "fast": [5, 9],
}
DEFAULT_PARAMS = {"slow": 21, "fast": 5, "macd_fast": 18, "macd_slow": 34, "macd_signal": 12}


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
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    buy = (((ef > es) & (ef.shift(1) <= es.shift(1)) & (hist > 0)) | (c > es)).to_numpy()
    sell = (((ef < es) & (ef.shift(1) >= es.shift(1)) & (hist < 0)) | (c < es)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if sell[i]:
            pos = -1
        elif buy[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
