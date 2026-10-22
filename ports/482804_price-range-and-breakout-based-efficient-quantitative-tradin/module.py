"""Consolidation-zone breaks of a zigzag pivot, 5-day bars: once more than 5 bars have sat in the zone, a new zigzag pivot above the zone goes long and one below it goes short; reversing.
Port of FMZ strategy #482804 "Price Range and Breakout Based Efficient Quantitative Trading Strategy" (Consolidation Zones - Live [Strategy]).

FMZ source id: 482804

Source
    https://www.fmz.com/strategy/482804 (PineScript v5, FMZ last modified 2025-02-27 17:46:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-245), zigzag period 10; minimum consolidation 5 bars; MPL 2.0 notice (LonesomeTheBlue)
    hb_ = high when highestbars(10) == 0;  lb_ = low when lowestbars(10) == 0;  dir 1 / -1 from them;  zz = the pivot of the bar;  pp = the extreme zz of the current dir run (loop up to 1000 bars)
    change(pp) != 0 and conscnt > 5 -> pp > condhigh: breakoutup, pp < condlow: breakoutdown;  conscnt counts bars in the zone;  zone = highest / lowest(5) at conscnt == 5, then widened by each bar's high / low
    breakoutup -> close Short, entry Long;  breakoutdown -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars(prd) == 0 is read as the bar's high equal to the 10-bar highest high (a tie counts as
      the current bar); likewise for lows. pp is the highest (dir 1) or lowest (dir -1) zigzag value of the
      current direction run, the most recent one while dir is still 0; the source's 1000-bar loop cap is a
      run of ~19 years at 5-day bars, beyond the data, so the run is not capped. ta.change(pp) != 0 is
      false when either value is na (Pine's na comparison). condhigh / condlow keep their last values when
      the count resets, as the var lines do. The plots, fill and alerts are drawing only. Each break
      closes the other side and enters: REVERSAL INTENDED. No sizing code. The MPL 2.0 notice is kept with
      the verbatim copy (ported, stated). Bars are blocks of five broker days (17:00 America/New_York)
      counted from 1970-01-01, stamped with their first minute. FREQ = "5D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zigzag pivot breaks of a consolidation zone.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: five-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482804_zigzag10_consolidation5_zone_break_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5D"  # backtest header period: 5d (five broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [10, 20],
    "conslen": [5, 10],
}
DEFAULT_PARAMS = {"prd": 10, "conslen": 5, "days": 5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    prd, cl = int(p["prd"]), int(p["conslen"])
    has_hb = (h >= h.rolling(prd).max()).to_numpy()
    has_lb = (lo <= lo.rolling(prd).min()).to_numpy()
    hh = h.rolling(cl).max().to_numpy()
    ll = lo.rolling(cl).min().to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    up, dn = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    d = 0
    pp_prev = np.nan
    run_pp = np.nan
    cnt = 0
    chi = clo = np.nan
    for i in range(m):
        nd = 1 if (has_hb[i] and not has_lb[i]) else (-1 if (has_lb[i] and not has_hb[i]) else d)
        if i == 0 or nd != d:
            run_pp = np.nan                  # a new direction run
        d = nd
        if has_hb[i] and has_lb[i]:
            zz = hv[i] if d == 1 else lv[i]
        else:
            zz = hv[i] if has_hb[i] else (lv[i] if has_lb[i] else np.nan)
        if not np.isnan(zz):
            if np.isnan(run_pp) or d == 0:
                run_pp = zz
            elif d == 1 and zz > run_pp:
                run_pp = zz
            elif d == -1 and zz < run_pp:
                run_pp = zz
        pp = run_pp
        changed = (not np.isnan(pp)) and (not np.isnan(pp_prev)) and pp != pp_prev
        if changed:
            if cnt > cl and not np.isnan(chi) and not np.isnan(clo):
                up[i] = pp > chi
                dn[i] = pp < clo
            in_zone = cnt > 0 and not np.isnan(chi) and not np.isnan(clo) and clo <= pp <= chi
            cnt = cnt + 1 if in_zone else 0
        else:
            cnt += 1
        if cnt >= cl:
            if cnt == cl:
                chi, clo = hh[i], ll[i]
            else:
                chi = max(chi, hv[i]) if not np.isnan(chi) else np.nan
                clo = min(clo, lv[i]) if not np.isnan(clo) else np.nan
        pp_prev = pp
    idx = h.index
    le, se = pd.Series(up, index=idx), pd.Series(dn, index=idx)
    false = pd.Series(False, index=idx)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
