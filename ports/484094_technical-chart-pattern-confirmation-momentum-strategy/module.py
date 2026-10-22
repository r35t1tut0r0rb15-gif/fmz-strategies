"""Five-bar high / low patterns with a close beyond the previous bar, broker days: a "head and shoulders", double bottom or ascending-triangle shape closing over the previous high goes long, a double top, descending triangle or flag closing under the previous low goes short, each with a 1.5 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #484094 "Technical Chart Pattern Confirmation Momentum Strategy" (Chart Pattern Strategy - Full Set).

FMZ source id: 484094

Source
    https://www.fmz.com/strategy/484094 (PineScript v5, FMZ last modified 2025-02-28 09:50:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 220-278), ATR 14; stop 1.5 ATR; target 3 ATR; pattern tests on bars [0..4]
    long = (headShoulders or doubleBottom or ascendingTriangle) and close > high[1] -> entry Buy + exit(stop = close - 1.5 atr, limit = close + 3 atr)
    short = (doubleTop or descendingTriangle or flag) and close < low[1] -> entry Sell + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pattern tests are kept as written (the "head and shoulders" and "double top" tests are the same
      five-bar high test; with close > high[1] the first can never fire, since it needs high < high[1]).
      The symmetrical triangle is a plot only. The levels are fixed at the signal close and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A repeat signal while held re-sends the bracket; stops() keeps the first, so the repeat
      case is marked trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED); a short called on the same bar as a long wins (called later, as #437773). Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, short bar-pattern breakouts with an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484094_five_bar_patterns_prev_bar_break_atr1_5_3_bracket_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_length": [14, 20],
    "tp_atr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_length": 14, "tp_atr": 3.0, "sl_atr": 1.5}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    H = [h.shift(k) for k in range(5)]
    L = [lo.shift(k) for k in range(5)]
    top = (H[1] > H[2]) & (H[1] > H[0]) & (H[1] > H[3]) & (H[1] > H[4]) & (H[0] < H[2]) & (H[0] < H[3])
    bottom = (L[1] < L[2]) & (L[1] < L[0]) & (L[1] < L[3]) & (L[1] < L[4]) & (L[0] > L[2]) & (L[0] > L[3])
    asc = (H[2] < H[1]) & (L[2] > L[1]) & (H[3] < H[2]) & (L[3] > L[2])
    desc = (H[2] > H[1]) & (L[2] < L[1]) & (H[3] < H[2]) & (L[3] < L[2])
    flag = (H[1] < H[0]) & (L[1] > L[0]) & (H[2] < H[1]) & (L[2] < L[1])
    se = (top | desc | flag) & (c < L[1])
    le = (top | bottom | asc) & (c > H[1]) & ~se
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_length"]))
    a, b = atr * float(p["sl_atr"]), atr * float(p["tp_atr"])
    lvl = {"l_sl": c - a, "l_tp": c + b, "s_sl": c + a, "s_tp": c - b}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
