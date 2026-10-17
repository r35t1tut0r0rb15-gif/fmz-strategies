"""Open / close moving-average crosses on a three-times-higher timeframe, always in, daily bars: the SMA 8 of the
three-day closes crossing above the SMA 8 of the three-day opens goes long, below goes short.
Port of FMZ strategy #482785 "移动均线趋势向量量化交易策略-Moving-Average-Trend-Direction-Quantitative-Strategy-with-Cross-Validation" (Open Close Cross Strategy v6).

FMZ source id: 482785

Source
    https://www.fmz.com/strategy/482785 (PineScript v6, FMZ last modified 2025-02-27 17:49:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 90-191), alternate resolution x 3 (3D on the 1D chart), basis "SMMA"
(= ta.sma in this script), length 8, stops 0 (off)
    closeSeries = sma(close, 8), openSeries = sma(open, 8), both requested on the 3D resolution with
    lookahead_on; crossover(closeAlt, openAlt) -> close a short, entry long; crossunder -> close a long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(..., lookahead_on) on a higher timeframe hands each daily bar the 3D bar's FINAL values (a
      look-ahead on history). House rule (#490787): the last COMPLETED 3D bar's values only, i.e. a 3D block's SMAs
      are used from the first daily bar of the next block. Three-day blocks are broker-day dates from 1970-01-01
      (decision owed, as #426509).
    * The "SMMA" option is ta.sma here (as written). use_res = False (the chart's own bars) is a GRID variant.
    * lastPositionType alternates with the crosses, so every cross reverses (REVERSAL INTENDED); always in. The
      initial SL / TP points are 0 (off). The 10000-bar window (timenow) covers all daily history.
    * Signal module, no stops. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the higher timeframe without look-ahead.
    2 generic: PASS, SMAs of opens and closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone), three-day blocks for the higher timeframe; no
venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482785_open_close_sma_cross_htf3_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "use_res": [True, False],
    "basis_len": [8, 14],
}
DEFAULT_PARAMS = {"use_res": True, "int_res": 3, "basis_len": 8}


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


def _series(bars_df, p):
    n = int(p["basis_len"])
    if not p["use_res"]:
        return bars_df["close"].rolling(n).mean(), bars_df["open"].rolling(n).mean()
    k = int(p["int_res"])
    key = np.asarray((broker_day(bars_df.index) - pd.Timestamp("1970-01-01")).days // k)
    g = bars_df.assign(_key=key).groupby("_key", sort=True).agg(open=("open", "first"), close=("close", "last"))
    cs, os_ = g["close"].rolling(n).mean(), g["open"].rolling(n).mean()
    # each daily bar sees the last 3D block completed BEFORE its own block (no look-ahead)
    pos = np.searchsorted(g.index.to_numpy(), key, side="left") - 1
    ok = pos >= 0
    c_alt, o_alt = np.full(len(key), np.nan), np.full(len(key), np.nan)
    c_alt[ok], o_alt[ok] = cs.to_numpy()[pos[ok]], os_.to_numpy()[pos[ok]]
    return pd.Series(c_alt, index=bars_df.index), pd.Series(o_alt, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ca, oa = _series(bars_df, p)
    long_e = ((ca > oa) & (ca.shift(1) <= oa.shift(1))).astype(bool)
    short_e = ((ca < oa) & (ca.shift(1) >= oa.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
