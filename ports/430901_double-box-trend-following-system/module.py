"""Double-box trend system (LonesomeTheBlue), 5-minute bars: a break of the 80-bar box sets the trend; in an up trend a
bar lifting off a fresh 21-bar low goes long (mirror short), with the 80-bar box's other side as the stop; a lower high
off a fresh 21-bar high closes the long, and any trend change closes everything.
Port of FMZ strategy #430901 "Double Box Trend Following System" (Grab Trading System).

FMZ source id: 430901

Source
    https://www.fmz.com/strategy/430901 (PineScript v4, FMZ last modified 2023-11-02 17:19:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 171-199), box 80 / 21
    trend := high > highest(80)[1] ? 1 : low < lowest(80)[1] ? -1 : trend
    entry long when trend == 1 and low[1] == lowest(21)[1] and low > lowest(21) (mirror short)
    long: exit(stop = lowest(80)) every bar; close long when high[1] == highest(21)[1] and high < highest(21)
    position open and change(trend) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(80) / lowest(80) include the current bar (the default source high / low). The stop is
      re-issued every bar at the current 80-bar low (a moving level): rule 2, mark
      trailing_stop_pending; the port fixes it at the signal bar's 80-bar low, as a fraction of its
      close, shifted one bar (the source places it from the bar after the fill).
    * The closes are written after the entries and act on the position held at the bar's start; a
      strategy.close does not undo a reversal; close_all leaves the bar flat. "Flat" follows the
      house stop on bars. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (rule 2).
    2 generic: PASS, rolling boxes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430901_double_box_trend"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "flb": [80, 160],
    "slb": [21, 10],
}
DEFAULT_PARAMS = {"flb": 80, "slb": 21}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    fl, sl = int(p["flb"]), int(p["slb"])
    maj_r, maj_s = h.rolling(fl).max(), lo.rolling(fl).min()
    min_r, min_s = h.rolling(sl).max(), lo.rolling(sl).min()
    buy_pat = ((lo.shift(1) == min_s.shift(1)) & (lo > min_s)).to_numpy()
    sell_pat = ((h.shift(1) == min_r.shift(1)) & (h < min_r)).to_numpy()
    up_brk = (h > maj_r.shift(1)).to_numpy()
    dn_brk = (lo < maj_s.shift(1)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    ms, mr = maj_s.to_numpy(), maj_r.to_numpy()
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr = np.full(m, np.nan)
    pos, entry_i, s_, trend = 0, -1, np.nan, 0
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house stop from the fill price
            e = ov[entry_i]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        prev_trend = trend
        trend = 1 if up_brk[i] else (-1 if dn_brk[i] else trend)
        start = pos
        if trend == 1 and buy_pat[i] and pos != 1:
            pos, entry_i, s_ = 1, i + 1, (cv[i] - ms[i]) / cv[i]
        elif trend == -1 and sell_pat[i] and pos != -1:
            pos, entry_i, s_ = -1, i + 1, (mr[i] - cv[i]) / cv[i]
        if start == 1 and pos == 1 and sell_pat[i]:
            pos = 0
        elif start == -1 and pos == -1 and buy_pat[i]:
            pos = 0
        if start != 0 and trend != prev_trend:
            pos = 0
        if pos != start:
            if pos == 1:
                le[i], sl_arr[i] = True, s_
            elif pos == -1:
                se[i], sl_arr[i] = True, s_
            elif start == 1:
                lx[i] = True
            else:
                sx[i] = True
    return le, lx, se, sx, sl_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _run(bars_df, p)
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_arr = _run(bars_df, p)[4]
    return {"sl_stop": pd.Series(sl_arr, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
