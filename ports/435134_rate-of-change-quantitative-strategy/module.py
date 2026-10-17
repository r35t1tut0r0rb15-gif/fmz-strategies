"""ROC 365 zero crosses with a bubble short and stop-and-reverse, broker days: one bar after the 365-bar ROC crosses above
zero (and stays above) go long; one bar after it crosses below (and stays below), or when a bubble (ROC above 200 for a
week) breaks back under 200, go short; each trade has a 10 % stop, and after a stop-out the strategy re-enters at once in
the opposite direction of the trade just closed.
Port of FMZ strategy #435134 "Rate of Change Quantitative Strategy" (RATE OF CHANGE BACKTESTING).

FMZ source id: 435134

Source
    https://www.fmz.com/strategy/435134 (PineScript v5, FMZ last modified 2023-12-12 15:56:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 160-275), ROC 365, bubble 200; stop 10 % of the signal close; fixed-ratio money management (sizing); dates 2017-2024 (filter on in the code: true)
    crossover(roc, 0)[1] and roc > 0 and position <= 0 -> entry long, exit(stop = close (1 - 10 %));  crossunder(roc, 0)[1] and roc < 0 and position >= 0 -> entry short
    inBubble and crossunder(roc, 200) and roc[1..7] > 200 and position >= 0 -> entry short;  flat -> entry opposite to the last closed trade

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are set from the signal close: sl_stop 0.10 of the fill (re-based). "Flat" follows
      the house stop on bars, and the last closed trade (a stop-out or a reversal) sets the
      direction of the immediate re-entry; when several entries fall on one bar the last issued
      wins. The cash-order ladder is sizing. inRange is always true in the code.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry; re-entry tracked through the house stop.
    2 generic: PASS, rate-of-change levels and a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed-ratio cash orders and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435134_roc365_bubble_stop_reverse"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "roc_len": [365, 180],
    "sl_pct": [0.10, 0.05],
}
DEFAULT_PARAMS = {"roc_len": 365, "bubble": 200.0, "sl_pct": 0.10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    roc = (c / c.shift(int(p["roc_len"])) - 1) * 100
    bub = float(p["bubble"])
    r1 = roc.shift(1)
    xo0 = ((roc > 0) & (r1 <= 0)).shift(1, fill_value=False).to_numpy()
    xu0 = ((roc < 0) & (r1 >= 0)).shift(1, fill_value=False).to_numpy()
    xub = ((roc < bub) & (r1 >= bub)).to_numpy()
    week = pd.concat([roc.shift(k) > bub for k in range(1, 8)], axis=1).all(axis=1).to_numpy()
    rv = roc.to_numpy()
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    s_ = float(p["sl_pct"])
    m = len(rv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ei, last, in_b = 0, -1, 0, False
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pos != 0 and i >= ei:                      # the house stop from the fill price
                if (pos == 1 and lv[i] <= ov[ei] * (1 - s_)) or (pos == -1 and hv[i] >= ov[ei] * (1 + s_)):
                    last, pos = pos, 0
            if rv[i] > bub and not in_b:
                in_b = True
            if rv[i] < 0 and in_b:
                in_b = False
            new = pos
            if pos <= 0 and xo0[i] and rv[i] > 0:
                new = 1
            if pos >= 0 and ((xu0[i] and rv[i] < 0) or (in_b and xub[i] and week[i])):
                new = -1
            if pos == 0 and last != 0:
                new = -last                               # re-enter against the last closed trade
            if new != pos and new != 0:
                if pos != 0:
                    last = pos                            # the reversal closes the open trade
                le[i], se[i] = new == 1, new == -1
                ei = i + 1
                pos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
