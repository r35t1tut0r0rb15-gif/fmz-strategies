"""Granville reversal (close crossing above the EMA 20) followed by a MACD golden cross, a MACD break above that
cross's value and a second golden cross: long, with the stop at the reversal bar's low and a target 1.618 reversal
ranges above the signal close, daily bars.
Port of FMZ strategy #482803 "基于Granville与MACD多重信号确认的趋势跟踪交易策略-Trend-Following-Trading-Strategy-Based-on-Granville-and-MACD-Multiple-Signal-Confirmation" (Granville + MACD Strategy).

FMZ source id: 482803

Source
    https://www.fmz.com/strategy/482803 (PineScript v5, FMZ last modified 2025-02-27 17:46:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-162), EMA 20, MACD 12 / 26 / 9
    crossover(close, ema) -> granvilleDone, low and range of that bar remembered, MACD stages reset
    granvilleDone and first crossover(macd, signal) -> macdGC_done, its bar and MACD value remembered
    macdGC_done and macd > that value -> breakoutDone
    all three and a later crossover(macd, signal) -> entry long with exit(stop = reversal low,
    limit = close + 1.618 x reversal range); every stage reset

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: (close - reversal low) / close and 1.618 x range /
      close, shifted one bar inside stops() and re-based on the fill (house rule). A signal whose stop is not below
      the close (zero-length trade) emits no entry (as L2 #491035); the stages still reset.
    * A new signal while held is ignored by the entry but re-places the exit at the new levels: fixed at entry,
      mark trailing_stop_pending (as #491506).
    * Long only. Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, an EMA, MACD and distances from the setup bar.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482803_granville_macd_staged_cross_bracket_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [20, 50],
    "tp_mult": [1.618, 1.0],
}
DEFAULT_PARAMS = {"ema_len": 20, "fast": 12, "slow": 26, "signal": 9, "tp_mult": 1.618}


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
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    cs = bars_df["close"]
    ema = cs.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = cs.ewm(span=int(p["fast"]), adjust=False).mean() - cs.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    rev = ((cs > ema) & (cs.shift(1) <= ema.shift(1))).to_numpy()
    gc = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    mv = macd.to_numpy()
    m = len(c)
    le = np.zeros(m, dtype=bool)
    sl, tp = np.full(m, np.nan), np.full(m, np.nan)
    g_done = gc_done = br_done = False
    g_low = g_rng = init_macd = np.nan
    gc_bar = None
    for i in range(m):
        if rev[i]:
            g_done, g_low, g_rng = True, lo[i], h[i] - lo[i]
            gc_done, br_done, init_macd, gc_bar = False, False, np.nan, None
        if g_done and not gc_done and gc[i]:
            gc_done, gc_bar, init_macd = True, i, mv[i]
        if gc_done and not br_done and mv[i] > init_macd:
            br_done = True
        if g_done and gc_done and br_done and gc_bar is not None and i > gc_bar and gc[i]:
            s_ = (c[i] - g_low) / c[i]
            if s_ > 0:
                le[i], sl[i], tp[i] = True, s_, p["tp_mult"] * g_rng / c[i]
            g_done = gc_done = br_done = False
            init_macd, gc_bar = np.nan, None
    return le, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl, tp = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl, index=idx).shift(1), "tp_stop": pd.Series(tp, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
