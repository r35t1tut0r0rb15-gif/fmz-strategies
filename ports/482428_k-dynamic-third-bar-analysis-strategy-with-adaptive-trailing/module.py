"""Two consecutive bars closing in the upper third of their range (the second opening in its lower or upper third) go
long, the lower-third mirror goes short; a stop at the previous bar's low (high), re-placed every bar, ends the
trade, daily bars.
Port of FMZ strategy #482428 "动态跟踪止损的三分之一K线量化交易策略-Dynamic-Third-Bar-Analysis-Strategy-with-Adaptive-Trailing-Stop" (TrinityBar with Trailing Stop).

FMZ source id: 482428

Source
    https://www.fmz.com/strategy/482428 (PineScript v5, FMZ last modified 2025-02-18 13:57:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 97-173), thirds of each bar's range, trailing 1 bar back
    validBuy = previous bar closes in its upper third (any open) and this bar opens in its lower or upper third and
    closes in its upper third -> close short, entry long when not long; validSell mirrored
    while long, every bar: exit(stop = low[1]); while short: exit(stop = high[1])

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop sits at the previous bar's low (high) and is re-placed every bar from the bar after the fill: a moving
      level the house bracket (fixed at the fill) cannot carry. simulate() keeps the resting order (placed at a
      bar's close, active from the next bar) and emits an exit signal on the bar whose low (high) reaches it, filled
      at the next open (one bar after Pine's stop fill). Mark trailing_stop_pending. A bar that reaches the stop and
      signals keeps only the reversal (or only the exit on a same-side signal).
    * The trailing timeframe input is the chart's own (""): low[1] / high[1] of the chart.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the previous-bar stop as exit signals (marked).
    2 generic: PASS, thirds of each bar's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND482242 with #482242 (Jaccard 0.770, similar, not a duplicate); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482428_trinity_bar_thirds_prev_bar_stop"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_bars": [1, 2],
}
DEFAULT_PARAMS = {"trail_bars": 1}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = h - lo
    lt, ut = lo + rng / 3, h - rng / 3
    up_c, dn_c = c >= ut, c <= lt
    o_lo, o_up = o <= lt, o >= ut
    buy = (up_c.shift(1, fill_value=False) & (o_lo | o_up) & up_c).to_numpy()
    sell = (dn_c.shift(1, fill_value=False) & (o_lo | o_up) & dn_c).to_numpy()
    both = buy & sell
    buy, sell = buy & ~both, sell & ~both            # a zero-range bar meets both: neither
    k = int(p["trail_bars"])
    tl, th = lo.shift(k).to_numpy(), h.shift(k).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend = 0, 0
    stop_l = stop_s = np.nan
    for i in range(m):
        if pend:
            pos, pend = pend, 0
            stop_l = stop_s = np.nan
        hit = 0
        if pos == 1 and not np.isnan(stop_l) and lv[i] <= stop_l:
            hit, pos, stop_l = 1, 0, np.nan
        elif pos == -1 and not np.isnan(stop_s) and hv[i] >= stop_s:
            hit, pos, stop_s = -1, 0, np.nan
        if buy[i] and pos <= 0 and hit != 1 and i + 1 < m:
            le[i], pend = True, 1
        elif sell[i] and pos >= 0 and hit != -1 and i + 1 < m:
            se[i], pend = True, -1
        if hit == 1 and not se[i]:
            lx[i] = True
        if hit == -1 and not le[i]:
            sx[i] = True
        if not pend:
            if pos == 1:
                stop_l = tl[i]
            elif pos == -1:
                stop_s = th[i]
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
