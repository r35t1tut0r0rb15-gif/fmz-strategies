"""Three smoothed moving averages, broker days: a close above the SMMA 21 with the SMMA 7 above the SMMA 13 goes long; a
close below the SMMA 21 with the SMMA 7 below the SMMA 13 goes short; held otherwise and reversed on the opposite state.
Port of FMZ strategy #434478 "Multi Moving Average Crossover Trading Strategy" (CryptOli 3 MAs long/short Backtest).

FMZ source id: 434478

Source
    https://www.fmz.com/strategy/434478 (PineScript v4, FMZ last modified 2023-12-06 17:10:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 122-228), MA type SMMA (default), lengths 7 / 13 / 21 on close (Heikin-Ashi off; the src ohlc4 input feeds only the HA path); date range 2015-2030
    smma = na(smma[1]) ? sma(close, n) : (smma[1] (n - 1) + close) / n
    close > smma21 and smma7 > smma13 -> entry long;  close < smma21 and smma7 < smma13 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SMMA is seeded by the first valid SMA, then recursive. The other MA types and the
      Heikin-Ashi source are off. The date window (2015 to 2030) is the author's: dropped.
      strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity is sizing.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434478_three_smma_state"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [7, 5],
    "long_len": [21, 42],
}
DEFAULT_PARAMS = {"short_len": 7, "middle_len": 13, "long_len": 21}


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


def _smma(v, n):
    sma = pd.Series(v).rolling(n).mean().to_numpy()
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        if i > 0 and not np.isnan(out[i - 1]):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
        else:
            out[i] = sma[i]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    s, mi, lg = (_smma(cv, int(p[k])) for k in ("short_len", "middle_len", "long_len"))
    with np.errstate(invalid="ignore"):
        lc = (cv > lg) & (s > mi)
        sc = (cv < lg) & (s < mi)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        if sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
