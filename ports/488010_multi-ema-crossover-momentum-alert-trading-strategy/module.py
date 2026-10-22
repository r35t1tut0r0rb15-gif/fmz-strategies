"""EMA 10 / 20 side with the close beyond the EMA 50 and a rising (falling) EMA 5 above (below) the EMA 10, 3-hour bars, from flat after a 2-bar cooldown: the up state goes long, the down state goes short; a close back through the EMA 15, or a sudden narrowing of the EMA 5 / 10 gap, closes.
Port of FMZ strategy #488010 "Multi EMA Crossover Momentum Alert Trading Strategy" (GRIM309 CallPut Strategy).

FMZ source id: 488010

Source
    https://www.fmz.com/strategy/488010 (PineScript v6, FMZ last modified 2025-03-24 13:49:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-275), EMA 5 / 10 / 15 / 20 / 50 (200 plotted); cooldown 2 bars; warning 2.5 x the mean change; capital 500, commission 0.1 %
    state 0 and cooldown done and ema10 > ema20 and close > ema50 and ema5 rising above ema10 -> entry Long, state 1;  mirror -> entry Short, state -1
    state 1 and close <= ema15 -> close Long, state 0, cooldown 0;  state -1 and close >= ema15 -> close Short
    warning: state != 0 and |gap - gap[1]| > 2.5 x mean |change| of the 4 earlier gaps and gap < gap[1] -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The position state, the cooldown counter and the warning close are followed in a loop, as written
      (the counter starts at 0 on a close and is incremented on the same bar, so a new entry needs two
      further bars). The gap is |EMA 5 - EMA 10| / EMA 10 in percent. Entries only from state 0: Opposite
      entries cannot occur. No other sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend states with an EMA exit and a momentum warning close.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: strategy(): capital 500, commission 0.1 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488010_ema10_20_50_trend_ema5_momentum_ema15_exit_cooldown_flat"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len15": [15, 20],
    "cooldownBars": [2, 5],
}
DEFAULT_PARAMS = {"len15": 15, "cooldownBars": 2, "len5": 5, "len10": 10, "len20": 20, "len50": 50,
                  "warn_mult": 2.5}


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

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    e5, e10, e15, e20, e50 = (ema(p[k]) for k in ("len5", "len10", "len15", "len20", "len50"))
    up = ((e10 > e20) & (c > e50) & (e5 > e5.shift(1)) & (e5 > e10)).to_numpy()
    dn = ((e10 < e20) & (c < e50) & (e5 < e5.shift(1)) & (e5 < e10)).to_numpy()
    gap = ((e5 - e10) / e10 * 100).abs()
    g = [gap.shift(k).to_numpy() for k in range(6)]
    avg = (np.abs(g[1] - g[2]) + np.abs(g[2] - g[3]) + np.abs(g[3] - g[4]) + np.abs(g[4] - g[5])) / 4
    with np.errstate(invalid="ignore"):
        jump = (np.abs(g[0] - g[1]) > float(p["warn_mult"]) * avg) & (g[0] < g[1])
    cv, c15 = c.to_numpy(dtype=float), e15.to_numpy()
    cd = int(p["cooldownBars"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    state = 0
    bsc = np.nan
    for i in range(m):
        ready = np.isnan(bsc) or bsc >= cd
        oc = up[i] and state == 0 and ready
        cc = state == 1 and cv[i] <= c15[i]
        op = dn[i] and state == 0 and ready
        cp = state == -1 and cv[i] >= c15[i]
        if state != 0 and jump[i]:
            cc = cc or state == 1
            cp = cp or state == -1
        if oc:
            le[i], state, bsc = True, 1, np.nan
        if cc:
            lx[i], state, bsc = True, 0, 0.0
        if op:
            se[i], state, bsc = True, -1, np.nan
        if cp:
            sx[i], state, bsc = True, 0, 0.0
        if not np.isnan(bsc):
            bsc += 1
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx), S(se), S(sx)


def portfolio_kwargs(**params):
    return {}
