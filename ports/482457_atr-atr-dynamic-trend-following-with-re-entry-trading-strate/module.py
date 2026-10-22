"""Closes crossing over an SMA 10 of highs plus a smoothed ATR band, broker days, long only: each entry gets a stop 2 bands under and a target 5 bands over the signal close, and no new entry is taken until a close reaches one of those levels.
Port of FMZ strategy #482457 "ATR动态趋势跟踪与重入场交易策略-ATR-Dynamic-Trend-Following-with-Re-entry-Trading-Strategy" (KON SET By Sai).

FMZ source id: 482457

Source
    https://www.fmz.com/strategy/482457 (PineScript v6, FMZ last modified 2025-02-18 15:11:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-171), length 10; band = sma(atr(200), 200) x 0.8; stop 2 bands, target (5 + 0) bands; max_bars 30 (display only)
    not inTrade and crossover(close, sma(high, 10) + band) -> entry Long + exit(stop = close - 2 band, limit = close + 5 band), inTrade := true
    inTrade and (close <= stopLoss or close >= targetPrice) -> inTrade := false, entryPrice := na;  not inTrade and close == entryPrice -> re-entry (as above)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's own inTrade flag, not the position, gates the entries: it is set on each entry and
      cleared only when a bar closes at or beyond the stop or the target, so after the bracket has closed
      the trade no new entry is taken until such a close (a loop). The re-entry needs close == entryPrice,
      which is na once the flag clears, so it never fires. The levels are fixed at the signal close and
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar late,
      as #458256). The short-side signal is plotted only. Long only. Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, ATR-banded SMA breakouts with a close-gated re-arm.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482457_sma10_high_atr_band_breakout_close_rearm_bracket_long"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [10, 20],
    "target_multiplier": [0, 2],
}
DEFAULT_PARAMS = {"length": 10, "target_multiplier": 0, "atr_length": 200, "band_mult": 0.8, "stop_bands": 2.0}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _signals(bars_df, p):
    h, c = bars_df["high"], bars_df["close"]
    n = int(p["atr_length"])
    band = _atr(bars_df, n).rolling(n).mean() * float(p["band_mult"])
    up_line = h.rolling(int(p["length"])).mean() + band
    sig = ((c > up_line) & (c.shift(1) <= up_line.shift(1))).to_numpy()
    sl_v = (c - band * float(p["stop_bands"])).to_numpy(dtype=float)
    tp_v = (c + band * (5 + float(p["target_multiplier"]))).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le = np.zeros(m, dtype=bool)
    l_sl, l_tp = np.full(m, np.nan), np.full(m, np.nan)
    in_trade, sl, tp = False, np.nan, np.nan
    for i in range(m):
        if not in_trade and sig[i]:
            le[i] = True
            sl, tp = sl_v[i], tp_v[i]
            l_sl[i], l_tp[i] = sl, tp
            in_trade = True
        if in_trade and (cv[i] <= sl or cv[i] >= tp):
            in_trade, sl, tp = False, np.nan, np.nan
    idx = c.index
    lvl = {"l_sl": pd.Series(l_sl, index=idx), "l_tp": pd.Series(l_tp, index=idx)}
    return pd.Series(le, index=idx), lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, lf & l_thr, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
