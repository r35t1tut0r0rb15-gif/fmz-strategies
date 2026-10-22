"""Pivot-built support / resistance channels (10 / 10 pivots over 290 bars, channel width 5 % of the 300-bar range, strength by pivot count plus bar touches), broker days: a close leaving the zones upward through a zone top goes long, downward through a zone bottom goes short; reversing, no other exit.
Port of FMZ strategy #484592 "Dynamic Breakout Master Channel Strategy An Adaptive Trading System Based on Support and Resistance Breakouts" (Dynamic Breakout Master by tradingbauhaus).

FMZ source id: 484592

Source
    https://www.fmz.com/strategy/484592 (PineScript v6, FMZ last modified 2025-03-03 10:33:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 204-372), pivot period 10 (High/Low); channel width 5 %; min strength 1; max zones 6; lookback 290; commission 0.1 %; MPL 2.0 notice (tradingbauhaus)
    on each pivot bar: store the pivot (newest first, drop those older than 290 bars);  for each pivot build a channel of the pivots within 5 % of the 300-bar range (strength 20 each) plus one per bar of the last 291 touching it;  take the strongest channels in turn (at least 20), removing overlapping ones, up to 10, then order them by strength
    not inside any of the first 6 zones and close[1] <= top < close -> entry ResBreak (long);  close[1] >= bottom > close -> entry SupBreak (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zone engine is followed as written, including its ordering step, which copies power[x] into
      power[y] without moving power[y] into power[x] (only the zones are swapped). The zones are rebuilt
      only on pivot bars and kept between them; a pivot is confirmed 10 bars after its bar (the centre
      strictly beyond every bar of the 10 on each side) and is stored with the confirming bar's index.
      The moving averages and the colours are drawing only. Entries only: each reverses the other side
      (REVERSAL INTENDED), no other exit; a short called on the same bar as a long wins (as #437773). The
      commission is a cost (the house cost model applies). The MPL 2.0 notice is kept with the verbatim
      copy (ported, stated). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot support / resistance zone breaks.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484592_pivot10_sr_zone_engine_break_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 5],
    "channel_width": [5, 3],
}
DEFAULT_PARAMS = {"period": 10, "channel_width": 5, "strength": 1, "max_zones": 6, "lookback": 290,
                  "range_bars": 300}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k, lb, rb = int(p["period"]), int(p["lookback"]), int(p["range_bars"])
    ph, pl = _pivot(h, 1, k), _pivot(lo, -1, k)
    width = ((h.rolling(rb).max() - lo.rolling(rb).min()) * float(p["channel_width"]) / 100).to_numpy()
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    nz = min(9, int(p["max_zones"]) - 1)
    min_pow = int(p["strength"]) * 20
    vals, poss = [], []
    zones = np.zeros(20)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for i in range(m):
        if ph[i] or pl[i]:
            vals.insert(0, hv[i - k] if ph[i] else lv[i - k])
            poss.insert(0, i)
            while poss and i - poss[-1] > lb:
                vals.pop()
                poss.pop()
            n = len(vals)
            lev = []
            for x in range(n):
                ceil_ = flo = vals[x]
                st = 0
                for lvl in vals:
                    gap = ceil_ - lvl if lvl <= ceil_ else lvl - flo
                    if gap <= width[i]:
                        if lvl <= ceil_:
                            flo = min(flo, lvl)
                        else:
                            ceil_ = max(ceil_, lvl)
                        st += 20
                lev.append([float(st), ceil_, flo])
            lo0 = max(0, i - lb)
            hw, lw = hv[lo0:i + 1], lv[lo0:i + 1]
            for x in range(n):
                top, bot = lev[x][1], lev[x][2]
                lev[x][0] += float(np.sum(((hw <= top) & (hw >= bot)) | ((lw <= top) & (lw >= bot))))
            zones[:] = 0.0
            power = np.zeros(10)
            cnt = 0
            for _ in range(n):
                mp, ms = -1.0, -1
                for y in range(n):
                    if lev[y][0] > mp and lev[y][0] >= min_pow:
                        mp, ms = lev[y][0], y
                if ms >= 0:
                    top, bot = lev[ms][1], lev[ms][2]
                    zones[cnt * 2], zones[cnt * 2 + 1] = top, bot
                    power[cnt] = lev[ms][0]
                    for y in range(n):
                        if bot <= lev[y][1] <= top or bot <= lev[y][2] <= top:
                            lev[y][0] = -1.0
                    cnt += 1
                    if cnt >= 10:
                        break
            for x in range(9):
                for y in range(x + 1, 10):
                    if power[y] > power[x]:
                        power[y] = power[x]              # as written: power[x] is not updated
                        zones[[y * 2, x * 2]] = zones[[x * 2, y * 2]]
                        zones[[y * 2 + 1, x * 2 + 1]] = zones[[x * 2 + 1, y * 2 + 1]]
        if i == 0:
            continue
        out = True
        for x in range(nz + 1):
            if zones[x * 2 + 1] <= cv[i] <= zones[x * 2]:
                out = False
        if out:
            for x in range(nz + 1):
                if cv[i - 1] <= zones[x * 2] < cv[i]:
                    le[i] = True
                if cv[i - 1] >= zones[x * 2 + 1] > cv[i]:
                    se[i] = True
    idx = c.index
    le_s, se_s = pd.Series(le, index=idx), pd.Series(se, index=idx)
    false = pd.Series(False, index=idx)
    return le_s & ~se_s, false, se_s, false.copy()


def portfolio_kwargs(**params):
    return {}
