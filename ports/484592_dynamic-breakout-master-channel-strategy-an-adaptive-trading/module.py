"""Breakouts of pivot-based support / resistance zones, always in, broker days: confirmed 10-bar pivots of the last 290
bars are grouped into zones no wider than 5 % of the 300-bar range and ranked by pivot count and touches; when the
close is outside every zone, a close crossing above a zone's top goes long and a close crossing below a zone's bottom
goes short.
Port of FMZ strategy #484592 "动态突破大师通道策略基于支撑阻力突破的自适应交易系统-Dynamic-Breakout-Master-Channel-Strategy-An-Adaptive-Trading-System-Based-on-Support-and-Resistance-Breakouts" (Dynamic Breakout Master by tradingbauhaus ).

FMZ source id: 484592

Source
    https://www.fmz.com/strategy/484592 (PineScript v6, FMZ last modified 2025-03-03 10:33:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 208-372), pivot period 10 (high / low), channel width 5 % of the 300-bar
range, min strength 1, 6 zones, lookback 290
    on a new pivot: store it (drop pivots older than 290 bars); for each pivot build a channel of the pivots within the
    width (strength + 20 each); add the touches of the last 290 bars' highs / lows; pick up to 10 strongest
    non-overlapping channels as zones; sort by strength (the source's swap keeps a partial power array, as written)
    close inside no zone: close[1] <= top and close > top (any of the first 6 zones) -> entry long;
    close[1] >= bottom and close < bottom -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.pivothigh / pivotlow as #430850 (strictly above / below the 10 bars on each side), known 10 bars after the
      pivot bar: no look-ahead. The 300-bar range is the high / low over 300 bars (na before: channels of one pivot).
    * The zone build, the touch count and the sort run exactly as written (including the sort's power-array quirk).
    * Both breakouts on one bar: the short, written last, wins. Entries reverse (REVERSAL INTENDED).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot zones scaled by the rolling range.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_484592_pivot_zone_breakout"
FAMILY = "support_resistance_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 5],
    "width_pct": [5, 3],
}
DEFAULT_PARAMS = {"period": 10, "width_pct": 5, "strength": 1, "max_zones": 6, "lookback": 290, "range_len": 300}


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


def _pivots(x, lb, rb, high):
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        if np.isnan(v):
            continue
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        out[t] = (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())
    return out


def _zones_rebuild(values, t, hv, lv, maxw, strength_min, lookback):
    n = len(values)
    levels = []
    for x in range(n):
        ceil = flo = values[x]
        s = 0
        for lvl in values:
            gap = ceil - lvl if lvl <= ceil else lvl - flo
            if gap <= maxw:                              # False while the 300-bar range is na
                if lvl <= ceil:
                    flo = min(flo, lvl)
                else:
                    ceil = max(ceil, lvl)
                s += 20
        levels += [float(s), ceil, flo]
    a = max(0, t - lookback)
    hs, ls = hv[a:t + 1], lv[a:t + 1]
    for x in range(n):
        top, bot = levels[3 * x + 1], levels[3 * x + 2]
        levels[3 * x] += int((((hs <= top) & (hs >= bot)) | ((ls <= top) & (ls >= bot))).sum())
    zones = [0.0] * 20
    power = [0.0] * 10
    counter = 0
    for _ in range(n):
        maxpower, maxspot = -1.0, -1
        for y in range(n):
            if levels[3 * y] > maxpower and levels[3 * y] >= strength_min * 20:
                maxpower, maxspot = levels[3 * y], y
        if maxspot >= 0:
            top, bot = levels[3 * maxspot + 1], levels[3 * maxspot + 2]
            zones[2 * counter], zones[2 * counter + 1] = top, bot
            power[counter] = levels[3 * maxspot]
            for y in range(n):
                if bot <= levels[3 * y + 1] <= top or bot <= levels[3 * y + 2] <= top:
                    levels[3 * y] = -1
            counter += 1
            if counter >= 10:
                break
    for x in range(9):
        for y in range(x + 1, 10):
            if power[y] > power[x]:
                power[y] = power[x]                      # as written: power[x] is not given the old power[y]
                zones[2 * x], zones[2 * y] = zones[2 * y], zones[2 * x]
                zones[2 * x + 1], zones[2 * y + 1] = zones[2 * y + 1], zones[2 * x + 1]
    return zones


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    per, lb = int(p["period"]), int(p["lookback"])
    ph = _pivots(hv, per, per, True)
    pl = _pivots(lv, per, per, False)
    rl = int(p["range_len"])
    top300 = bars_df["high"].rolling(rl).max().to_numpy()
    bot300 = bars_df["low"].rolling(rl).min().to_numpy()
    nz = min(9, int(p["max_zones"]) - 1)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    values, positions = [], []
    zones = [0.0] * 20
    for t in range(m):
        if ph[t] or pl[t]:
            values.insert(0, hv[t - per] if ph[t] else lv[t - per])
            positions.insert(0, t)
            while positions and t - positions[-1] > lb:
                values.pop()
                positions.pop()
            maxw = (top300[t] - bot300[t]) * p["width_pct"] / 100
            zones = _zones_rebuild(values, t, hv, lv, maxw, int(p["strength"]), lb)
        if t == 0:
            continue
        inside = any(zones[2 * x + 1] <= cv[t] <= zones[2 * x] for x in range(nz + 1))
        if inside:
            continue
        res = any(cv[t - 1] <= zones[2 * x] < cv[t] for x in range(nz + 1))
        sup = any(cv[t - 1] >= zones[2 * x + 1] > cv[t] for x in range(nz + 1))
        se[t] = sup
        le[t] = res and not sup
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
