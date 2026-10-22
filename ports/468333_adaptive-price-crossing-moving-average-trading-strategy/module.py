"""Close crossings of the Hull 104, daily bars: the close crossing over the Hull goes long, crossing under goes short, each with a 1.25-point stop and 37.5-point target from the signal close, at most one entry per side until the position is flat again; reversing.
Port of FMZ strategy #468333 "Adaptive Price Crossing Moving Average Trading Strategy" (SHIESTD).

FMZ source id: 468333

Source
    https://www.fmz.com/strategy/468333 (PineScript v5, FMZ last modified 2024-09-26 16:12:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-193), HMA 104 (WMA 52 / 104, WMA 10); stop 1.25, target 37.5 (price units); 2 contracts; long_open / short_open flags cleared when flat
    crossover(close, hma) and not long_open -> entry Long (qty 2) + exit(stop = close - 1.25, limit = close + 37.5), long_open
    crossunder(close, hma) and not short_open -> entry Short (qty 2) + exit(stop = close + 1.25, limit = close - 37.5), short_open
    no open trade at the bar's close -> long_open = short_open = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags are cleared on any bar that closes flat, including the signal bar itself (the order
      fills at the next open), so an entry is refused only when the same side was already entered
      while the current position stayed open, as written. The 1.25 / 37.5 are price amounts, ported as
      fractions of 42000 (0.0000298 / 0.000893 of the fill), and the bracket is followed in the loop so
      the flags line up. The 2-contract quantity is not ported. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point bracket as fractions of the fill.
    2 generic: PASS, Hull crossings with a point bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed 2-contract quantity stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_468333_close_cross_hull104_point_bracket_side_flags_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hma_length": [104, 55],
    "sl_frac": [0.0000298, 0.01],
    "tp_frac": [0.000893, 0.03],
}
DEFAULT_PARAMS = {"hma_length": 104, "sl_frac": 0.0000298, "tp_frac": 0.000893}


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


def _wma(x, n):
    n = int(n)
    out = pd.Series(0.0, index=x.index)
    for k in range(n):
        out = out + (n - k) * x.shift(k)
    return out / (n * (n + 1) / 2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["hma_length"])
    hma = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(np.floor(np.sqrt(n) + 0.5)))
    xo = ((c > hma) & (c.shift(1) <= hma.shift(1))).to_numpy()
    xu = ((c < hma) & (c.shift(1) >= hma.shift(1))).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    sl, tp = float(p["sl_frac"]), float(p["tp_frac"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, s_l, t_l = 0, 0, np.nan, np.nan
    l_open = s_open = False
    for i in range(m):
        if pend != 0:
            pos, pend = pend, 0
            s_l, t_l = ov[i] * (1 - pos * sl), ov[i] * (1 + pos * tp)
        if pos == 1 and (lv[i] <= s_l or hv[i] >= t_l):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= s_l or lv[i] <= t_l):
            pos = 0
        if xo[i] and not l_open:
            if pos != 1:
                le[i], pend = True, 1
            l_open = True
        if xu[i] and not s_open:
            if pos != -1:
                se[i], pend = True, -1
            s_open = True
        if pos == 0:
            l_open = s_open = False              # no open trade at this bar's close
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
