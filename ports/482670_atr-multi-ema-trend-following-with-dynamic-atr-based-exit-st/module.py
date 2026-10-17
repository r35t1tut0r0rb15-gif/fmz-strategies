"""EMA 9 / 20 golden crosses above the EMA 50 with RSI 45-70 and the close more than 1.1 ATR from the EMA 50, at most
one signal a day, long only, with a 2.5 ATR stop and a 3.5 ATR target, hourly bars.
Port of FMZ strategy #482670 "基于多均线趋势和ATR动态止盈止损的加密货币交易策略-Multi-EMA-Trend-Following-with-Dynamic-ATR-Based-Exit-Strategy-for-Cryptocurrency-Trading" (Backtest Last 2880 Baars Filers and Exits).

FMZ source id: 482670

Source
    https://www.fmz.com/strategy/482670 (PineScript v6, FMZ last modified 2025-02-20 14:45:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 108-182), EMA 9 / 20 / 50, ATR 14, RSI 14
    buy = crossover(ema9, ema20) and 45 < rsi < 70 and close > ema50 and close > ema20 and |close - ema50| > 1.1 ATR
          and linreg(ema50, 5, 0) > -0.2 and bar_index > 10 and dailyTradeCount < 1
    sell mirrored (30 < rsi < 55, close below, linreg(ema50, 5, 0) < 0.2)
    each signal: entry with exit(limit = close +/- TP, stop = close -/+ SL), dailyTradeCount += 1 (reset on a new
    dayofweek); SL / TP = 2.5 / 3.5 ATR by default (3.0-3.2 / 3.5-5.0 ATR for five named FX tickers)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "slope" filters compare the linreg VALUE of the EMA 50 (a price) with -0.2 / 0.2: the buy filter always
      passes and the sell filter never does on any instrument priced above 0.2 (criterion 2, a price level): both
      dropped as inert (as #492009), so the port is long only.
    * The per-ticker SL / TP table is collapsed to GRID values (2.5 / 3.5 default, 3.0 / 4.0 the FX rows' middle);
      the module does not look symbols up.
    * Clock rule (check 9 / C6): the one-signal-a-day counter resets on a new UTC calendar day (dayofweek in the
      exchange zone; the header names no exchange, read as UTC). It counts signals, held or not.
    * The bracket is placed with the entry from the signal bar: SL / TP ATR / close, shifted one bar inside stops()
      and re-based on the fill (house rule). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, EMAs, RSI and ATR multiples (the price-level slope filters are inert and dropped).
    3 crypto-exchange-only: no (no exchange in the header).
    4 signals only: 2 % of equity and the 2 % risk sizing quoted; the bracket via stops(), in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used; one signal per UTC calendar day.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482670_ema9_20_cross_trend_distance_daily_one_atr_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.5, 3.0],
    "tp_mult": [3.5, 4.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "dist_mult": 1.1, "sl_mult": 2.5, "tp_mult": 3.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e9, e20, e50 = (c.ewm(span=n, adjust=False).mean() for n in (9, 20, 50))
    atr = _atr(bars_df, int(p["atr_len"]))
    rsi = _rsi(c, 14)
    cond = ((e9 > e20) & (e9.shift(1) <= e20.shift(1)) & (rsi > 45) & (rsi < 70) & (c > e50) & (c > e20)
            & ((c - e50).abs() > p["dist_mult"] * atr)).to_numpy()
    day = bars_df.index.normalize()
    m = len(c)
    le = np.zeros(m, dtype=bool)
    count, last_day = 0, None
    for i in range(m):
        if last_day is not None and day[i] != last_day:
            count = 0
        last_day = day[i]
        if cond[i] and i > 10 and count < 1:
            le[i], count = True, count + 1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
