"""HPotter's volatility-adjusted Finite Volume Elements (22-bar signed volume share, adaptive cutoff) against its EMA 40, broker days: above goes long, below goes short (held on a tie); reversing.
Port of FMZ strategy #429476 "Adaptive Volatility Finite Volume Elements Strategy" (Volatility Finite Volume Elements).

FMZ source id: 429476

Source
    https://www.fmz.com/strategy/429476 (PineScript v2, FMZ last modified 2023-10-17 14:50:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 143-179), samples 22, EMA 40, cutoffs 0.1 / 0.1; reverse off
    FveFactor = MF > CutOff x close ? 1 : MF < -CutOff x close ? -1 : 0, MF = close - hl2 + hlc3 - hlc3[1];  xFVE = 100 sum(volume x factor, 22) / sum(volume, 22)
    pos = xFVE > ema(xFVE, 40) ? 1 : < ? -1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The FVE half of #427517 on its own. stdev is Pine's population stdev; a bar with an undefined cutoff
      counts as factor 0. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, finite volume elements against its EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the FVE signed volume share; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429476_volatility_fve22_ema40_state_reversal"
FAMILY = "volume_index"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "samples": [22, 50],
    "perma": [40, 20],
}
DEFAULT_PARAMS = {"samples": 22, "perma": 40, "cintra": 0.1, "cinter": 0.1}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n, perma = int(p["samples"]), int(p["perma"])
    hlc3 = (h + lo + c) / 3
    intra = np.log(h) - np.log(lo)
    inter = np.log(hlc3) - np.log(hlc3.shift(1))
    vintra = intra.rolling(n).mean().rolling(n).std(ddof=0)
    vinter = inter.rolling(n).mean().rolling(n).std(ddof=0)
    cut = float(p["cintra"]) * vintra + float(p["cinter"]) * vinter
    mf = c - (h + lo) / 2 + hlc3 - hlc3.shift(1)
    fac = pd.Series(np.where(mf > cut * c, 1.0, np.where(mf < -cut * c, -1.0, 0.0)), index=c.index)
    xfve = (v * fac).rolling(n).sum() / v.rolling(n).sum() * 100
    ema = xfve.ewm(span=perma, adjust=False).mean()
    raw = np.where(xfve > ema, 1, np.where(xfve < ema, -1, 0))
    pos = np.zeros(len(raw), dtype=np.int8)
    q = 0
    for i in range(len(raw)):
        if raw[i] != 0:
            q = raw[i]
        pos[i] = q
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((pos == 1) & (prev != 1), index=ix), false,
            pd.Series((pos == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
