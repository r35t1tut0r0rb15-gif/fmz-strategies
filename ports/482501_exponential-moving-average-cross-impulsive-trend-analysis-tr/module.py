"""Three bars after a close crosses the EMA 10: an up candle, a down candle, then an up candle closing above both
previous highs goes long (mirrored short), with the stop at the signal bar's low (high), daily bars.
Port of FMZ strategy #482501 "指数移动平均线交叉脉冲趋势分析交易策略-Exponential-Moving-Average-Cross-Impulsive-Trend-Analysis-Trading-Strategy" (EMA Cross Impulsive Strategy).

FMZ source id: 482501

Source
    https://www.fmz.com/strategy/482501 (PineScript v5, FMZ last modified 2025-02-18 17:41:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-183), EMA 10, impulsive body 10 ticks, RR 3
    bars since crossover(close, ema10): bar 1 bullish with body >= 10 ticks, bar 2 bearish, bar 3 bullish (body >=
    10 ticks) closing above max(high[1], high[2]) -> entry long with exit(stop = low, profit = close + 3 (close -
    low)); short mirrored after crossunder

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 10-tick minimum body is a price unit (criterion 2): a fraction of a dollar on the author's BTC_USDT, so it
      is dropped as inert (as #492009): any up (down) candle qualifies.
    * profit= takes TICKS; the source passes a price LEVEL (close + 3 R). Read as a price distance (lane rule,
      #427592) the target sits a full price away: unreachable, dropped as inert. The trade ends at the stop or on a
      reversal.
    * The bar counters start at 0 (var) and count from the first bar, so the pattern can also fire before the first
      cross (as written).
    * The stop is placed with the entry: (close - low) / close of the signal bar (shorts (high - close) / close),
      picked by the signal's side, shifted one bar inside stops() and re-based on the fill (house rule); a zero-length
      stop emits no entry. Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a stop set at entry.
    2 generic: PASS, an EMA, candle direction and the signal bar's range (the tick body and level target dropped).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, margin 100; the stop via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482501_ema10_cross_impulse_pullback_impulse"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [10, 20],
}
DEFAULT_PARAMS = {"ema_len": 10}


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


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    cs = bars_df["close"]
    ema = cs.ewm(span=int(p["ema_len"]), adjust=False).mean()
    up = ((cs > ema) & (cs.shift(1) <= ema.shift(1))).to_numpy()
    dn = ((cs < ema) & (cs.shift(1) >= ema.shift(1))).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    nl = ns = 0
    i1l = cl = i2l = i1s = cs_ = i2s = False
    for i in range(m):
        bull, bear = c[i] > o[i], c[i] < o[i]
        if up[i]:
            nl, i1l, cl, i2l = 0, False, False, False
        else:
            nl += 1
        if nl == 1:
            i1l = bull
        if nl == 2:
            cl = bear
        if nl == 3:
            i2l = bull and i >= 2 and c[i] > max(h[i - 1], h[i - 2])
        if dn[i]:
            ns, i1s, cs_, i2s = 0, False, False, False
        else:
            ns += 1
        if ns == 1:
            i1s = bear
        if ns == 2:
            cs_ = bull
        if ns == 3:
            i2s = bear and i >= 2 and c[i] < min(lo[i - 1], lo[i - 2])
        le[i] = nl == 3 and i1l and cl and i2l and c[i] > lo[i]
        se[i] = ns == 3 and i1s and cs_ and i2s and h[i] > c[i]
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    le = le & ~se                                   # the later short call wins on a shared bar
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sl = ((c - lo) / c).where(pd.Series(le & ~se, index=c.index), (h - c) / c)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
