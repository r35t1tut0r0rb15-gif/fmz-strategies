"""MACD 12 / 26 / 9 crosses inside each MACD sign regime, 1-hour bars: above zero, the first MACD cross up below the regime's
highest MACD goes long with a 4 % stop; below zero, the first cross down above the regime's lowest goes short with a 4 %
stop; a trade more than 5 % in profit that gives back a fifth of its best profit (on closes) is closed.
Port of FMZ strategy #434983 "MACD趋势跟踪策略MACD-Trend-Following-Strategy" (MACD Cross Strategy).

FMZ source id: 434983

Source
    https://www.fmz.com/strategy/434983 (PineScript v5, FMZ last modified 2023-12-11 14:57:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-209), MACD 12 / 26 / 9; stop 4 % of the signal close; give-back exit after 5 % profit at 80 % of the best profit
    macd > 0: highestMACD = max(highestMACD, macd), short flag reset;  else lowestMACD = min(lowestMACD, macd), long flag reset
    crossover(macd, signal) and macd < highestMACD and macd > 0 and not haveOpenedLong -> entry long, exit(stop = close (1 - 4 %)), entryLongPrice = close
    long: profit = close - entryLongPrice > 0 -> best = max(best, profit); profit / entry > 5 % and best x 0.8 > profit -> close long, best = 0;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop level is fixed from the signal close: sl_stop 0.04 of the fill (re-based). The
      give-back rule is the script's own bookkeeping on closes (the entry price is the signal close,
      the best profit is not reset when the stop closes a trade, as written): a close-based exit
      signal, not a broker trail (no mark). "Position held" follows the house stop on bars.
    * The per-regime flags allow one long per positive MACD regime and one short per negative one.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry; give-back exit on closes.
    2 generic: PASS, MACD crosses, a percent stop and percent profit rules.
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

NAME = "fmz_434983_macd_regime_giveback"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.04, 0.02],
    "min_profit": [0.05, 0.02],
}
DEFAULT_PARAMS = {"sl_pct": 0.04, "min_profit": 0.05, "keep": 0.8}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    xo = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    xu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    mv = macd.to_numpy()
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    s_, mp, kp = float(p["sl_pct"]), float(p["min_profit"]), float(p["keep"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ei = 0, -1
    hi_m = lo_m = 0.0
    hol = hos = False
    elp = esp = np.nan
    blp = bsp = 0.0
    for i in range(m):
        if pos != 0 and i >= ei:                          # the house stop from the fill price
            e0 = ov[ei]
            if (pos == 1 and lv[i] <= e0 * (1 - s_)) or (pos == -1 and hv[i] >= e0 * (1 + s_)):
                pos = 0
        if mv[i] > 0:
            lo_m, hi_m, hos = 0.0, max(hi_m, mv[i]), False
        else:
            hi_m, lo_m, hol = 0.0, min(lo_m, mv[i]), False
        new = pos
        if xo[i] and mv[i] < hi_m and mv[i] > 0 and not hol:
            new, elp, hol = 1, cv[i], True
        if xu[i] and mv[i] > lo_m and mv[i] < 0 and not hos:
            new, esp, hos = -1, cv[i], True
        if pos > 0:
            pr = cv[i] - elp
            if pr > 0:
                blp = max(blp, pr)
                if pr / elp > mp and blp * kp > pr:
                    if new == pos:
                        new = 0
                    blp = 0.0
        if pos < 0:
            pr = esp - cv[i]
            if pr > 0:
                bsp = max(bsp, pr)
                if pr / esp > mp and bsp * kp > pr:
                    if new == pos:
                        new = 0
                    bsp = 0.0
        if new != pos and new != 0:
            ei = i + 1
        le[i], se[i] = new == 1 and pos != 1, new == -1 and pos != -1
        lx[i], sx[i] = pos == 1 and new == 0, pos == -1 and new == 0
        pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
