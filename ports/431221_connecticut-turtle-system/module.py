"""Connecticut turtle system, broker days, long only: a close above the previous 55-bar high (system 2), or above the
previous 20-bar high unless the last system-1 trade won (system 1), goes long; a close under a 2-ATR stop from the last
buy close, or under the previous 10-bar low, closes; adds every 1 ATR are not ported, but they move the stop as written.
Port of FMZ strategy #431221 "Connecticut Turtle System" (Turtle).

FMZ source id: 431221

Source
    https://www.fmz.com/strategy/431221 (PineScript v4, FMZ last modified 2023-11-06 10:23:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 157-306), L1 20 / exit 10, L2 55 / exit 20, stop 2 N, pyramid 1 N, ATR 14, pyramiding 5
    not inBuy: close > highest(55)[1] -> L2 entry; else close > highest(20)[1] -> L1 entry unless win; stop = close - 2 N
    inBuy: close > nextBuyPrice and buys < 6 -> add, stop = close - 2 N, next = high + N
           close < stop -> close (win false);  else mode L1 and close > highest(55)[1] and win -> re-enter as L2
           else close < lowest(10)[1] or close < lowest(20)[1] -> close; win = close >= average buy price

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state (inBuy, win, mode, buy count, average price, stop and next-buy levels) is ported
      line for line; after a winning L1 trade the next L1 breakout is skipped but tracked
      (inBuy true without a position), as written, and an add while so tracked opens the position.
    * pyramiding 5: adds are not ported (one net position); each add still resets the stop and the
      next add level. The stops are close-checked exits (strategy.close on the bar close), not stop
      orders. close_all before an entry nets to the long held. Long only; Opposite entries cannot
      occur. N is ta.atr(14) (Wilder). The date filter (2000-9999) is always true.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, Donchian breakouts and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity per entry and pyramiding 5 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431221_connecticut_turtle_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_n": [2.0, 3.0],
    "l1": [20, 40],
}
DEFAULT_PARAMS = {"stop_n": 2.0, "pyramid_n": 1.0, "l1": 20, "l2": 55, "l1_exit": 10, "l2_exit": 20, "atr_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    l1 = h.rolling(int(p["l1"])).max().shift(1).to_numpy()
    l2 = h.rolling(int(p["l2"])).max().shift(1).to_numpy()
    x1 = lo.rolling(int(p["l1_exit"])).min().shift(1).to_numpy()
    x2 = lo.rolling(int(p["l2_exit"])).min().shift(1).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    nn = _rma(tr, int(p["atr_len"]))
    cv, hv = c.to_numpy(dtype=float), h.to_numpy(dtype=float)
    sn, pn = float(p["stop_n"]), float(p["pyramid_n"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, in_buy, win, mode = 0, False, False, "L1"
    buy_p = tot_p = avg_p = stop_p = next_p = 0.0
    buys = 0
    for i in range(m):
        ci, n = cv[i], nn[i]
        if not in_buy:
            if ci > l2[i]:
                mode, pos, win = "L2", 1, False
                buy_p, buys, tot_p, avg_p = ci, 1, ci, ci
                stop_p, next_p, in_buy = ci - sn * n, hv[i] + pn * n, True
            elif ci > l1[i]:
                mode = "L1"
                if not win:
                    pos = 1
                win = False
                buy_p, buys, tot_p, avg_p = ci, 1, ci, ci
                stop_p, next_p, in_buy = ci - sn * n, hv[i] + pn * n, True
            else:
                in_buy = False
        else:
            if ci > next_p and buys < 6:
                pos = 1
                stop_p, next_p = ci - sn * n, hv[i] + pn * n
                buys += 1
                tot_p += buy_p
                avg_p = tot_p / buys
            if ci < stop_p:
                in_buy, pos, win, buy_p, avg_p = False, 0, False, 0.0, 0.0
            elif mode == "L1" and ci > l2[i]:
                if win:
                    in_buy, win, mode, pos = True, False, "L2", 1
                    buy_p, buys, tot_p, avg_p = ci, 1, ci, ci
                    stop_p, next_p = ci - sn * n, ci + pn * n
            elif ci < x1[i] or ci < x2[i]:
                in_buy, pos = False, 0
                win = not (ci < avg_p)
                buy_p = 0.0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
