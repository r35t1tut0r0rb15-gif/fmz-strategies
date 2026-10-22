"""Three-bar staircase counts, daily bars: the third bar in a row of higher lows goes long, the third bar in a row of lower highs goes short; reversing. Each trade has a 2-point stop and 6-point target from its signal close (fractions of 42000).
Port of FMZ strategy #473399 "Multi Wave Trend Following Price Analysis Strategy" (Indicatore Minimi e Massimi).

FMZ source id: 473399

Source
    https://www.fmz.com/strategy/473399 (PineScript v5, FMZ last modified 2024-11-29 16:40:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-132), stop 2 / target 6 in price from the signal close
    low > low[1] > low[2] -> countUp += 1, countDown := 0;  high < high[1] < high[2] -> countDown += 1, countUp := 0;  else both 0;  countUp == 3 -> entry Long, exit(limit = close + 6, stop = close - 2);  countDown == 3 -> entry Short, exit(limit = close - 6, stop = close + 2)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counts are a loop. The 2 / 6 are price amounts, ported as fractions of 42000 of the signal
      close (0.0000476 / 0.000143), sent as fractions of the fill open; a level at or through it is
      marketable and closed one bar late (as #458256). REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the price bracket as fractions of the signal close.
    2 generic: PASS, staircase counts with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the price bracket stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473399_three_higher_lows_lower_highs_point_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.0000476, 0.00476],
    "tp_frac": [0.000143, 0.0143],
}
DEFAULT_PARAMS = {"sl_frac": 0.0000476, "tp_frac": 0.000143}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    upb = ((lo > lo.shift(1)) & (lo.shift(1) > lo.shift(2))).to_numpy()
    dnb = ((h < h.shift(1)) & (h.shift(1) < h.shift(2))).to_numpy()
    m = len(c)
    cu, cd = np.zeros(m), np.zeros(m)
    u = d = 0
    for i in range(m):
        if upb[i]:
            u, d = u + 1, 0
        elif dnb[i]:
            d, u = d + 1, 0
        else:
            u = d = 0
        cu[i], cd[i] = u, d
    ix = bars_df.index
    le, se = pd.Series(cu == 3, index=ix), pd.Series(cd == 3, index=ix)
    ks, kt = float(p["sl_frac"]), float(p["tp_frac"])
    lvl = {"l_sl": c * (1 - ks), "l_tp": c * (1 + kt), "s_sl": c * (1 + ks), "s_tp": c * (1 - kt)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    lx = lf & l_thr & ~se
    sx = sf & s_thr & ~le
    return le, lx, se, sx


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
