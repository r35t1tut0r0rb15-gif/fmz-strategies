"""Broker days, long only: the close above the close of the bar that confirmed the latest close pivot high (46 / 32) goes long (re-entering while it holds); once a close falls back to or under that level while long, a bracket of -1.75 % / +2 % around the entry price is armed and ends the trade.
Port of FMZ strategy #442333 "Quantitative Breakthrough Uptrend Reference Strategy" (Steady Uptrend Strategy (CheatCode1)).

FMZ source id: 442333

Source
    https://www.fmz.com/strategy/442333 (PineScript v5, FMZ last modified 2024-02-21 10:58:01).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 131-224), pivots on the close 46 / 32; take profit 2 %, stop 1.75 %; volume filter unused
    l1 = pivothigh(close, 46, 32);  l1V = valuewhen(l1, close, 0);  close > l1V -> entry Long;  close < S1V -> cancel Long
    position_size > 0 and not (close > l1V) -> exit(stop = avg x (1 - 1.75 %), limit = avg x (1 + 2 %));  openprofit >= 0 and sL -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * valuewhen(l1, close, 0) is the close of the bar on which the pivot is confirmed (32 bars after
      the pivot), not the pivot's own value (weird case). An entry is cancelled on a bar that is also
      below the support level. The bracket order exists only from the first bar whose close is not above
      the level while long and then stays; the house engine cannot arm a bracket later, so the signals
      follow it: after it is armed, a bar whose low reaches the stop or whose high reaches the target
      closes the trade at the next open (mark trailing_stop_pending). The sL close needs Plotl1 < PlotS1 on
      one bar, but both then equal that bar's close, so it can never fire. The volume SMA feeds nothing: volume is not used.
      Long only. 100 % of equity and the commission are sizing and costs. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; late-armed bracket followed in the signals.
    2 generic: PASS, closes above a pivot-confirmation level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 1500, commission 0.01 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442333_close_above_pivot_confirm_level_late_bracket_long_only"
FAMILY = "support_resistance"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "left": [46, 20],
    "right": [32, 10],
}
DEFAULT_PARAMS = {"left": 46, "right": 32, "take": 0.02, "stop": 0.0175}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    L, R = int(p["left"]), int(p["right"])
    ph, _ = _pivot_hit(c, 1, L, R)
    pl, _ = _pivot_hit(c, -1, L, R)
    cv = c.to_numpy(dtype=float)
    l1v = _fixnan(pd.Series(np.where(ph, cv, np.nan), index=c.index)).to_numpy()
    s1v = _fixnan(pd.Series(np.where(pl, cv, np.nan), index=c.index)).to_numpy()
    lc = cv > l1v
    sc = cv < s1v
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tk, st = float(p["take"]), float(p["stop"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_in, pend_out, px, armed = 0, False, False, np.nan, False
    for i in range(m):
        if pend_in:
            pos, pend_in, px, armed = 1, False, ov[i], False
        if pend_out:
            pos, pend_out = 0, False
        if pos == 1:
            hit = armed and (lv[i] <= px * (1 - st) or hv[i] >= px * (1 + tk))
            if hit:
                if i + 1 < m:
                    lx[i], pend_out = True, True
                continue
            if not lc[i]:
                armed = True
        elif not pend_in and lc[i] and not sc[i] and i + 1 < m:
            le[i], pend_in = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
