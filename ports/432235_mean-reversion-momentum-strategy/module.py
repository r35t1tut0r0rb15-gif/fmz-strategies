"""Regression z-score fades above the SMA 200, 1-hour bars: the close more than one standard deviation below its 10-bar
regression line, under the SMA 10 and above the SMA 200, goes long; more than one above it, over the SMA 10 and above
the SMA 200, goes short; the close back across the SMA 10 closes the trade; a 1 % target and a 1 % stop.
Port of FMZ strategy #432235 "Mean Reversion Momentum Strategy" (GMS: Mean Reversion Strategy).

FMZ source id: 432235

Source
    https://www.fmz.com/strategy/432235 (PineScript v4, FMZ last modified 2023-11-15 17:40:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-274), length 10, thresholds +-1, MA exit 10, trend SMA 200 ("Above"), both sides, PT 1 %, SL 1 %
    x = (close - linreg(close, 10, 0)) / stdev(close, 10)
    x < -1 and close < sma10 and close > sma200 -> entry long;  close > sma10 -> close long
    x > 1 and close > sma10 and close > sma200 -> entry short;  close < sma10 -> close short
    every bar: exit("EXIT", profit = close x 1 % / mintick, loss = close x 1 % / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default branch is active (Both, Above, MA exit); the other branches are input options.
    * The bracket's tick counts are recomputed every bar as 1 % of the current close, so its levels
      move a little with the price after entry: a moving level that stops() cannot express (rule 2,
      mark trailing_stop_pending). The port keeps 1 % of the fill for the trade (house bracket, live
      on the fill bar).
    * The closes act on the position held at the bar's start: a long met by a short signal closes and
      goes short; a short met by a long signal reverses (the later close of the short does not undo
      it): REVERSAL INTENDED. The port's state machine follows the house bracket on bars. ta.stdev is
      the population deviation; linreg as Pine. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (the drift pending).
    2 generic: PASS, a regression z-score, SMA levels and percentage exits of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits quoted in original_sizing.txt.
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

NAME = "fmz_432235_linreg_zscore_fade"
FAMILY = "zscore_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [10, 20],
    "thr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"lookback": 10, "thr": 1.0, "ma_exit": 10, "trend": 200, "pt_pct": 1.0, "sl_pct": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["lookback"])
    x = (c - _linreg(c, n)) / c.rolling(n).std(ddof=0)
    s10 = c.rolling(int(p["ma_exit"])).mean()
    s200 = c.rolling(int(p["trend"])).mean()
    th = float(p["thr"])
    el = ((x < -th) & (c < s10) & (c > s200)).to_numpy()
    xl = (c > s10).to_numpy()
    es = ((x > th) & (c > s10) & (c > s200)).to_numpy()
    xs = (c < s10).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["pt_pct"]) / 100, float(p["sl_pct"]) / 100
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house bracket from the fill price
            ep = ov[e_i]
            if pos == 1 and (lv[i] <= ep * (1 - sl) or hv[i] >= ep * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= ep * (1 + sl) or lv[i] <= ep * (1 - tp)):
                pos = 0
        start = pos
        if el[i]:
            pos = 1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if es[i]:
            pos = -1
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        if pos != 0 and pos != start:
            e_i = i + 1
            ent[i] = pos
        tgt[i] = pos
    return tgt, ent


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tgt, ent = _run(bars_df, p)
    prev = np.concatenate(([0], tgt[:-1]))
    le = ent == 1
    lx = (prev == 1) & (tgt == 0)
    se = ent == -1
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, ent = _run(bars_df, p)
    idx = bars_df.index
    on = pd.Series(ent != 0, index=idx)
    sl = pd.Series(np.where(on, float(p["sl_pct"]) / 100, np.nan), index=idx)
    tp = pd.Series(np.where(on, float(p["pt_pct"]) / 100, np.nan), index=idx)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
