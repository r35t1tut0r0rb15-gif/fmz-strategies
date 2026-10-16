"""HPotter three line break, broker days: in an up trend a close above the last line extends the lines
and a close below the line three back flips the trend down; in a down trend the mirror. The trend
holds a long or a short (always in the market).
Port of FMZ strategy #427684 "Three Line Breakout Strategy".

FMZ source id: 427684

Source
    https://www.fmz.com/strategy/427684 (PineScript v3, FMZ last modified 2023-09-23 16:02:20).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-241)
    xu, xu1, xu2, xu3 = close each bar (not var), then shifted on a new line:
    up trend: close > xu[1] -> shift up (trend 1); close < xu3[1] -> lines to xu1[1], xu = close (trend -1)
    down trend: close > xu3[1] -> lines to xu1[1], xu = close (trend 1); close < xu[1] -> shift (trend -1)
    trend 1 -> entry long; -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: the line variables are not `var`, so on a bar with no new line they reset to the
      bar's close (the classic three-line break would keep them); the next bar compares with that
      close. Decision owed: the intended version keeps the lines.
    * xtrend[1] is na on the first bar, so the down-trend branch runs there.
    * "Trade reverse" fixed off. strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, closes only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427684_hpotter_three_line_break"
FAMILY = "price_action_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p_tr = 0                                       # 0 = na
    p_u = p_u1 = p_u2 = p_u3 = np.nan
    for i in range(m):
        x = c[i]
        u = u1 = u2 = u3 = x                       # not var: reset to the close every bar
        if p_tr == 1:
            if x > p_u:
                u3, u2, u1, u = p_u2, p_u1, p_u, x
                tr = 1
            elif x < p_u3:
                u3, u2, u1, u = p_u1, p_u1, p_u1, x
                tr = -1
            else:
                tr = 1
        else:
            if x > p_u3:
                u3, u2, u1, u = p_u1, p_u1, p_u1, x
                tr = 1
            elif x < p_u:
                u3, u2, u1, u = p_u2, p_u1, p_u, x
                tr = -1
            else:
                tr = -1
        tgt[i] = tr
        p_tr, p_u, p_u1, p_u2, p_u3 = tr, u, u1, u2, u3
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
