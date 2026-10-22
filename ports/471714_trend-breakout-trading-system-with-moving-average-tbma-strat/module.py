"""Close breakouts over the SMA 20, daily bars, long only: a close over the SMA after one at or under it buys, with a stop at the 7-bar low and a target twice that distance over the close.
Port of FMZ strategy #471714 "Trend Breakout Trading System with Moving Average TBMA Strategy" (Trend Breakout with SL and TP).

FMZ source id: 471714

Source
    https://www.fmz.com/strategy/471714 (PineScript v5, FMZ last modified 2024-11-12 16:24:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-135), SMA 20; stop = lowest(low, 7) (current bar included); target = stop + 2 x (close - stop); the length 25 input unused
    close > sma20 and close[1] <= sma20 -> entry Long + exit(limit = low7 + 2 x (close - low7)) + exit(stop = low7)

Interpretation choices (Pine rules in SURVEY_README.md)
    * close[1] is compared with the current SMA, as written. The levels are prices fixed on the signal
      bar, sent as fractions of the fill open (the signal bar's levels shifted into the fill bar; a level
      at or through the fill open is closed one bar late), and followed in the loop. A new breakout
      while a long is held re-sends both exits from the new bar, which stops() cannot express: the
      opening levels are kept (as #434428, mark trailing_stop_pending). Long only. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, SMA breakouts with a swing-low stop and 2:1 target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_471714_close_over_sma20_low7_stop_2r_target_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trend_len": [20, 50],
    "low_len": [7, 14],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"trend_len": 20, "low_len": 7, "rr": 2.0}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    t = c.rolling(int(p["trend_len"])).mean()
    sig = ((c > t) & (c.shift(1) <= t)).to_numpy()
    sl_l = lo.rolling(int(p["low_len"])).min().to_numpy()
    cv, ov, hv, lv = (x.to_numpy(dtype=float) for x in (c, o, h, lo))
    rr = float(p["rr"])
    m = len(cv)
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
            sl_n = sl_l[i]
            tp_n = sl_n + (cv[i] - sl_n) * rr
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
