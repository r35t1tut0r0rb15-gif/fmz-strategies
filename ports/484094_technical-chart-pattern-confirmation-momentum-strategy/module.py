"""Five-bar swing and triangle patterns confirmed by a close beyond the previous bar, with a 1.5 ATR stop and a 3 ATR
target, broker days: a swing-top / swing-bottom / ascending-triangle pattern with the close above the previous high
goes long; a swing-top / descending-triangle / flag pattern with the close below the previous low goes short.
Port of FMZ strategy #484094 "技术图形确认型多周期动量策略-Technical-Chart-Pattern-Confirmation-Momentum-Strategy" (Chart Pattern Strategy - Full Set).

FMZ source id: 484094

Source
    https://www.fmz.com/strategy/484094 (PineScript v5, FMZ last modified 2025-02-28 09:50:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 224-277), ATR 14, stop 1.5 ATR, target 3 ATR
    headAndShoulders = doubleTop = high[1] above high[0], high[2], high[3], high[4] and high[0] < high[2], high[3]
    doubleBottom = the low mirror;  ascending = high[2] < high[1], low[2] > low[1], high[3] < high[2], low[3] > low[2]
    descending = high[2] > high[1], low[2] < low[1], high[3] < high[2], low[3] < low[2]
    flag = high[1] < high, low[1] > low, high[2] < high[1], low[2] < low[1]
    long = (headAndShoulders or doubleBottom or ascending) and close > high[1];  short = (doubleTop or descending or
    flag) and close < low[1];  entry + exit(stop = close -+ 1.5 ATR, limit = close +- 3 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pattern tests as written (the "head and shoulders" equals the double-top test and is used on the long side,
      as written). The bracket is fixed at the signal bar: sl_stop = sl_mult x ATR / close, tp_stop = 2 x that,
      shifted one bar inside stops() and re-based on the fill (house rule). A same-side signal while held re-places it:
      mark trailing_stop_pending; the port keeps the entry's bracket.
    * Both directions on one bar: the short, written last, wins. Entries reverse (REVERSAL INTENDED). Stop module:
      portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their first minute;
      FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, bar patterns and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484094_chart_pattern_set_bracket"
FAMILY = "chart_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 2.5],
    "atr_len": [14, 7],
}
DEFAULT_PARAMS = {"atr_len": 14, "sl_mult": 1.5, "tp_ratio": 2.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    h1, h2, h3, h4 = (h.shift(k) for k in (1, 2, 3, 4))
    l1, l2, l3, l4 = (lo.shift(k) for k in (1, 2, 3, 4))
    top = (h1 > h2) & (h1 > h) & (h1 > h3) & (h1 > h4) & (h < h2) & (h < h3)
    bot = (l1 < l2) & (l1 < lo) & (l1 < l3) & (l1 < l4) & (lo > l2) & (lo > l3)
    asc = (h2 < h1) & (l2 > l1) & (h3 < h2) & (l3 > l2)
    desc = (h2 > h1) & (l2 < l1) & (h3 < h2) & (l3 < l2)
    flag = (h1 < h) & (l1 > lo) & (h2 < h1) & (l2 < l1)
    short_e = ((top | desc | flag) & (c < l1)).astype(bool)
    long_e = ((top | bot | asc) & (c > h1) & ~short_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
