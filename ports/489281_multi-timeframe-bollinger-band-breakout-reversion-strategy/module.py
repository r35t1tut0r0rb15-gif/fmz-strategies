"""Bollinger 20 x 1.5 outside-candle reversals with a 3 R close target, broker days: after a candle entirely above the
upper band, a bar that trades below that candle's low goes short; after a candle entirely below the lower band, a bar
above its high goes long; a close beyond three times the outside candle's range from its low (high) closes the trade
(the source's break-even stop is pending).
Port of FMZ strategy #489281 "多周期布林带突破回归交易策略-Multi-Timeframe-Bollinger-Band-Breakout-Reversion-Strategy" (Bollinger Band Long & Short Strategy).

FMZ source id: 489281

Source
    https://www.fmz.com/strategy/489281 (PineScript v5, FMZ last modified 2025-04-03 10:26:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 190-253), BB 20 x 1.5, RR 3, break-even at 2 R
    outsideUpper = open[1], close[1] and low[1] all above the upper band [1];  outsideLower mirrored
    short = outsideUpper and lowest(low, 4) < low[1] (and barssince(outsideUpper) <= 4): entry = low[1], stop level
    = high[1], risk = high[1] - low[1], target = entry - 3 risk, break-even level = entry - 2 risk
    short held: close <= break-even level -> exit(stop = entry);  close <= target -> close;  longs mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * lowest(low, 4) includes the current bar, so it is below low[1] when this bar's low (or one of the two before
      it) is; barssince(outsideUpper) is 0 on the signal bar. The stop level is used only for the risk: there is no
      initial stop, as written.
    * The target is checked on closes: a close-based exit signal (rule 3).
    * The break-even stop starts after a close at 2 R, where R is the outside candle's range (a per-trade gain the
      house lock_in cannot express): mark trailing_stop_pending, described in PORT_NOTES.md, not emitted.
    * The levels are shared variables, overwritten by each signal; the checks use the position held at the bar.
      Entries reverse (REVERSAL INTENDED); the two setups cannot fall on one bar. The INR loss cap is sizing.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a close-checked target; the break-even stop pending (mark).
    2 generic: PASS, band positions and candle ranges.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed-loss quantity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489281_bb_outside_candle_reversal_3r"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.5, 2.0],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.5, "rr": 3.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = c.rolling(n).std(ddof=0)
    ub, lb = basis + p["mult"] * dev, basis - p["mult"] * dev
    out_up = ((c.shift(1) > ub.shift(1)) & (o.shift(1) > ub.shift(1)) & (lo.shift(1) > ub.shift(1))).to_numpy()
    out_dn = ((c.shift(1) < lb.shift(1)) & (o.shift(1) < lb.shift(1)) & (h.shift(1) < lb.shift(1))).to_numpy()
    brk_low = (lo.rolling(4).min() < lo.shift(1)).to_numpy()
    brk_high = (h.rolling(4).max() > h.shift(1)).to_numpy()
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    rr = float(p["rr"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = held = 0
    target = np.nan
    for i in range(1, m):
        start = pos
        if out_up[i] and brk_low[i]:
            entry, risk = lv[i - 1], hv[i - 1] - lv[i - 1]
            target = entry - risk * rr
            if risk > 0:
                pos = -1
        if held == -1 and cv[i] <= target and start == -1 and pos == -1:
            pos = 0
        if out_dn[i] and brk_high[i]:
            entry, risk = hv[i - 1], hv[i - 1] - lv[i - 1]
            target = entry + risk * rr
            if risk > 0:
                pos = 1
        if held == 1 and cv[i] >= target and start == 1 and pos == 1:
            pos = 0
        tgt[i] = pos
        held = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
