"""Closes outside the Bollinger 20 / 2 bands and 25 pips beyond a re-touched swing support (resistance), 4-hour bars, from flat: the low side goes long and the high side goes short, with a stop 15 pips beyond the signal bar's low (high) and no live target.
Port of FMZ strategy #489056 "Multi Layer Bollinger Bands Support Resistance Price Breakout Trading Strategy" (Gold BB Support/Resistance Strategy).

FMZ source id: 489056

Source
    https://www.fmz.com/strategy/489056 (PineScript v6, FMZ last modified 2025-04-01 16:55:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-225), BB 20 / 2; S/R distance 25 pips; SL 15 pips; TP 2 x (avg price, na at the signal); pip = mintick x 10
    support := valuewhen(lowest(low, 5)[1] == low[1], low[1]);  validSupport := valuewhen(low within 0.05 % of support, support)
    flat and close < lower and close <= validSupport - 25 pips -> entry BB Long + exit(stop = low - 15 pips, limit = avg + 2 x 15 pips);  mirror -> entry BB Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are valuewhen chains, followed in a loop. The target is built from
      strategy.position_avg_price, which is na on the flat signal bar where the exit is sent, so only the
      stop is live, as written. The pip distances (mintick x 10) are read as percents at the header coin's
      price (ETH about 3000 with tick 0.01: 25 pips = 0.083 %, 15 pips = 0.05 %; C2 ADAPT, as #458242). Entries
      need a flat position at the bar's close, so a loop follows the stop on each bar's high / low (as
      #449508); the stop is sent as a fraction of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256). Opposite entries cannot occur (entries only from flat). Stop module:
      portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No sizing
      code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar stop as a fraction of the fill.
    2 generic: ADAPT, pip distances read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: margins stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489056_bb20_2_outside_retouched_sr_pip_stop_flat"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sr_pips": [25, 100],
    "stop_pips": [15, 60],
}
DEFAULT_PARAMS = {"sr_pips": 25, "stop_pips": 15, "length": 20, "mult": 2.0, "pip_frac": 3.3333e-05}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upv, lov = (basis + dev).to_numpy(), (basis - dev).to_numpy()
    s_cond = (lo.rolling(5).min().shift(1) == lo.shift(1)).to_numpy()
    r_cond = (h.rolling(5).max().shift(1) == h.shift(1)).to_numpy()
    l1, h1 = lo.shift(1).to_numpy(), h.shift(1).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    pf = float(p["pip_frac"])
    kd, ks = float(p["sr_pips"]) * pf, float(p["stop_pips"]) * pf
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, side = np.full(m, np.nan), np.zeros(m)
    sup = res = vs = vr = np.nan
    pos, pend, sl, sl_n = 0, 0, np.nan, np.nan
    for i in range(m):
        if s_cond[i]:
            sup = l1[i]
        if r_cond[i]:
            res = h1[i]
        if sup * 0.9995 <= lv[i] <= sup * 1.0005:     # na compares false
            vs = sup
        if res * 0.9995 <= hv[i] <= res * 1.0005:
            vr = res
        if pend in (1, -1):
            pos, pend, sl = pend, 0, sl_n
            if (pos == 1 and sl >= ov[i]) or (pos == -1 and sl <= ov[i]):
                if pos == 1:                     # a level through the fill: closed at the next open
                    lx[i] = True
                else:
                    sx[i] = True
                pend = 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and lv[i] <= sl:
            pos = 0                              # the stop fills inside this bar
        elif pos == -1 and pend == 0 and hv[i] >= sl:
            pos = 0
        if pos != 0 or pend != 0:
            continue
        if cv[i] < lov[i] and cv[i] <= vs - cv[i] * kd:
            sl_n = lv[i] - cv[i] * ks
            le[i], pend, sl_sent[i], side[i] = True, 1, sl_n, 1
        elif cv[i] > upv[i] and cv[i] >= vr + cv[i] * kd:
            sl_n = hv[i] + cv[i] * ks
            se[i], pend, sl_sent[i], side[i] = True, -1, sl_n, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, sd = sl_l.shift(1), sd.shift(1)    # the signal bar's level, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
