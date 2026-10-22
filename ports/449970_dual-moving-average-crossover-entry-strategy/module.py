"""Opens above the SMA 5 buy from flat, daily bars, long only; the first close at or above the fill price closes (the second scenario can never fire).
Port of FMZ strategy #449970 "Dual Moving Average Crossover Entry Strategy" (YBS Strategy 1.1).

FMZ source id: 449970

Source
    https://www.fmz.com/strategy/449970 (PineScript v5, FMZ last modified 2024-04-30 17:37:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-112), SMA 5; distance 0.002 (scenario 2); stop 0.1 % (scenario 2)
    open > sma5 and no open trade -> entry Buy Scenario 1;  open < sma5 and open - sma5 > 0.002 -> entry Buy Scenario 2 (never: contradictory)
    close >= avg -> close Buy Scenario 1;  close <= avg x 0.999 -> close Buy Scenario 2 (never entered)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second scenario needs the open under the SMA and above it at once, so it never fires, and
      its 0.1 % close names an id that is never entered. The remaining close is a bar-close test of
      the close against the fill price (the next open after the signal), filled at the next open; it
      is false while flat (the average price is na). Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exit is a close test against the fill.
    2 generic: PASS, open above the SMA 5 with a break-even-or-better close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449970_open_above_sma5_breakeven_close_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [5, 10],
}
DEFAULT_PARAMS = {"ma_len": 5}


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
    o, c = bars_df["open"], bars_df["close"]
    ma = c.rolling(int(p["ma_len"])).mean()
    go = (o > ma).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, fp = False, np.nan
    for i in range(m):
        if not held and go[i]:
            le[i] = True
            fp = ov[i + 1] if i + 1 < m else np.nan   # the fill: the next bar's open
        elif held and cv[i] >= fp:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
