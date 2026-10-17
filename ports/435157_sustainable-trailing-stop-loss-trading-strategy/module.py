"""Always-in trailing-stop template, broker days, as written: the entry conditions are the template's placeholders (always
true), so from flat a long opens at once with a stop 3 % under the signal close; once the close is more than 1 % above the
reference the stop ratchets up (about 4 % of the stop level under the close) and the reference moves to the stop; a close
at or under the stop closes the long, and a new long opens on the next flat bar.
Port of FMZ strategy #435157 "Sustainable Trailing Stop Loss Trading Strategy" (TRAILING STOP LOSS TO LONG AND SHORT).

FMZ source id: 435157

Source
    https://www.fmz.com/strategy/435157 (PineScript v4, FMZ last modified 2023-12-12 17:29:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 189-319), position type LONG; initial stop 3 %; placeholder conditions 1 == 1 (entry) and 1 != 1 (close)
    flat and entry (1 == 1) -> entry long at close, stop = close (1 - 3 %), reference = close;  open and close <= stop -> close
    pct = (close - ref) / ref x 100 > 1 -> stop = max(stop, ref (1 + (pct - 4) / 100)), ref = stop   (stopLossPercent is reset to -3 every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the script's own level tested on bar closes (strategy.close at the next open): a
      close-based exit, not a broker stop (no mark). An entry is not taken on the bar of an exit (the
      trade is still open when the bar is calculated). The placeholder conditions are ported as
      written (the template is meant to be combined with real signals: that version is owed).
    * The SHORT position type mirrors it (grid). The date window (2014 to 9999) is the author's:
      dropped. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ratchet on closes.
    2 generic: PASS, percent stops.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435157_always_in_ratchet_template"
FAMILY = "always_in_trailing_stop"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "side": ["LONG", "SHORT"],
    "init_sl": [3.0, 6.0],
}
DEFAULT_PARAMS = {"side": "LONG", "init_sl": 3.0}


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
    longside = str(p["side"]) == "LONG"
    base = -float(p["init_sl"]) if longside else float(p["init_sl"])
    cv = bars_df["close"].to_numpy(dtype=float)
    m = len(cv)
    ent, ext = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    is_open, pending, ref, stop = False, False, 0.0, 0.0
    for i in range(m):
        if pending:                                  # the entry order fills at this bar's open
            is_open, pending = True, False
        c = cv[i]
        crossed = (c <= stop) if longside else (c >= stop)
        if is_open and crossed:
            ref, stop = 0.0, 0.0
            ext[i] = True
            is_open = False                          # flat from the next open; no entry on this bar
        elif not is_open and not pending:
            ref = c
            stop = c + c * base / 100
            ent[i], pending = True, True
        if is_open and ref != 0:
            pct = (c - ref) / ref * 100
            if longside and pct > 1:
                stop = max(stop, ref + ref * (base + pct - 1.0) / 100)
                ref = stop
            elif not longside and pct < -1:
                stop = min(stop, ref + ref * (base + pct + 1.0) / 100)
                ref = stop
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    if longside:
        return pd.Series(ent, index=ix), pd.Series(ext, index=ix), false, false.copy()
    return false, false.copy(), pd.Series(ent, index=ix), pd.Series(ext, index=ix)


def portfolio_kwargs(**params):
    return {}
