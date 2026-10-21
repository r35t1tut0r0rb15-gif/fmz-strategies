"""EMA 20 / 50 crossings, broker days: the cross up goes long, the cross down goes short; reversing. The bracket from the latest close (1 % stop, 2 % target) closes every short at the open after its first bar;
the long's per-bar bracket is not ported (pending).
Port of FMZ strategy #438459 "Swing Trading Strategy with 20 50 EMA Cross" (EMA Cross).

FMZ source id: 438459

Source
    https://www.fmz.com/strategy/438459 (PineScript v5, FMZ last modified 2024-01-12 11:22:33).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 134-158), stop 1 %, reward ratio 2 (target 2 %); EMA 20 / 50
    crossover(ema 20, ema 50) -> entry Long;  crossunder -> entry Short;  every bar: exit(all entries, stop = close x 0.99, limit = close x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit has no from_entry, so it covers both sides, and it is re-sent on every bar from that bar's
      close. For a short, the buy stop 1 % UNDER the close and the buy limit 2 % over it both sit on the
      wrong side of the market, so the short is closed at the open after its first bar: the port closes
      it with an exit signal on the fill bar (exact). For a long, the stop and target move with each close
      (active for the next bar): stops() cannot express a level re-set every bar, so it is described and
      kept pending (as #437036, mark trailing_stop_pending); longs end at the opposite entry until then.
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the short's immediate exit as a signal.
    2 generic: PASS, EMA crossings; per-bar long bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_438459_ema20_50_cross_short_one_bar"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    m = len(c)
    le, se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    for i in range(m):
        if pend:                                         # the entry of the last bar fills at this open
            pos, pend = pend, 0
        if pos == -1 and not up[i]:
            sx[i], pos = True, 0                         # the wrong-side bracket closes it at the next open
        if up[i] and pos != 1 and i + 1 < m:
            le[i], pend = True, 1
        elif dn[i] and pos != -1 and i + 1 < m:
            se[i], pend = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
