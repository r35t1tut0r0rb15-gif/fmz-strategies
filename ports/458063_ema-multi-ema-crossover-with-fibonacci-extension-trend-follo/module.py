"""Four EMA 5 / 10 / 30 set-ups, 3-hour bars, long only: a dip to the EMA 30 in a strong uptrend, an EMA 5 cross back over the EMA 30, closes over two highs under the EMA 5 in a downtrend, or an EMA 10 cross over the EMA 30 buy when no set-up is active; each set-up has its own close-based stop, and a close above the stacked EMAs or at Fibonacci extensions of the 20-bar range from the entry low takes profit.
Port of FMZ strategy #458063 "多重EMA交叉结合斐波那契扩展的趋势跟踪策略-Multi-EMA-Crossover-with-Fibonacci-Extension-Trend-Following-Strategy" (EMA Combined Strategy with Specific Stop Loss).

FMZ source id: 458063

Source
    https://www.fmz.com/strategy/458063 (PineScript v5, FMZ last modified 2024-07-29 16:42:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 183-354), EMA 5 / 10 / 30; lowest(low, 3) stops; 20-bar swing range; extensions 0.618 / 0.786 / 1.618 (the '1' level is overwritten by 1.618; the 1.618 level is never set)
    no set-up active: cond1 / cond2 / cond3 / cond4 -> entry Long, flag the set-up, stop low = lowest(low, 3), fib levels = low + range x 0.618 / 0.786 / 1.618
    entry active: set-up 1 and crossover(ema30, ema10) -> close;  set-ups 2-4 and close < their stop low -> close
    low[1] > ema5[1] and low > ema5 and ema5 > ema10 > ema30 -> close;  high >= fib and close <= / < fib -> close (each level)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The set-up flags, stop lows and extension levels are followed bar by bar as written, beside the
      actual position: the management runs on the entry's own bar too, where a close finds no trade
      yet but clears the flags (the order still fills and the trade waits for a later set-up to be
      managed again). All exits are bar-close tests filled at the next open. fib_extension_level_1 is
      assigned twice (the 1.618 value wins) and fib_extension_level_1_618 stays na, so its test never
      holds, as written. Long only. No sizing code. FREQ = "3h" from the backtest header (UTC-aligned
      3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stops and targets are close tests.
    2 generic: PASS, EMA set-ups with set-up stops and Fibonacci targets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458063_ema5_10_30_setups_fib_extension_exits_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "swing_len": [20, 50],
}
DEFAULT_PARAMS = {"swing_len": 20}


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


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e30, e10, e5 = (c.ewm(span=n, adjust=False).mean() for n in (30, 10, 5))
    x30_5 = _xover(e30, e5)
    c1 = (lo <= e30) & (c > e30) & (e10 > e5) & (e30 * 1.01 < e5)
    prior = pd.Series(False, index=c.index)
    for k in range(1, 7):
        prior = prior | x30_5.shift(k, fill_value=False)
    c2 = _xover(e5, e30) & prior
    c3 = (h.shift(2) < e5.shift(2)) & (h.shift(1) < e5.shift(1)) & (e5 < e10) & (e10 < e30) & (h.shift(1) < c)
    x5_30, x10_30 = _xover(e5, e30), _xover(e10, e30)
    c4 = x10_30 & (x5_30 | x5_30.shift(1, fill_value=False) | x10_30.shift(2, fill_value=False)
                   | x10_30.shift(3, fill_value=False)) & (e10.shift(1) < e10) & (e5.shift(1) < e5)
    stop1 = _xover(e30, e10).to_numpy()
    profit = ((lo.shift(1) > e5.shift(1)) & (lo > e5) & (e5 > e10) & (e10 > e30)).to_numpy()
    n = int(p["swing_len"])
    rng = (h.rolling(n).max() - lo.rolling(n).min()).to_numpy()
    ll3 = lo.rolling(3).min().to_numpy()
    conds = [x.to_numpy() for x in (c1, c2, c3, c4)]
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    flags = [False, False, False, False]
    lows = [np.nan] * 4
    has_entry = False
    f618 = f786 = f1 = np.nan
    for i in range(m):
        cur = pos
        for k in range(4):
            if conds[k][i] and not any(flags):
                if cur != 1:
                    cur = 1
                lows[k] = ll3[i]
                f618, f786, f1 = lv[i] + rng[i] * 0.618, lv[i] + rng[i] * 0.786, lv[i] + rng[i] * 1.618
                has_entry = True
                flags[k] = True
        if has_entry:
            hit = False
            if flags[0] and stop1[i]:
                hit, flags[0] = True, False
            for k in (1, 2, 3):
                if flags[k] and cv[i] < lows[k]:
                    hit, flags[k] = True, False
            if profit[i] or (hv[i] >= f618 and cv[i] <= f618) or (hv[i] >= f786 and cv[i] < f786) \
                    or (hv[i] >= f1 and cv[i] < f1):
                hit, flags = True, [False, False, False, False]
            if hit:
                has_entry = False
                if pos == 1:
                    cur = 0                      # the close acts only on a long held into the bar
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        pos = cur
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
