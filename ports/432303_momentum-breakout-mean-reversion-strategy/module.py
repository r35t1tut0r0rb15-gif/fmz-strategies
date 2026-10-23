"""From flat, a bar closing under the EMA 3 with its open above the OHLC average, volume not above the previous bar's and the close outside the previous bar's body goes long, hourly bars, long only; the position closes after 10 bars beyond the first, or on the 5th close above the entry price.
Port of FMZ strategy #432303 "Momentum Breakout Mean Reversion Strategy" (Free Strategy #01 (ES / SPY)).

FMZ source id: 432303

Source
    https://www.fmz.com/strategy/432303 (PineScript v3, FMZ last modified 2023-11-16 10:47:41).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-189), quantity 1; EMA 3; max profit closes 5; max bars 10
    Cond00 = position_size == 0;  close < ema(close, 3) and open > ohlc4 and volume <= volume[1] and (close < min(open[1], close[1]) or close > max(open[1], close[1])) -> entry L1
    BarsSinceEntry := Cond00 ? 0 : BarsSinceEntry[1] + 1;  MaxProfitCount += close > position_avg_price and BarsSinceEntry > 1;  BarsSinceEntry - 1 >= 10 or MaxProfitCount >= 5 -> close L1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters run as written: the fill bar is bar 1 of the position, closes above the average price
      count from bar 2, and the close goes out on the bar where BarsSinceEntry reaches 11 or the count
      reaches 5 (they need not be consecutive). The average price is the entry fill (the next bar's open).
      On the bar the close fills the position is flat again, so a new entry may be signalled there. volume
      <= volume[1] compares the bar with the previous one only. Long only. qty = 1 is sizing. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pullback entries with time and profit-count exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 1 unit, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in Cond03 = volume <= volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432303_ema3_pullback_volume_drop_time_profit_count_exit_long"
FAMILY = "pullback_time_exit"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_bars": [10, 20],
    "max_profit_closes": [5, 3],
}
DEFAULT_PARAMS = {"ema_len": 3, "max_bars": 10, "max_profit_closes": 5}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    ohlc = (o + h + lo + c) / 4.0
    po, pc = o.shift(1), c.shift(1)
    body_lo = pd.concat([po, pc], axis=1).min(axis=1, skipna=False)
    body_hi = pd.concat([po, pc], axis=1).max(axis=1, skipna=False)
    ent = ((c < ema) & (o > ohlc) & (v <= v.shift(1)) & ((c < body_lo) | (c > body_hi))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    mb, mp = int(p["max_bars"]), int(p["max_profit_closes"])
    m = len(ent)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, bs, cnt, avg = 0, 0, 0, np.nan
    for i in range(m):
        if pos == 1:
            bs += 1
            if bs == 1:
                avg = ov[i]                              # the entry fills at this bar's open
            if cv[i] > avg and bs > 1:
                cnt += 1
            if bs - 1 >= mb or cnt >= mp:
                lx[i], pos = True, 0
        elif pos == 0 and ent[i] and i + 1 < m:
            le[i], pos, bs, cnt = True, 1, 0, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
