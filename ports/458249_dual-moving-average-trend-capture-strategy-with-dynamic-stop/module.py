"""Close crossings of the SMA 14 on the side of the SMA 50, 1-hour bars, entries only from flat: the close crossing over the SMA 14 above the SMA 50 goes long with a 1 % target and a stop at the previous bar's low, the mirror goes short with the previous bar's high as its stop.
Port of FMZ strategy #458249 "Dual Moving Average Trend Capture Strategy with Dynamic Stop Loss and Filter" (Moving Average Breakout with Filter and Dynamic Stop Loss).

FMZ source id: 458249

Source
    https://www.fmz.com/strategy/458249 (PineScript v5, FMZ last modified 2024-07-31 11:46:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 180-262), SMA 14, filter SMA 50 (types SMA); target 1 % of the signal close; stop low[1] / high[1] (dynamic 1 % stop off)
    crossover(close, ma) and close > filterMa and flat -> tp = close x 1.01, sl = low[1], entry Long + exit(limit = tp, stop = sl)
    crossunder(close, ma) and close < filterMa and flat -> tp = close x 0.99, sl = high[1], entry Short + exit(limit = tp, stop = sl)

Interpretation choices (Pine rules in SURVEY_README.md)
    * inPosition is cleared at the same bar's close whenever the position is flat, so the gate is
      strategy.position_size == 0: entries only from flat. The levels are prices fixed on the signal
      bar: sent as fractions of the fill open (the signal bar's level shifted into the fill bar), and
      followed in the loop so the from-flat entries line up; a level already at or through the fill
      open is marketable and is sent as a bar-close exit on the fill bar (one bar late). Opposite
      entries cannot occur (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, SMA crossings with a filter, previous-bar stop and percent target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458249_close_sma14_cross_sma50_filter_prev_bar_stop_from_flat"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [14, 30],
    "filter_len": [50, 100],
    "tp_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"ma_len": 14, "filter_len": 50, "tp_pct": 0.01}


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
    ma = c.rolling(int(p["ma_len"])).mean()
    fm = c.rolling(int(p["filter_len"])).mean()
    lc = ((c > ma) & (c.shift(1) <= ma.shift(1)) & (c > fm)).to_numpy()
    sc = ((c < ma) & (c.shift(1) >= ma.shift(1)) & (c < fm)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    h1, l1 = h.shift(1).to_numpy(dtype=float), lo.shift(1).to_numpy(dtype=float)
    tp = float(p["tp_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl_a, tp_a, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl_a, tp_a = pend, 0, sl_n, tp_n
            through = (sl_a >= ov[i] or tp_a <= ov[i]) if pos == 1 else (sl_a <= ov[i] or tp_a >= ov[i])
            if through:                          # a level at or through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl_a, tp_a = 2, np.nan, np.nan
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and (lv[i] <= sl_a or hv[i] >= tp_a):
            pos, sl_a, tp_a = 0, np.nan, np.nan  # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl_a or lv[i] <= tp_a):
            pos, sl_a, tp_a = 0, np.nan, np.nan
        if pos == 0 and pend == 0:
            if lc[i]:
                sl_n, tp_n = l1[i], cv[i] * (1 + tp)
                le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
            elif sc[i]:
                sl_n, tp_n = h1[i], cv[i] * (1 - tp)
                se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
    ix = bars_df.index
    out = [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, tp_sent, side)]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = _run(bars_df, p)[:4]
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    tp_f = (tp_l / o - 1).where(sd > 0, 1 - tp_l / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
