"""Candle-run internal shifts after a touch of the 10-bar low (high), broker days, from flat: a close over the previous and current bearish-run highs after a low touch goes long, the mirror goes short; the opposite signal or a close a few ticks beyond the entry close (stop 10, target 20 ticks) closes.
Port of FMZ strategy #488536 "Dynamic Liquidity Driven Market Structure Adaptive Trading Strategy" (Liquidity + Internal Market Shift Strategy).

FMZ source id: 488536

Source
    https://www.fmz.com/strategy/488536 (PineScript v6, FMZ last modified 2025-03-28 17:13:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-343), mode Both; SL 10 ticks; TP 20 ticks (on); liquidity lookback 10 / 10; run length 1
    runs of bullish / bearish candles keep their lowest low / highest high;  shift up: close > previous and current bearish-run highs;  shift down: mirror
    touch: low <= lowest(low, 10) / high >= highest(high, 10) (kept);  signals need the touch and no lock (locks clear after 3 bars or a new touch)
    flat (entryPrice na) and bearish signal -> entry Short;  flat and bullish signal -> entry Long;  opposite signal -> close;  close <= entry - 10 ticks or >= entry + 20 ticks -> close (long; short mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The candle runs, kept touches, locks, the bar counter and the entry-price state are followed in a
      loop, as written; lastInternalShift is never changed, so it never blocks. The tick distances are
      read as percents at the header coin's price (ETH about 3000 with tick 0.01: 10 ticks = 0.0033 %; C2
      ADAPT, as #458242) and tested on closes (exit signals, no stop module). Entries only while the state
      is flat: Opposite entries cannot occur. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based tick stop and target.
    2 generic: ADAPT, tick distances read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488536_liquidity_touch_internal_shift_tick_close_exits_flat"
FAMILY = "market_structure"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [10, 20],
    "stop_ticks": [10, 100],
}
DEFAULT_PARAMS = {"lookback": 10, "stop_ticks": 10, "tick_frac": 3.3333e-06}


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
    n = int(p["lookback"])
    at_low = (lo <= lo.rolling(n).min()).to_numpy()
    at_high = (h >= h.rolling(n).max()).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    sl_f = float(p["stop_ticks"]) * float(p["tick_frac"])
    tp_f = 2 * sl_f
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    bc = brc = 0
    lbp = hbp = pbp = pbrp = np.nan
    t_lo = t_hi = lock_b = lock_s = False
    bslt = np.nan
    ep, side = np.nan, 0
    for i in range(m):
        if cv[i] > ov[i]:
            bc, brc = bc + 1, 0
            if bc == 1 or lv[i] < lbp:
                lbp = lv[i]
        elif cv[i] < ov[i]:
            brc, bc = brc + 1, 0
            if brc == 1 or hv[i] > hbp:
                hbp = hv[i]
        else:
            bc = brc = 0
            lbp = hbp = np.nan
        shift_dn = cv[i] < pbp and cv[i] < lbp          # na compares false
        shift_up = cv[i] > pbrp and cv[i] > hbp
        if bc >= 1:
            pbp = lbp
        if brc >= 1:
            pbrp = hbp
        if at_low[i]:
            t_lo = True
        if at_high[i]:
            t_hi = True
        bull = shift_up and t_lo and not lock_b
        bear = shift_dn and t_hi and not lock_s
        if bull:
            lock_b, t_lo, bslt = True, False, 0.0
        if bear:
            lock_s, t_hi, bslt = True, False, 0.0
        if not np.isnan(bslt):
            bslt += 1
        if bslt >= 3:
            lock_b = lock_s = False
        if t_lo:
            lock_b = False
        if t_hi:
            lock_s = False
        if bear and np.isnan(ep):
            se[i], ep, side = True, cv[i], -1
        if bull and np.isnan(ep):
            le[i], ep, side = True, cv[i], 1
        if side == -1 and bull:
            sx[i], ep, side = True, np.nan, 0
        if side == 1 and bear:
            lx[i], ep, side = True, np.nan, 0
        if side == 1 and (cv[i] <= ep * (1 - sl_f) or cv[i] >= ep * (1 + tp_f)):
            lx[i], ep, side = True, np.nan, 0
        if side == -1 and (cv[i] >= ep * (1 + sl_f) or cv[i] <= ep * (1 - tp_f)):
            sx[i], ep, side = True, np.nan, 0
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~le), S(se), S(sx & ~se)


def portfolio_kwargs(**params):
    return {}
