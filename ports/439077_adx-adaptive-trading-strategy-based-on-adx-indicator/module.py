"""ADX between the DI lines, broker days: the ADX 14 under DI+ and over DI- with both gaps at least 10 goes long, the mirror (ADX over DI+, under DI-) goes short; reversing. The P/L table only displays.
Port of FMZ strategy #439077 "基于ADX指标的自适应交易策略Adaptive-Trading-Strategy-Based-on-ADX-Indicator" (Monthly Performance by Dr. Maurya).

FMZ source id: 439077

Source
    https://www.fmz.com/strategy/439077 (PineScript v5, FMZ last modified 2024-01-17 15:33:37).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 160-196), len 14; th 20 (unused); long / short difference 10; 15 contracts, commission 0.1 %
    DI+ / DI- / DX from the source's running sums (nz seeds), ADX = sma(DX, 14);  |DI+ - ADX| >= 10 and |DI- - ADX| >= 10 and DI- < ADX < DI+ -> entry Long;  the same gaps and DI+ < ADX < DI- -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DMI is the source's own Wilder-style running sums (the first bar's true range uses a 0
      previous close, as written), with the ADX as an SMA 14 of DX. th is unused. The monthly table only
      displays. strategy.entry reverses: REVERSAL INTENDED. The quantity and commission are sizing / costs.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX position against the DI lines.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 15-contract quantity and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG439077 (2 members, best partner #440455, Jaccard 0.958); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439077_adx_between_di_lines"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [14, 21],
    "diff": [10, 5],
}
DEFAULT_PARAMS = {"len": 14, "diff": 10.0}


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


def _source_dmi(hv, lv, cv, n):
    m = len(cv)
    h1 = np.concatenate(([0.0], hv[:-1]))
    l1 = np.concatenate(([0.0], lv[:-1]))
    c1 = np.concatenate(([0.0], cv[:-1]))
    tr = np.maximum(np.maximum(hv - lv, np.abs(hv - c1)), np.abs(lv - c1))
    dmp = np.where(hv - h1 > l1 - lv, np.maximum(hv - h1, 0), 0.0)
    dmm = np.where(l1 - lv > hv - h1, np.maximum(l1 - lv, 0), 0.0)
    s_tr = s_p = s_m = 0.0
    dip, dim, dx = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        s_tr = s_tr - s_tr / n + tr[i]
        s_p = s_p - s_p / n + dmp[i]
        s_m = s_m - s_m / n + dmm[i]
        with np.errstate(divide="ignore", invalid="ignore"):
            dip[i], dim[i] = s_p / s_tr * 100, s_m / s_tr * 100
            dx[i] = abs(dip[i] - dim[i]) / (dip[i] + dim[i]) * 100
    return dip, dim, dx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    n = int(p["len"])
    dip, dim, dx = _source_dmi(hv, lv, cv, n)
    adx = pd.Series(dx, index=bars_df.index).rolling(n).mean().to_numpy()
    g = float(p["diff"])
    d2, d3 = np.abs(dip - adx), np.abs(dim - adx)
    buy = (d2 >= g) & (d3 >= g) & (adx < dip) & (adx > dim)
    sell = (d2 >= g) & (d3 >= g) & (adx > dip) & (adx < dim)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
