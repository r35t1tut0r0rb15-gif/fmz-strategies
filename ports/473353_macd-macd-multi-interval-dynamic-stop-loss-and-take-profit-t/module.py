"""MACD 12 / 26 / 9 crossings, 12-hour bars: the cross up goes long, the cross down closes the long and goes short; reversing. The long's 1 % stop and 2 % target are set from strategy.position_avg_price on the signal bar (na from flat, the replaced short's price on a reversal), as written; the short has no exit.
Port of FMZ strategy #473353 "MACD多区间动态止盈止损交易系统-MACD-Multi-Interval-Dynamic-Stop-Loss-and-Take-Profit-Trading-System" (MACD Strategy with Settings).

FMZ source id: 473353

Source
    https://www.fmz.com/strategy/473353 (PineScript v5, FMZ last modified 2024-11-29 15:01:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-156), MACD 12 / 26 / 9; stop 1 %, target 2 % of avg on the signal bar; trail_offset 1.5 (no trail_points)
    crossover(macd, signal) -> sl := avg x 0.99, tp := avg x 1.02, entry Long;  long: exit(stop = sl, limit = tp, trail_offset = 1.5);  crossunder -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are stored on the signal bar from strategy.position_avg_price, which is na from flat
      (no bracket) and the replaced short's fill price on a reversal, as written (as #468309, #473147);
      the exit re-sent while long keeps those stored levels. trail_offset without trail_points sets no
      trail (as #441084). The loop tracks the fill prices and the bracket inside each bar; the levels
      are sent as fractions of the long's fill open (a level at or through it is marketable and closed
      one bar late). Crossings alternate, so no repeat signal re-sets the levels. The short ends only
      at the next long entry. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      12-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "12h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the bracket base, as written.
    2 generic: PASS, MACD crossings with a long bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473353_macd12_26_9_cross_reversal_long_bracket_from_replaced_avg"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.01, 0.02],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"sl_pct": 0.01, "tp_pct": 0.02}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lc = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    sc = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    slp, tpp = float(p["sl_pct"]), float(p["tp_pct"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, avg, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, avg, sl, tp = pend, 0, ov[i], sl_n, tp_n
            if pos == 1 and (sl >= ov[i] or tp <= ov[i]):   # a level through the fill: closed at the next open
                lx[i], pend, sl, tp = True, 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, avg, sl, tp = 0, 0, np.nan, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan     # the bracket fills inside this bar
        if pend == 2:
            continue
        if lc[i] and pos != 1:
            sl_n, tp_n = avg * (1 - slp), avg * (1 + tpp)    # na from flat
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i] and pos != -1:
            sl_n, tp_n = np.nan, np.nan                      # the short has no exit
            se[i], pend, side[i] = True, -1, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, tp_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0)
    tp_f = (tp_l / o - 1).where(sd > 0)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
