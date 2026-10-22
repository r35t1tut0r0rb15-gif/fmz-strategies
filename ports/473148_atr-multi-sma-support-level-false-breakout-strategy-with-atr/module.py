"""False breaks of the floor-pivot support in an SMA 50 / 200 uptrend, daily bars, long only: after a bar whose low broke the support derived from the bar before, a close back over the support buys, with a stop 1 ATR under the signal bar's low and a target at the 10-bar high.
Port of FMZ strategy #473148 "多重均线支撑位假突破策略结合ATR止损系统-Multi-SMA-Support-Level-False-Breakout-Strategy-with-ATR-Stop-Loss-System" (False Break Trading Strategy).

FMZ source id: 473148

Source
    https://www.fmz.com/strategy/473148 (PineScript v5, FMZ last modified 2024-11-27 16:17:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-147), SMA 50 / 200; pivot = hlc3[1], support = 2 x pivot - high[1]; ATR 14; target = highest(high, 10) (current bar included)
    sma50 > sma200 and low[1] < support and close > support -> stop = low - atr, target = highest(high, 10), entry Long + exit(stop, limit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The support is computed from the previous bar, as written, and the test compares the previous low
      with it. The levels are prices fixed on the signal bar, sent as fractions of the fill open (the
      signal bar's levels shifted into the fill bar; a level at or through the fill open is closed one
      bar late), and followed in the loop. A new signal while held re-sends both from the new bar, which
      stops() cannot express: the opening levels are kept (as #434428, mark trailing_stop_pending). Long
      only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, false breaks of a pivot support in an uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473148_pivot_support_false_break_atr_stop_swing_target_long"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [10, 20],
    "atr_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"lookback": 10, "atr_mult": 1.0, "atr_len": 14}


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
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    up = c.rolling(50).mean() > c.rolling(200).mean()
    pivot = (h.shift(1) + lo.shift(1) + c.shift(1)) / 3
    support = 2 * pivot - h.shift(1)
    sig = (up & (lo.shift(1) < support) & (c > support)).to_numpy()
    sl_l = (lo - float(p["atr_mult"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    tp_l = h.rolling(int(p["lookback"])).max().to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent = np.full(m, np.nan), np.full(m, np.nan)
    pos, pend, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos, pend, sl, tp = 1, 0, sl_n, tp_n
            if sl >= ov[i] or tp <= ov[i]:
                lx[i], pend, sl, tp = True, 2, np.nan, np.nan   # a level through the fill: closed at the next open
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, sl, tp = 0, np.nan, np.nan      # the bracket fills inside this bar
        if sig[i] and pos == 0 and pend == 0:
            sl_n, tp_n = sl_l[i], tp_l[i]
            le[i], pend, sl_sent[i], tp_sent[i] = True, 1, sl_n, tp_n
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, sl_sent, tp_sent)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)[:2]
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l = _run(bars_df, p)[2:]
    o = bars_df["open"]
    sl_f = 1 - sl_l.shift(1) / o                              # the signal bar's levels, read at the fill
    tp_f = tp_l.shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
