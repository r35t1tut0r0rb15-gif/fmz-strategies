"""Breakouts of consolidation zones found from zig-zag pivots: when the latest pivot extreme leaves a zone that has
held for more than 5 bars, go long above it and short below it, always in, five-day bars.
Port of FMZ strategy #482804 "基于价格区间和突破的高效量化交易策略Price-Range-and-Breakout-Based-Efficient-Quantitative-Trading-Strategy" (Consolidation Zones - Live [Strategy]).

FMZ source id: 482804

Source
    https://www.fmz.com/strategy/482804 (PineScript v5, FMZ last modified 2025-02-27 17:46:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 112-245), pivot period 10, minimum consolidation 5
    hb = high if it is the 10-bar highest, lb = low if the 10-bar lowest; dir = 1 / -1 on a lone hb / lb
    zz = the bar's pivot (dir decides on a bar with both); pp = the extreme zz of the current dir run
    when pp changes: breakout up if conscnt > 5 and pp > condhigh, down if pp < condlow; conscnt counts on while pp
    stays inside [condlow, condhigh], else resets to 0; when pp does not change: conscnt += 1
    conscnt == 5 -> zone = 5-bar highest high / lowest low; conscnt > 5 -> zone widened by each bar's high / low
    breakout up -> entry long (after closing a short); breakout down -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars(10) == 0 is read as "the bar's high equals the 10-bar highest" (ties count as the current bar);
      lowestbars mirrored.
    * pp is the highest (dir 1) or lowest (dir -1) pivot since dir last changed, as the source's 1000-bar loop; while
      dir is still 0 it is the latest pivot. ta.change(pp) with na on either side counts as no change.
    * The closes before each entry repeat the reversal (REVERSAL INTENDED); always in after the first breakout.
      Signal module, no stops. Five-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as
      #426509); FREQ = "5D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling extremes and pivot-defined ranges.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in five-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482804_pivot_consolidation_zone_breakout_5d"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5D"  # backtest header period: 5d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [10, 20],
    "conslen": [5, 10],
}
DEFAULT_PARAMS = {"prd": 10, "conslen": 5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=5):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=5)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    prd, cl = int(p["prd"]), int(p["conslen"])
    has_h = (h >= h.rolling(prd).max()).to_numpy()
    has_l = (lo <= lo.rolling(prd).min()).to_numpy()
    hh, ll = h.rolling(cl).max().to_numpy(), lo.rolling(cl).min().to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    d = 0
    prev_d = None
    run_ext = run_last = np.nan
    prev_pp = np.nan
    cnt, ch, cl_ = 0, np.nan, np.nan
    pos = 0
    for i in range(m):
        if has_h[i] and not has_l[i]:
            d = 1
        elif has_l[i] and not has_h[i]:
            d = -1
        if has_h[i] and has_l[i]:
            zz = hv[i] if d == 1 else lv[i]
        else:
            zz = hv[i] if has_h[i] else (lv[i] if has_l[i] else np.nan)
        if prev_d is None or d != prev_d:                  # a new dir run: the loop stops at the change
            run_ext = run_last = np.nan
        prev_d = d
        if not np.isnan(zz):
            run_last = zz
            if np.isnan(run_ext):
                run_ext = zz
            elif d == 1:
                run_ext = max(run_ext, zz)
            elif d == -1:
                run_ext = min(run_ext, zz)
        pp = run_ext if d != 0 else run_last
        up = dn = False
        if not np.isnan(pp) and not np.isnan(prev_pp) and pp != prev_pp:
            if cnt > cl and not np.isnan(ch) and not np.isnan(cl_):
                up, dn = pp > ch, pp < cl_
            in_zone = cnt > 0 and not np.isnan(ch) and not np.isnan(cl_) and cl_ <= pp <= ch
            cnt = cnt + 1 if in_zone else 0
        else:
            cnt += 1
        if cnt >= cl:
            if cnt == cl:
                ch, cl_ = hh[i], ll[i]
            else:
                ch, cl_ = max(ch, hv[i]), min(cl_, lv[i])
        prev_pp = pp
        if up and pos != 1:
            le[i], pos = True, 1
        if dn and pos != -1:
            se[i], pos = True, -1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
