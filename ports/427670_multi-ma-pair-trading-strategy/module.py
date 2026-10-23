"""Two short-term pullback entries, long only, entered only when flat: (1) the close under the SMA 10 and at or under the SMA 3 after a previous close above it, the open above the EMA 5 and a falling SMA 8; or (2) the close under the EMA 3, the open above the bar's OHLC average, volume not above the previous bar's and the close outside the previous body; the trade closes after 10 bars or after its fifth profitable close.
Port of FMZ strategy #427670 "Multi MA Pair Trading Strategy" (Free Strategy #08 (Combo of #01 and #02) (ES / SPY)).

FMZ source id: 427670

Source
    https://www.fmz.com/strategy/427670 (PineScript v3, FMZ last modified 2023-09-23 15:16:50).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 215-261), SMA 3 / 8 / 10, EMA 5 / 3; max profit closes 5; max bars 10; quantity 1
    Entry01 = flat and close < sma(10) and close <= sma(3) and close[1] > sma(3)[1] and open > ema(5) and sma(8) < sma(8)[1];  Entry02 = flat and close < ema(3) and open > ohlc4 and volume <= volume[1] and close outside the previous body
    BarsSinceEntry = flat ? 0 : +1;  MaxProfitCount = flat ? 0 : (close > avg and BarsSinceEntry > 1 ? +1);  BarsSinceEntry - 1 >= 10 or MaxProfitCount >= 5 -> close L1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters run from the bar the position is first held (the fill bar counts 1), as written; the
      profit count compares closes with the fill price from the second held bar. The source has no
      backtest header and no bar-size input (ES / SPY in the title): FREQ = "bar_size_pending"; the bars
      come from the house bar_sizes.build_bars. Long only. The 1-unit quantity is sizing.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-count and profit-count exits.
    2 generic: PASS, short-term pullback entries with time / profit-count exits.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: quantity 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar by the house bar builder) in Entry02's volume <= volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427670_sma_ema_pullback_two_entries_bar_and_profit_count_exit_long"
FAMILY = "pullback"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_bars": [10, 20],
    "max_profit_closes": [5, 3],
}
DEFAULT_PARAMS = {"max_bars": 10, "max_profit_closes": 5}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    s1, s2, s3 = c.rolling(3).mean(), c.rolling(8).mean(), c.rolling(10).mean()
    e1, e2 = c.ewm(span=5, adjust=False).mean(), c.ewm(span=3, adjust=False).mean()
    ohlc4 = (o + h + lo + c) / 4
    en1 = (c < s3) & (c <= s1) & (c.shift(1) > s1.shift(1)) & (o > e1) & (s2 < s2.shift(1))
    body_lo = np.minimum(o.shift(1), c.shift(1))
    body_hi = np.maximum(o.shift(1), c.shift(1))
    en2 = (c < e2) & (o > ohlc4) & (v <= v.shift(1)) & ((c < body_lo) | (c > body_hi))
    ent = (en1 | en2).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    mb, mp = int(p["max_bars"]), int(p["max_profit_closes"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, pend, fill = False, False, np.nan
    bse = mpc = 0
    for i in range(m):
        if pend:                                       # the entry fills at this bar's open
            held, pend = True, False
        if not held:
            bse = mpc = 0
        else:
            bse += 1
            if cv[i] > fill and bse > 1:
                mpc += 1
        if held and (bse - 1 >= mb or mpc >= mp):
            lx[i] = True
            held = False                               # the close fills at the next open
        elif not held and not pend and ent[i] and i + 1 < m and not lx[i]:
            le[i] = True
            pend, fill = True, ov[i + 1]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
