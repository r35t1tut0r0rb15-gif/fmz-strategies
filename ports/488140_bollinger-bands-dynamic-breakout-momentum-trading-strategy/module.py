"""Close crossings over the upper Bollinger band 20 / 1.9, broker days, long only: the cross goes long; four bars without a close over the upper band, or a low touching the basis, closes.
Port of FMZ strategy #488140 "Bollinger Bands Dynamic Breakout Momentum Trading Strategy" (Bollinger Bands Strategy 5m).

FMZ source id: 488140

Source
    https://www.fmz.com/strategy/488140 (PineScript v6, FMZ last modified 2025-03-25 14:10:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 231-285), BB 20 / 1.9; tolerance 4 bars; short side commented out
    crossover(close, upper) and position <= 0 -> entry Long
    long: close > upper ? count := 0 : count += 1;  count >= 4 or low <= basis -> close Long, count := 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counter is a var, kept between trades and reset only on a close, and it runs only while a long
      is held (from the bar after the entry signal, when it has filled); a loop follows it, as written.
      The short side is commented out. Long only. No sizing code. MPL 2.0 source (the notice is kept:
      Mozilla Public License 2.0, © GoodDayss). Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts with a stall-count and basis exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488140_bb20_19_upper_breakout_stall4_basis_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.9, 2.5],
    "tolerance": [4, 2],
}
DEFAULT_PARAMS = {"mult": 1.9, "tolerance": 4, "length": 20}


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
    lo, c = bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    upper = basis + float(p["mult"]) * c.rolling(n).std(ddof=0)
    cross = ((c > upper) & (c.shift(1) <= upper.shift(1))).to_numpy()
    cv, lv, uv, bv = c.to_numpy(dtype=float), lo.to_numpy(dtype=float), upper.to_numpy(), basis.to_numpy()
    tol = int(p["tolerance"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, cnt = 0, 0, 0
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == -1:
            pos = 0
        pend = 0
        if cross[i] and pos <= 0:
            le[i], pend = True, 1
        if pos > 0:
            cnt = 0 if cv[i] > uv[i] else cnt + 1
            if cnt >= tol or lv[i] <= bv[i]:
                lx[i], pend, cnt = True, -1, 0
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
