"""A pivot-based zigzag direction (5 / 5 pivots, 1 % deviation) with Williams %R 14 crossings, 2-day bars: in an up-leg %R crossing back over -80 goes long, in a down-leg %R crossing back under -20 goes short, each with a 1 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #482419 "Trend Momentum Strategy Multi Period Dynamic ZigZag Wave Timing System" (Zig Zag + Williams %R Strategy).

FMZ source id: 482419

Source
    https://www.fmz.com/strategy/482419 (PineScript v6, FMZ last modified 2025-02-18 13:29:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-207), zigzag depth 5, deviation 1 %; Williams %R 14, -20 / -80; stop 1 %, target 2 %; 300 % of equity
    pivothigh(5, 5) and dir != -1 and (no last high or high[5] > last high x 1.01) -> last high := high[5], dir := -1;  pivotlow mirror -> dir := 1
    dir == 1 and crossover(wr, -80) -> entry Long + exit(stop = close x 0.99, limit = close x 1.02);  dir == -1 and crossunder(wr, -20) -> entry Short + exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop follows the zigzag direction as written: a confirmed pivot high (strict, 5 bars each side)
      turns it down only from up or unset and only above the last pivot high by 1 %, a pivot low the
      mirror. The bracket is sent on each signal bar from its close: the opening signal's levels are
      ported, sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256); a repeat crossing inside a trade re-sends it, which is not followed (as
      #434428, mark trailing_stop_pending). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The 300 % of equity size is sizing.
      2-day bars are blocks of two broker days. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, zigzag direction with Williams %R re-entries and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 300 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482419_zigzag5_dev1_williams_r_cross_pct_bracket_reversal"
FAMILY = "support_resistance"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "depth": [5, 10],
    "deviation": [1.0, 3.0],
}
DEFAULT_PARAMS = {"depth": 5, "deviation": 1.0, "wr_length": 14, "sl_pct": 0.01, "tp_pct": 0.02, "days": 2}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow on the chart bars)."""
    v = np.asarray(x, dtype=float)
    m = len(v)
    out = np.zeros(m, dtype=bool)
    for t in range(2 * span, m):
        c = v[t - span]
        rest = np.concatenate([v[t - 2 * span:t - span], v[t - span + 1:t + 1]])
        if np.isnan(c) or np.isnan(rest).any():
            continue
        out[t] = (c > rest).all() if side > 0 else (c < rest).all()
    return out


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["depth"])
    ph, pl = _pivot(h, 1, k), _pivot(lo, -1, k)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    dev = float(p["deviation"]) / 100
    m = len(hv)
    zz = np.zeros(m)
    d, last_h, last_l = 0, np.nan, np.nan
    for t in range(m):
        if ph[t] and d != -1 and (np.isnan(last_h) or hv[t - k] > last_h * (1 + dev)):
            last_h, d = hv[t - k], -1
        if pl[t] and d != 1 and (np.isnan(last_l) or lv[t - k] < last_l * (1 - dev)):
            last_l, d = lv[t - k], 1
        zz[t] = d
    n = int(p["wr_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    wr = (hh - c) / (hh - ll).where(hh > ll) * -100
    zs = pd.Series(zz, index=c.index)
    le = (zs == 1) & (wr > -80) & (wr.shift(1) <= -80)
    se = (zs == -1) & (wr < -20) & (wr.shift(1) >= -20)
    sp, tp = float(p["sl_pct"]), float(p["tp_pct"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
