"""Broker days: on volume over 1.5 x its 20-day average, a close 1 % above the last confirmed swing high (pivots 10 / 10) or a rejection of the last swing low (low through it, close back above, within 1 %) goes long; the mirror goes short; a 3 % target and 2 % stop from each bar's close, re-sent every bar, are followed in the signals; reversing.
Port of FMZ strategy #491895 "Pivot Based Volume Weighted Breakout Reversal Strategy" (S/R Breakout/Reversal + Volume + Alerts).

FMZ source id: 491895

Source
    https://www.fmz.com/strategy/491895 (PineScript v5, FMZ last modified 2025-04-24 17:08:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 103-167), pivothigh / pivotlow 10 / 10 (last values kept); volume SMA 20 x 1.5; TP 3 %, SL 2 % from the current close every bar; 100 % of equity
    longCondition = (close > res x 1.01 and highVolume) or (close within 1 % of sup and low <= sup and close > sup and highVolume) -> entry Long;  shortCondition mirrored -> entry Short
    every bar: exit("Long TP/SL", limit = close x 1.03, stop = close x 0.98);  exit("Short TP/SL", limit = close x 0.97, stop = close x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent every bar from that bar's close (including the signal bar, for the pending
      entry), so they move both ways; the signals follow them: a bar that reaches the previous bar's stop
      or target closes the trade at the next open (mark trailing_stop_pending). A bar where both sides
      qualify (possible when the last swing high sits under the last swing low) takes the later call,
      the short. The swing levels are the last confirmed pivots (seen 10 bars after the pivot bar,
      strict). REVERSAL INTENDED. 100 % of equity is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent percent exits followed in the signals.
    2 generic: PASS, swing-level breakouts and rejections on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491895_swing_sr_breakout_rejection_volume_rolling_pct_exits_reversal"
FAMILY = "breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pivot_len": [10, 5],
    "tp_pct": [3.0, 5.0],
}
DEFAULT_PARAMS = {"pivot_len": 10, "vol_mult": 1.5, "tp_pct": 3.0, "sl_pct": 2.0}


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
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    k = int(p["pivot_len"])
    ph, phv = _pivot_hit(h, 1, k, k)
    pl, plv = _pivot_hit(lo, -1, k, k)
    res = _fixnan(pd.Series(np.where(ph, phv, np.nan), index=c.index))
    sup = _fixnan(pd.Series(np.where(pl, plv, np.nan), index=c.index))
    hv = v > v.rolling(20).mean() * float(p["vol_mult"])
    buy = (((c > res * 1.01) & hv)
           | ((c >= sup * 0.99) & (c <= sup * 1.01) & (lo <= sup) & (c > sup) & hv)).to_numpy()
    sell = (((c < sup * 0.99) & hv)
            | ((c >= res * 0.99) & (c <= res * 1.01) & (h >= res) & (c < res) & hv)).to_numpy()
    tp, sl = float(p["tp_pct"]) / 100, float(p["sl_pct"]) / 100
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    l_tp, l_st, s_tp, s_st = cn * (1 + tp), cn * (1 - sl), cn * (1 - tp), cn * (1 + sl)
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine = 0, 0
    for i in range(m):
        held = pine
        if i > 0 and held == 1 and (ln[i] <= l_st[i - 1] or hn[i] >= l_tp[i - 1]):
            held = 0                       # the exit sent at the previous close is touched
        elif i > 0 and held == -1 and (hn[i] >= s_st[i - 1] or ln[i] <= s_tp[i - 1]):
            held = 0
        new = held
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1                       # the later call wins on a two-sided bar
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
