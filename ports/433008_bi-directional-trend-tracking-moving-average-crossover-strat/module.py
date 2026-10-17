"""Open / close ALMA crossover, broker days, long only (shorts are off by default): an ALMA 18 (offset 0.88, sigma 1) of
the closes and one of the opens are compared on the previous bar; when "close ALMA >= open ALMA" switches on a long
opens, when it switches off the long is closed.
Port of FMZ strategy #433008 "Bi Directional Trend Tracking Moving Average Crossover Strategy" (OCC Trend Combo 1 day BTC Moonflag).

FMZ source id: 433008

Source
    https://www.fmz.com/strategy/433008 (PineScript v4, FMZ last modified 2023-11-23 15:26:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 372-582), stratRes 1D on the 1D chart, ALMA 18 / 0.88 / sigma 1; longs on, shorts off; the ATR / correlation trend lines are plots only
    closeSeries = security(tickerid, '1D', alma(close, 18, 0.88, 1), lookahead_on);  openSeries = the same on open
    on each new 1D bar: thisBar = closeSeries[1] >= openSeries[1]; a change from the last value -> crossOver
    crossOver and thisBar -> entry long (after closing a short);  crossOver and not thisBar -> close long (shorts excluded)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MA resolution (1D) equals the chart's (1d header), so security(..., lookahead_on) returns
      the bar's own value: nothing from the future. Every daily bar is a "new bar", and the decision
      reads the previous bar ([1]), as written: one extra bar of delay before the engine's own lag.
    * The ATR trend, correlation trend and their combination only draw lines; the commented-out
      alternatives are not used. The date window is always true.
    * Pine alma(): m = offset x (len - 1), s = len / sigma, Gaussian weights with the newest value at
      the far end. The initial "last" state is false.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; same-resolution security.
    2 generic: PASS, a crossover of two moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433008_occ_alma_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "basis_len": [18, 36],
    "alma_offset": [0.88, 0.5],
}
DEFAULT_PARAMS = {"basis_len": 18, "alma_offset": 0.88, "alma_sigma": 1.0}


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


def _alma(x, n, offset, sigma):
    """Pine alma(x, n, offset, sigma): weights over the last n values, the newest at index n - 1."""
    m = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))
    w = w / w.sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, off, sg = int(p["basis_len"]), float(p["alma_offset"]), float(p["alma_sigma"])
    cs = _alma(bars_df["close"], n, off, sg)
    os_ = _alma(bars_df["open"], n, off, sg)
    this = (cs.shift(1) >= os_.shift(1)).to_numpy()
    m = len(this)
    tgt = np.zeros(m, dtype=np.int8)
    last, pos = False, 0
    for i in range(m):
        if this[i] != last:
            last = bool(this[i])
            pos = 1 if last else 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
