"""A candle wholly outside the Bollinger 20 / 1.5 band, broker days: after a candle wholly above the upper band, a 4-bar low under its low goes short; after one wholly below the lower band, a 4-bar high over its high goes long; a close 3 R beyond the candle's edge closes; reversing (the break-even stop is pending).
Port of FMZ strategy #489281 "Multi Timeframe Bollinger Band Breakout Reversion Strategy" (Bollinger Band Long & Short Strategy).

FMZ source id: 489281

Source
    https://www.fmz.com/strategy/489281 (PineScript v5, FMZ last modified 2025-04-03 10:26:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 186-260), BB 20 / 1.5; RR 3, break-even at 2 R; max loss 4000 per trade (sizing)
    candle[1] wholly above upper[1] and lowest(low, 4) < low[1] -> entry := low[1], risk := high[1] - low[1], tp := entry - 3 risk, be := entry - 2 risk, entry Short (qty = 4000 / risk)
    short and close <= be -> exit(stop = entry);  short and close <= tp -> close Short;  long mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels (entry reference, target, break-even) are shared vars set on every signal bar, held or
      not, and followed in a loop with the position, as written; the target is tested on closes and sent
      as a close (an exit signal). The break-even stop is armed only after a close beyond 2 R and then sits
      at the reference level: it cannot be held as a stop from the fill (the house lock-in trail keys on
      the best price and the fill), so it is not ported, mark trailing_stop_pending. An entry on the other
      side reverses (REVERSAL INTENDED). The risk-sized quantity is sizing (no entry when the range is
      zero). Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested 3 R target; the armed break-even stop pending.
    2 generic: PASS, outside-band candle breaks with an R-multiple target.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized quantity (4000 / risk) stored, not ported.
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

NAME = "fmz_489281_bb20_15_outside_candle_break_3r_close_target_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.5, 2.0],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"mult": 1.5, "rr": 3.0, "length": 20}


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
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    o1, h1, l1, c1 = o.shift(1), h.shift(1), lo.shift(1), c.shift(1)
    out_up = (c1 > up.shift(1)) & (o1 > up.shift(1)) & (l1 > up.shift(1))
    out_dn = (c1 < dn.shift(1)) & (o1 < dn.shift(1)) & (h1 < dn.shift(1))
    rng = h1 - l1
    s_sig = (out_up & (lo.rolling(4).min() < l1) & (rng > 0)).to_numpy()
    l_sig = (out_dn & (h.rolling(4).max() > h1) & (rng > 0)).to_numpy()
    h1v, l1v, rv, cv = h1.to_numpy(), l1.to_numpy(), rng.to_numpy(), c.to_numpy(dtype=float)
    rr = float(p["rr"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, nxt, tp = 0, 0, np.nan
    for i in range(m):
        pos = nxt
        if s_sig[i]:
            tp = l1v[i] - rv[i] * rr
            se[i] = True
            nxt = -1
        if pos < 0 and cv[i] <= tp:
            sx[i] = True
            if nxt == -1:
                nxt = 0
        if l_sig[i]:
            tp = h1v[i] + rv[i] * rr
            le[i] = True
            nxt = 1
        if pos > 0 and cv[i] >= tp:
            lx[i] = True
            if nxt == 1:
                nxt = 0
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    le_s, lx_s, se_s, sx_s = S(le), S(lx), S(se), S(sx)
    held_l = le_s & lx_s                   # a refused same-side entry with that bar's close
    held_s = se_s & sx_s
    return le_s & ~held_l, lx_s & ~se_s, se_s & ~held_s, sx_s & ~le_s


def portfolio_kwargs(**params):
    return {}
