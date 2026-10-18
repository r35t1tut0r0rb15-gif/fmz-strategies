"""Previous daily HLC3 against a Kaufman adaptive average, broker days: the previous bar's HLC3 crossing over the EMA 20 of the Kaufman average
of HLC3 goes long; crossing under goes short (reversing).
Port of FMZ strategy #435897 "Heikin-Ashi与考夫曼自适应移动平均线交易策略Heikin-Ashi-and-Kaufman-Adaptive-Moving-Average-Trading-Strategy" (HLC3/Kaufman Strategy).

FMZ source id: 435897

Source
    https://www.fmz.com/strategy/435897 (PineScript v2, FMZ last modified 2023-12-19 15:51:30).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 137-177), Kaufman length 5, fast 2.5, slow 20; EMA 20 of the average; HLC3 of the daily bar shifted by 1
    nAMA = nz(nAMA[1]) + nsmooth (hlc3 - nz(nAMA[1])), efficiency ratio over 5 bars;  bfma = ema(security(tickerid, "D", hlc3)[1], 1);  bsma = ema(security(tickerid, period, nAMA), 20)
    crossover(bfma, bsma) -> entry long;  crossunder(bfma, bsma) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" read on the daily backtest chart is the chart's own HLC3, so the shifted copy is the
      previous bar's HLC3 (no look-ahead); the second request is at the chart resolution. The Kaufman
      average starts from zero (nz), as written. strategy.entry reverses: REVERSAL INTENDED. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435897_hlc3_kaufman_cross"
FAMILY = "adaptive_average"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
    "sloma": [20, 30],
}
DEFAULT_PARAMS = {"length": 5, "fastend": 2.5, "slowend": 20, "sloma": 20, "shift": 1}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    x = (h + lo + c) / 3
    n = int(p["length"])
    noise = x.diff().abs().rolling(n).sum()
    signal = (x - x.shift(n)).abs()
    with np.errstate(invalid="ignore", divide="ignore"):
        er = (signal / noise).where(noise != 0, 0.0)
    nf, ns = 2 / (float(p["fastend"]) + 1), 2 / (float(p["slowend"]) + 1)
    sm = ((er * (nf - ns) + ns) ** 2).to_numpy()
    xv = x.to_numpy(dtype=float)
    m = len(xv)
    ama = np.full(m, np.nan)
    for i in range(m):
        prev = ama[i - 1] if i > 0 and not np.isnan(ama[i - 1]) else 0.0     # nz(nAMA[1])
        ama[i] = prev + sm[i] * (xv[i] - prev)
    bsma = pd.Series(ama, index=c.index).ewm(span=int(p["sloma"]), adjust=False).mean()
    bfma = x.shift(int(p["shift"]))
    le = ((bfma > bsma) & (bfma.shift(1) <= bsma.shift(1))).fillna(False).astype(bool)
    se = ((bfma < bsma) & (bfma.shift(1) >= bsma.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
