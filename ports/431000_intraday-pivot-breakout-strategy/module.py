"""Pivot breakouts with an EMA 150 side filter (The Bull Hartist), broker days, from flat: the high crossing above the last
confirmed pivot-high close (10 / 15 bars) with the close at or above the EMA 150 goes long, the low crossing below the
last pivot-low close with the close at or below it goes short; a 3.2 ATR stop from the signal close.
Port of FMZ strategy #431000 "Intraday Pivot Breakout Strategy" (PIVOT STRATEGY [5MIN TF]).

FMZ source id: 431000

Source
    https://www.fmz.com/strategy/431000 (PineScript v5, FMZ last modified 2023-11-03 16:35:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 171-264), pivots 10 / 15 on close, EMA 150, ATR 14 x 3.2
    upper_price = last pivothigh(close, 10, 15); long = crossover(high, upper_price + mintick) and flat and close >= ema150
    lower_price = last pivotlow(close, 10, 15); short = crossunder(low, lower_price - mintick) and flat and close <= ema150
    long: exit(stop = close - 3.2 ATR) every bar;  short: exit(stop = close + 3.2 ATR) every bar
    close_all when hour == 14 and minute == 55

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-issued every bar at the latest close -+ 3.2 ATR (a level that moves both ways,
      not a best-price trail): rule 2, mark trailing_stop_pending; the port fixes it at the signal
      bar's 3.2 ATR as a fraction of its close, shifted one bar.
    * The one-tick offset is dropped (crossover of the level itself). Pivots are strict (as #430840),
      their value the close at the pivot bar. The 14:55 close_all never fires on the header's daily
      bars (and time_cond is always true), so neither is ported. The strategy() line is commented out
      in the corpus copy: orders read as written (as #429505).
    * Entries only from flat ("flat" follows the house stop on bars). Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header (the title's 5-minute chart is not the header's).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (rule 2).
    2 generic: PASS, pivots, an EMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out 60-unit order size stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the source's 09:35-14:00 window and 14:55 close are inert on daily bars.
Opposite entries cannot occur.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431000_pivot_breakout_ema_filter"
FAMILY = "pivot_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rightbars": [15, 5],
    "atr_mult": [3.2, 2.0],
}
DEFAULT_PARAMS = {"leftbars": 10, "rightbars": 15, "ema_len": 150, "atr_len": 14, "atr_mult": 3.2}


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
    """True at bar t when bar t - rb is a strict pivot over lb bars before and rb bars after."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if high:
            out[t] = v > left.max() and v > right.max()
        else:
            out[t] = v < left.min() and v < right.min()
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    cv = c.to_numpy(dtype=float)
    lb, rb = int(p["leftbars"]), int(p["rightbars"])
    ph, pl = _pivots(cv, lb, rb, True), _pivots(cv, lb, rb, False)
    m = len(cv)
    up_lvl, dn_lvl = np.zeros(m), np.zeros(m)
    u = d = 0.0
    for t in range(m):
        if ph[t]:
            u = cv[t - rb]
        if pl[t]:
            d = cv[t - rb]
        up_lvl[t], dn_lvl[t] = u, d
    hv, lv, ov = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), o.to_numpy(dtype=float)
    xo = np.zeros(m, dtype=bool)
    xu = np.zeros(m, dtype=bool)
    xo[1:] = (hv[1:] > up_lvl[1:]) & (hv[:-1] <= up_lvl[:-1])
    xu[1:] = (lv[1:] < dn_lvl[1:]) & (lv[:-1] >= dn_lvl[:-1])
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    dist = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_mult"]) / c).to_numpy()
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr = np.full(m, np.nan)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house stop from the fill price
            e = ov[entry_i]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        if pos != 0 or np.isnan(dist[i]):
            continue
        if xo[i] and cv[i] >= ema[i]:
            le[i], pos, entry_i, s_ = True, 1, i + 1, dist[i]
            sl_arr[i] = s_
        elif xu[i] and cv[i] <= ema[i]:
            se[i], pos, entry_i, s_ = True, -1, i + 1, dist[i]
            sl_arr[i] = s_
    return le, se, sl_arr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_arr = _run(bars_df, p)[2]
    return {"sl_stop": pd.Series(sl_arr, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
