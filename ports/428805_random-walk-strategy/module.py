"""Pseudo-random entries with a 3 % bracket, broker days: from flat, a fixed number sequence (a linear
congruential generator advanced one step per bar) decides long (value >= 500) or short; each trade has a
3 % stop and a 3 % target.
Port of FMZ strategy #428805 "Random Walk Strategy" (Random strategy).

FMZ source id: 428805

Source
    https://www.fmz.com/strategy/428805 (PineScript v3, FMZ last modified 2023-10-09 16:10:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 186-205), seed 200, a 16, c 10, m 1000, stop / target 30 (x 0.1 %)
    curRandom = curRandom[1] == 0 ? seed : (16 x curRandom[1] + 10) % 1000   (one step per bar)
    flat: curRandom >= 500 -> entry long, else entry short;
    exit(loss = close x 30 / 1000 / mintick, profit = close x 30 / 1000 / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "signal" is a deterministic sequence indexed by the bar number from the first bar of the
      data: the same data gives the same trades. It is a random-entry benchmark, ported as written.
    * The bracket is 3 % of the signal bar's close; the house sl_stop / tp_stop are 3 % of the fill
      price (the next open): stated approximation.
    * "Flat" follows the house bracket: the loop marks the position closed once a bar's high / low
      reaches the stop or target from the fill price. Opposite entries cannot occur (entries from flat).
    * The custom date switch defaults to false (dropped). Stop module: portfolio_kwargs {} (driver D4).
    * Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, percentages only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_428805_random_entry_bracket"
FAMILY = "stop_and_reverse_bracket"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "seed": [200, 777],
    "stop_loss": [30, 60],
}
DEFAULT_PARAMS = {"seed": 200, "stop_loss": 30, "take_profit": 30, "a": 16, "c": 10, "m": 1000}


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
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    a, cc, mm = int(p["a"]), int(p["c"]), int(p["m"])
    sl, tp = p["stop_loss"] / 1000, p["take_profit"] / 1000
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cur = 0
    pos, entry_i = 0, -1
    for i in range(m):
        cur = int(p["seed"]) if cur == 0 else (a * cur + cc) % mm
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - sl) or hv[i] >= e * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + sl) or lv[i] <= e * (1 - tp)):
                pos = 0
        if pos == 0:
            if cur >= mm / 2:
                le[i], pos = True, 1
            else:
                se[i], pos = True, -1
            entry_i = i + 1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_loss"]) / 1000, "tp_stop": float(p["take_profit"]) / 1000}


def portfolio_kwargs(**params):
    return {}
