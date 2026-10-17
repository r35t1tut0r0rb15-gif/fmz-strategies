"""Gaussian-smoothed detrended price oscillator (DraftVenture), broker days: the ALMA (50) of the DPO (EMA 50, 26 bars
back) crossing above its own value 25 bars earlier while below zero goes long; crossing below it, or below zero, closes
the long; the mirror rules trade shorts.
Port of FMZ strategy #431392 "Gaussian Detrended Reversion Trading Strategy" (Gaussian Detrended Reversion Strategy).

FMZ source id: 431392

Source
    https://www.fmz.com/strategy/431392 (PineScript v5, FMZ last modified 2023-11-07 15:01:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-164), DPO 50, ALMA 50 / 0.85 / 6, lag 25
    dpo = close - ema(close, 50)[26];  a = alma(dpo, 50, 0.85, 6);  lag = a[25]
    entryL = crossover(a, lag) and a < 0;  exitL = crossunder(a, lag) or crossunder(a, 0)
    entryS = crossunder(a, lag) and a > 0;  exitS = crossover(a, lag) or crossover(a, 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * barsback = 50 / 2 + 1 = 26 (integer input). ALMA as Pine's (Gaussian weights, offset 0.85,
      sigma 6, the newest bars weighted most).
    * Order of the source: entry long, close long, entry short, close short; a close acts on the
      position held at the bar's start and does not undo a reversal on the same bar.
      strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a smoothed detrended oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 15 % of equity stored in original_sizing.txt.
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

NAME = "fmz_431392_gaussian_dpo_reversion"
FAMILY = "zscore_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [50, 100],
    "lag": [25, 10],
}
DEFAULT_PARAMS = {"period": 50, "alma_len": 50, "lag": 25}


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


def _alma(x, n, offset=0.85, sigma=6.0):
    mm = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - mm) ** 2) / (2 * s * s))
    return x.rolling(n).apply(lambda a: (a * w).sum() / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["period"])
    dpo = c - c.ewm(span=n, adjust=False).mean().shift(n // 2 + 1)
    a = _alma(dpo, int(p["alma_len"]))
    lag = a.shift(int(p["lag"]))
    a1, l1 = a.shift(1), lag.shift(1)
    x_up = (a > lag) & (a1 <= l1)
    x_dn = (a < lag) & (a1 >= l1)
    z_up = (a > 0) & (a1 <= 0)
    z_dn = (a < 0) & (a1 >= 0)
    e_l = (x_up & (a < 0)).to_numpy()
    x_l = (x_dn | z_dn).to_numpy()
    e_s = (x_dn & (a > 0)).to_numpy()
    x_s = (x_up | z_up).to_numpy()
    m = len(e_l)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if e_l[i]:
            pos = 1
        if x_l[i] and start == 1 and pos == 1:
            pos = 0
        if e_s[i]:
            pos = -1
        if x_s[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
