"""Closes crossing above the 10-bar SMA of highs plus a smoothed ATR band go long with a 2-band stop and a 5-band
target; no new trade until a close passes either level, long only, daily bars.
Port of FMZ strategy #482457 "ATR动态趋势跟踪与重入场交易策略-ATR-Dynamic-Trend-Following-with-Re-entry-Trading-Strategy" (KON SET By Sai).

FMZ source id: 482457

Source
    https://www.fmz.com/strategy/482457 (PineScript v6, FMZ last modified 2025-02-18 15:11:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-156), length 10, band = sma(atr(200), 200) x 0.8, targets + 0
    signal_up = crossover(close, sma(high, 10) + band)
    not inTrade and signal_up -> stop = close - 2 band, target = close + 5 band, entry long with exit(stop, limit),
    inTrade := true
    inTrade and (close <= stop or close >= target) -> inTrade := false
    re-entry when not inTrade and close == entryPrice (entryPrice is na after an exit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The re-entry tests close == entryPrice, which is na after every exit: it never fires (inert). signal_down is
      only drawn.
    * The bracket is placed with the entry from the signal bar: 2 band / close and 5 band / close, shifted one bar
      inside stops() and re-based on the fill (house rule).
    * inTrade is cleared only by a CLOSE beyond the signal-close levels (as written); simulate() keeps that flag, so a
      broker stop hit inside a bar without such a close still blocks new entries until one comes.
    * Long only. Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, SMAs and a smoothed ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482457_sma_high_atr_band_break_bracket_long"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [10, 20],
    "tp_band": [5.0, 3.0],
}
DEFAULT_PARAMS = {"length": 10, "atr_len": 200, "band_mult": 0.8, "sl_band": 2.0, "tp_band": 5.0}


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


def _run(bars_df, p):
    h, c = bars_df["high"], bars_df["close"]
    band = _atr(bars_df, int(p["atr_len"])).rolling(int(p["atr_len"])).mean() * p["band_mult"]
    up_line = h.rolling(int(p["length"])).mean() + band
    sig = ((c > up_line) & (c.shift(1) <= up_line.shift(1))).to_numpy()
    cv, bv = c.to_numpy(dtype=float), band.to_numpy()
    m = len(cv)
    le = np.zeros(m, dtype=bool)
    sl, tp = np.full(m, np.nan), np.full(m, np.nan)
    in_trade, stop, target = False, np.nan, np.nan
    for i in range(m):
        if not in_trade and sig[i] and i + 1 < m:
            stop, target = cv[i] - p["sl_band"] * bv[i], cv[i] + p["tp_band"] * bv[i]
            le[i], sl[i], tp[i], in_trade = True, p["sl_band"] * bv[i] / cv[i], p["tp_band"] * bv[i] / cv[i], True
        if in_trade and (cv[i] <= stop or cv[i] >= target):
            in_trade = False
    return le, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl, tp = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl, index=idx).shift(1), "tp_stop": pd.Series(tp, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
