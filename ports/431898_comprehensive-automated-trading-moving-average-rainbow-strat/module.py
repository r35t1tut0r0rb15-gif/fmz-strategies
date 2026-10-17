"""Moving-average rainbow pull-backs (AugustoErni), 1-hour bars, from flat: in an up trend (close over the mean of twelve
EMAs 3-55, EMAs 20 > 25 > 30 > 35) a higher high after the previous bar's low touched the rainbow goes long, with the
stop at the touched EMA and the target 1.6 times that distance; the mirror trades shorts.
Port of FMZ strategy #431898 "Comprehensive Automated Trading Moving Average Rainbow Strategy" (Moving Average Rainbow (Stormer)).

FMZ source id: 431898

Source
    https://www.fmz.com/strategy/431898 (PineScript v5, FMZ last modified 2023-11-13 10:44:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 175-378), EMA 3 / 5 / 8 / 13 / 20 / 25 / 30 / 35 / 40 / 45 / 50 / 55, target factor 1.6, turnover trend on
    touch (up trend) = the next EMA down when low sits between two neighbouring EMAs; prevTouch = touch[1]
    long = close > mean and ema20 > 25 > 30 > 35 and high > high[1] and prevTouch set and no recorded position
    stop = prevTouch (lower low: the current touch, or the mean of prevTouch and the low); target = close + |close - stop| x 1.6
    exit(stop, limit) at entry; turnover trend: EMAs 3-13 falling order and close < mean after a new high -> limit = the highest high

Interpretation choices (Pine rules in SURVEY_README.md)
    * The touch functions keep their last value when the trend is neither (Pine var), as written. The
      stop and target are levels at the signal close; as fractions of the entry fill (the open after
      the signal, known at that open), a level already passed at that open exits at once.
    * The turnover trend re-issues the exit with the limit at the highest high since entry (a moving
      level): rule 2, mark trailing_stop_pending, not emitted. The turnover-signal options are off by
      default. "Flat" follows the house bracket on bars; entries only from flat. Opposite entries
      cannot occur. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; levels fixed at entry (rule 2).
    2 generic: PASS, EMA ribbons and reward ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_431898_ma_rainbow_pullback"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "target_factor": [1.6, 1.0],
    "scale": [1.0, 2.0],
}
DEFAULT_PARAMS = {"target_factor": 1.6, "scale": 1.0}
LENGTHS = (3, 5, 8, 13, 20, 25, 30, 35, 40, 45, 50, 55)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _touch(x, mas, flag, up):
    """maTouchPriceTrend: the EMA under (over) the one the bar's low (high) passed; kept when no trend."""
    m = len(x)
    out = np.full(m, np.nan)
    tp = np.nan
    for i in range(m):
        if flag[i]:
            tp = np.nan
            for j in range(11):
                a, b = mas[j][i], mas[j + 1][i]
                if (up and x[i] <= a and x[i] >= b) or ((not up) and x[i] >= a and x[i] <= b):
                    tp = b
                    break
        out[i] = tp
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sc = float(p["scale"])
    mas = [c.ewm(span=max(1, int(round(L * sc))), adjust=False).mean().to_numpy() for L in LENGTHS]
    mean = np.mean(mas, axis=0)
    hv, lv, cv, ov = (x.to_numpy(dtype=float) for x in (h, lo, c, o))
    m = len(cv)
    a58 = (mas[4] > mas[5]) & (mas[5] > mas[6]) & (mas[6] > mas[7])
    b58 = (mas[4] < mas[5]) & (mas[5] < mas[6]) & (mas[6] < mas[7])
    upt = (cv > mean) & a58
    dnt = (cv < mean) & b58
    cur_u = _touch(lv, mas, upt, True)
    cur_d = _touch(hv, mas, dnt, False)
    prev_u = np.concatenate(([np.nan], cur_u[:-1]))
    prev_d = np.concatenate(([np.nan], cur_d[:-1]))
    h1 = np.concatenate(([np.nan], hv[:-1]))
    l1 = np.concatenate(([np.nan], lv[:-1]))
    lc = upt & (hv > h1) & ~np.isnan(prev_u)
    scn = dnt & (lv < l1) & ~np.isnan(prev_d)
    tf = float(p["target_factor"])
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_lvl, tp_lvl = np.full(m, np.nan), np.full(m, np.nan)
    pos, e_i, sl_, tp_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= e_i:                         # house bracket at the levels
            if pos == 1 and (lv[i] <= sl_ or hv[i] >= tp_ or ov[i] <= sl_ or ov[i] >= tp_):
                pos = 0
            elif pos == -1 and (hv[i] >= sl_ or lv[i] <= tp_ or ov[i] >= sl_ or ov[i] <= tp_):
                pos = 0
        if pos != 0:
            continue
        if lc[i]:
            st = prev_u[i]
            if lv[i] < l1[i]:
                st = (st + lv[i]) / 2 if np.isnan(cur_u[i]) else cur_u[i]
            tg = cv[i] + abs(cv[i] - st) * tf
            if tg > 0 and st > 0:
                le[i], pos, e_i, sl_, tp_ = True, 1, i + 1, st, tg
                sl_lvl[i], tp_lvl[i] = st, tg
        elif scn[i]:
            st = prev_d[i]
            if hv[i] > h1[i]:
                st = (st + hv[i]) / 2 if np.isnan(cur_d[i]) else cur_d[i]
            tg = cv[i] - abs(cv[i] - st) * tf
            if tg > 0 and st > 0:
                se[i], pos, e_i, sl_, tp_ = True, -1, i + 1, st, tg
                sl_lvl[i], tp_lvl[i] = st, tg
    return le, se, sl_lvl, tp_lvl


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sl_lvl, tp_lvl = _run(bars_df, p)
    idx = bars_df.index
    o = bars_df["open"]
    side = pd.Series(np.where(le, 1.0, np.where(se, -1.0, np.nan)), index=idx).shift(1)
    s = pd.Series(sl_lvl, index=idx).shift(1)
    t = pd.Series(tp_lvl, index=idx).shift(1)
    return {"sl_stop": ((o - s) / o * side).clip(lower=1e-9), "tp_stop": ((t - o) / o * side).clip(lower=1e-9)}


def portfolio_kwargs(**params):
    return {}
