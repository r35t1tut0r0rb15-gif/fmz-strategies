"""Hourly bars: after the day's first hour from 09:15 (exchange time, UTC for the header's venue), the close crossing over that hour's high on the same bar as a rising EMA 9 crossing over the session VWAP goes long; the mirror at the first-hour low goes short; each trade gets an ATR 14 stop and a 1 % target from its fill; reversing.
Port of FMZ strategy #484091 "量化交易突破策略首时段ATR止损与EMA斜率优化策略-Quantitative-Breakout-Strategy-First-Hour-ATR-Stop-Loss-with-EMA-Slope-Optimization" (FnO Intraday Strategy with ATR SL, EMA Slope & Signals).

FMZ source id: 484091

Source
    https://www.fmz.com/strategy/484091 (PineScript v5, FMZ last modified 2025-02-28 09:46:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 228-308), session start 09:15 (exchange time), first candle 60 minutes; EMA 9 and its slope; VWAP(hlc3); ATR 14 x 1; target 1 %; 10 % of equity
    firstHourHigh / Low = high / low of the bars with sessionStart <= time <= sessionStart + 60 min (reset on each new day);  firstHourComplete = time > sessionStart + 60 min
    longCondition = firstHourComplete and crossover(close, firstHourHigh) and crossover(ema9, vwap) and ema9 > ema9[1] -> entry Long;  short mirrored
    position_size > 0 -> exit(stop = avg - atr, limit = avg x 1.01) every bar;  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The clock rule uses the venue's time zone (Binance futures: UTC): on hourly bars only the 10:00
      bar's open lies in 09:15 .. 10:15, so the "first hour" is that bar's range and entries come from the
      11:00 bar on; days are UTC calendar days, as written. ta.vwap(hlc3) restarts each session: the house
      session is the broker day (17:00 America/New_York). The bracket is re-sent every bar from
      position_avg_price with the current ATR: ported as fixed at the fill, the stop from the signal bar's
      ATR and a 1 % target (the source's stop distance follows each bar's ATR and starts after the fill
      bar: trailing_stop_pending). REVERSAL INTENDED. 10 % of equity is sizing. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR / 1 % bracket from the fill.
    2 generic: PASS, opening-range breakouts confirmed by an EMA / VWAP crossing.
    3 crypto-exchange-only: no (exchange pair in the header only ("FnO" in the title)).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: first hour from 09:15 UTC (the venue's zone), UTC days; VWAP on the broker day.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484091_first_hour_breakout_ema_vwap_cross_atr_1pct_1h_reversal"
FAMILY = "opening_range"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.0, 2.0],
    "target": [0.01, 0.02],
}
DEFAULT_PARAMS = {"start_min": 555, "first_min": 60, "atr_mult": 1.0, "target": 0.01}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    ix = bars_df.index
    utc = ix.tz_convert("UTC")
    mins = (utc.hour * 60 + utc.minute).to_numpy()
    st, fm = int(p["start_min"]), int(p["first_min"])
    in_first = (mins >= st) & (mins <= st + fm)
    after = mins > st + fm
    uday = np.asarray(utc.normalize().tz_localize(None))
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    fh, fl = np.full(len(hn), np.nan), np.full(len(hn), np.nan)
    a = b = np.nan
    for i in range(len(hn)):
        if i > 0 and uday[i] != uday[i - 1]:
            a = b = np.nan                   # reset on each new (UTC) day
        if in_first[i]:
            a = hn[i] if np.isnan(a) else max(a, hn[i])
            b = ln[i] if np.isnan(b) else min(b, ln[i])
        fh[i], fl[i] = a, b
    fh, fl = pd.Series(fh, index=ix), pd.Series(fl, index=ix)
    e9 = c.ewm(span=9, adjust=False).mean()
    day = broker_day(ix)
    src = (h + lo + c) / 3
    vw = (src * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    slope = e9 - e9.shift(1)
    after = pd.Series(after, index=ix)
    buy = (after & (c > fh) & (c.shift(1) <= fh.shift(1)) & (e9 > vw) & (e9.shift(1) <= vw.shift(1)) & (slope > 0))
    sell = (after & (c < fl) & (c.shift(1) >= fl.shift(1)) & (e9 < vw) & (e9.shift(1) >= vw.shift(1)) & (slope < 0))
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o = bars_df["open"]
    d = (float(p["atr_mult"]) * _atr(bars_df, 14)).shift(1) / o
    entry = le.shift(1, fill_value=False) | se.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(entry, d)
    tp_f = pd.Series(np.nan, index=o.index).mask(entry, float(p["target"]))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
