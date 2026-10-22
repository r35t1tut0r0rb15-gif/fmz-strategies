"""Break-and-retest of the latest 3 / 3 pivot levels, broker days: after the low trades under the last pivot-low support, a close back at or over it with the low within 0.5 % of it goes long; after the high trades over the last pivot-high resistance, a close at or under it with the high within 0.5 % goes short; reversing, no other exit.
Port of FMZ strategy #482873 "Multi Level Quantitative Trend Trading Strategy Based on Support Resistance Breakout and Retest" (SR Breakout & Retest Strategy (4hr)).

FMZ source id: 482873

Source
    https://www.fmz.com/strategy/482873 (PineScript v5, FMZ last modified 2025-02-20 16:00:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-170), pivots 3 / 3; retest tolerance 0.005; 10 % of equity, capital 10000
    pivotlow(low, 3, 3) -> candidateSupport, broken / retested reset;  pivothigh(high, 3, 3) -> candidateResistance likewise
    not broken and low < support -> broken;  broken and not retested and close >= support and |low - support| <= support x 0.005 -> retested, entry Long_Support
    not broken and high > resistance -> broken;  broken and not retested and close <= resistance and |high - resistance| <= resistance x 0.005 -> retested, entry Short_Resistance

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is confirmed 3 bars after its bar and its level becomes the candidate on the confirming bar
      (Pine's pivotlow / pivothigh; the centre strictly beyond every bar of the 3 on each side). A break
      and a retest can fall on the same bar, as the sequential if lines allow. Default pyramiding refuses
      a second long while long; the other side reverses (REVERSAL INTENDED); a short called on the same
      bar as a long wins (called later, as #437773). There is no other exit. The labels are drawing only.
      The title's "4hr" is not the header's bar size (1d). The 10 % of equity size is sizing. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot level break-and-retest.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482873_pivot3_3_break_retest_0_5pct_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pivot_bars": [3, 5],
    "tolerance": [0.005, 0.01],
}
DEFAULT_PARAMS = {"pivot_bars": 3, "tolerance": 0.005}


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
    k, tol = int(p["pivot_bars"]), float(p["tolerance"])
    pl, ph = _pivot(lo, -1, k), _pivot(h, 1, k)
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sup = res = np.nan
    sb = sr = rb = rr = False
    for i in range(m):
        if pl[i]:
            sup, sb, sr = lv[i - k], False, False
        if ph[i]:
            res, rb, rr = hv[i - k], False, False
        if not np.isnan(sup):
            if not sb and lv[i] < sup:
                sb = True
            if sb and not sr and cv[i] >= sup and abs(lv[i] - sup) <= sup * tol:
                sr, le[i] = True, True
        if not np.isnan(res):
            if not rb and hv[i] > res:
                rb = True
            if rb and not rr and cv[i] <= res and abs(hv[i] - res) <= res * tol:
                rr, se[i] = True, True
    idx = c.index
    le, se = pd.Series(le, index=idx), pd.Series(se, index=idx)
    false = pd.Series(False, index=idx)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
