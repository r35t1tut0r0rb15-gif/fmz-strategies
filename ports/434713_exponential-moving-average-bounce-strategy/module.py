"""EMA 20 bounces from flat, broker days: after a bar whose low was above the EMA, a bar dipping under it and closing above
it goes long, with a stop just under the 10-bar low and a target 1.2 times that distance; the mirror bounce from above
goes short with the stop just over the 10-bar high.
Port of FMZ strategy #434713 "Exponential Moving Average Bounce Strategy" (EMA Bounce).

FMZ source id: 434713

Source
    https://www.fmz.com/strategy/434713 (PineScript v4, FMZ last modified 2023-12-08 16:47:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 182-263), EMA 20; swing look back 10, SL increment 0.2 %, TP 1.2 R; direct reverse off, reverse off
    BullBounce = low[1] > ema[1] and low < ema and close > ema -> entry long when flat;  BearBounce = high[1] < ema[1] and high > ema and close < ema -> entry short when flat
    SL = lowest(10) (1 - 0.2 %) at the bar the position changed;  TP = avg + (avg - SL) 1.2;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script takes the swing level at the bar its position changes (the fill bar's close); the
      port takes it from the signal bar (the 10 bars up to it), as fractions of the signal close
      shifted one bar inside stops() (re-based on the fill): approximation stated. A signal whose
      stop is not beyond the close places no entry.
    * Entries only from flat (direct reversal off): "flat" follows the house bracket on bars.
      Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on daily
      bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (approximation stated).
    2 generic: PASS, average bounces and swing-based exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434713_ema_bounce_swing_bracket"
FAMILY = "ma_pullback"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [20, 50],
    "rr": [1.2, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 20, "swing": 10, "incr": 0.002, "rr": 1.2}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    bull = ((lo.shift(1) > e.shift(1)) & (lo < e) & (c > e)).to_numpy()
    bear = ((h.shift(1) < e.shift(1)) & (h > e) & (c < e)).to_numpy()
    n, inc, rr = int(p["swing"]), float(p["incr"]), float(p["rr"])
    ll = (lo.rolling(n).min() * (1 - inc)).to_numpy()
    hh = (h.rolling(n).max() * (1 + inc)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    with np.errstate(invalid="ignore"):
        l_sl, s_sl = (cv - ll) / cv, (hh - cv) / cv
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl, tp = np.full(m, np.nan), np.full(m, np.nan)
    pos, ei, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= ei:                          # the house bracket from the fill price
            e0 = ov[ei]
            if pos == 1 and (lv[i] <= e0 * (1 - s_) or hv[i] >= e0 * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + s_) or lv[i] <= e0 * (1 - t_)):
                pos = 0
        if pos == 0 and bull[i] and l_sl[i] > 0:
            le[i], pos, ei, s_, t_ = True, 1, i + 1, l_sl[i], l_sl[i] * rr
            sl[i], tp[i] = s_, t_
        elif pos == 0 and bear[i] and s_sl[i] > 0:
            se[i], pos, ei, s_, t_ = True, -1, i + 1, s_sl[i], s_sl[i] * rr
            sl[i], tp[i] = s_, t_
    return le, se, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _run(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
