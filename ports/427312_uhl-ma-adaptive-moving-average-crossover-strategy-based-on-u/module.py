"""Uhl MA crossover system, broker days: two variance-adaptive averages, a corrected trend step (CTS)
of the close and a corrected moving average (CMA) of SMA 100; CTS crossing above CMA goes long,
crossing below goes short (always in the market after the first cross).
Port of FMZ strategy #427312 "Adaptive Moving Average Crossover Strategy Based on Uhl MA".

FMZ source id: 427312

Source
    https://www.fmz.com/strategy/427312 (PineScript v4, FMZ last modified 2023-09-19 22:06:42).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 118-130), length 100, mult 1, source close
    Var = variance(close, 100); sma = sma(close, 100)
    ka = Var < (sma - cma[1])^2 ? 1 - Var / (sma - cma[1])^2 : 0; cma = ka sma + (1 - ka) cma[1]
    kb = Var < (close - cts[1])^2 ? 1 - Var / (close - cts[1])^2 : 0; cts = kb close + (1 - kb) cts[1]
    crossover(cts, cma) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * variance is the population variance over 100 bars ending at the bar (Pine's default, biased).
    * nz(cma[1], src) / nz(cts[1], src) seed both with the close; nz(sma - cma[1]) is 0 before cma
      exists (then ka = 0).
    * "mult" is declared but unused by the script. The equity plot lines are display only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the variance ratios are scale-free.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427312_uhl_ma_cross"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50, 200],
}
DEFAULT_PARAMS = {"length": 100}


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
    n = int({**DEFAULT_PARAMS, **params}["length"])
    c = bars_df["close"]
    var = c.rolling(n).var(ddof=0).to_numpy()
    sma = c.rolling(n).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    cma, cts = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        cma1 = cma[i - 1] if i else np.nan
        cts1 = cts[i - 1] if i else np.nan
        d_ma = sma[i] - cma1
        secma = (0.0 if np.isnan(d_ma) else d_ma) ** 2
        d_ts = cv[i] - cts1
        sects = (0.0 if np.isnan(d_ts) else d_ts) ** 2
        ka = 1 - var[i] / secma if var[i] < secma else 0.0
        kb = 1 - var[i] / sects if var[i] < sects else 0.0
        base_ma = cv[i] if np.isnan(cma1) else cma1
        base_ts = cv[i] if np.isnan(cts1) else cts1
        cma[i] = ka * sma[i] + (1 - ka) * base_ma if ka else base_ma
        cts[i] = kb * cv[i] + (1 - kb) * base_ts if kb else base_ts
    cma1 = np.concatenate(([np.nan], cma[:-1]))
    cts1 = np.concatenate(([np.nan], cts[:-1]))
    up = (cts > cma) & (cts1 <= cma1)
    dn = (cts < cma) & (cts1 >= cma1)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
