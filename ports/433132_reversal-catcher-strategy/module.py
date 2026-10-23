"""Hourly bars, trading only on bars opening before 15:00 UTC: in an EMA 21 / 50 downtrend, a higher-high higher-low bar closing back inside the Bollinger 20 x 1.5 bands after a bar wholly under the lower band, with the RSI 14 crossing over 30, goes long (the mirror in an uptrend goes short); the close beyond the target (band or basis) or the signal's stop (the previous bar's low / high) closes; everything closes from 15:00 UTC; reversing.
Port of FMZ strategy #433132 "Reversal Catcher Strategy" (Strategy:Reversal-Catcher).

FMZ source id: 433132

Source
    https://www.fmz.com/strategy/433132 (PineScript v5, FMZ last modified 2023-11-24 16:43:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 147-241), BB 20 x 1.5 of close; EMA 21 / 50; RSI 14, 70 / 30; trade type Both; end of day 1500; markets always on: off
    longCond = high[1] < BBlower[1] and BBlower < close < BBupper and (low > low[1] and high > high[1] and close > high[1]) and crossover(rsi, 30) and ema21 < ema50;  sl := low[1], target := high >= basis ? upper : basis
    hourVal < 1500: entries, then close "enter long" when close >= target or close <= sl (short mirror);  else close_all(immediately = true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour / minute of time('1') in the exchange's time zone are read as the bar's open time in UTC (the
      header exchange), so bars opening 00:00 to 14:00 UTC trade and later bars close everything. The stop
      and target are the script's own close-based levels, set on every signal bar (also a repeated one
      while in the position) and shared by both sides, as written. A close acts only on a position the
      bar's entries leave unchanged (call order). close_all(immediately = true) fills at the bar's close in
      the script; the port fills at the next bar's open (weird case, one minute later). ta.vwap only feeds a
      hidden plot: volume is not used. trade type Both is not read by any condition. REVERSAL INTENDED.
      qty = 1 unit is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop and target in the signals.
    2 generic: PASS, Bollinger re-entry reversals against the EMA trend with an end-of-day exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 1 unit, capital 100000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: trades on bars opening before 15:00 UTC (header exchange time); close_all from 15:00 UTC.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433132_bb_reentry_rsi_cross_counter_trend_eod_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [1.5, 2.0],
    "end_hour": [15, 20],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 1.5, "fast": 21, "slow": 50, "rsi_len": 14, "ob": 70.0, "os": 30.0,
                  "end_hour": 15}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    rsi = _rsi(c, int(p["rsi_len"]))
    ef, es = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    h1, l1 = h.shift(1), lo.shift(1)
    ob, os_ = float(p["ob"]), float(p["os"])
    hh = (lo > l1) & (h > h1) & (c > h1)
    ll = (lo < l1) & (h < h1) & (c < l1)
    long_c = ((h1 < lower.shift(1)) & (c > lower) & (c < upper) & hh
              & (rsi > os_) & (rsi.shift(1) <= os_) & (ef < es)).to_numpy()
    short_c = ((l1 > upper.shift(1)) & (c < upper) & (c > lower) & ll
               & (rsi < ob) & (rsi.shift(1) >= ob) & (ef > es)).to_numpy()
    ix = bars_df.index
    inwin = np.asarray(ix.hour * 100 + ix.minute < int(p["end_hour"]) * 100)
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    bv, uv, dv = basis.to_numpy(), upper.to_numpy(), lower.to_numpy()
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, sl, tg = 0, np.nan, np.nan
    for i in range(m):
        if not inwin[i]:
            if pos == 1:
                lx[i], pos = True, 0
            elif pos == -1:
                sx[i], pos = True, 0
            continue
        changed = False
        if long_c[i] and i > 0:
            if pos != 1:
                le[i], pos, changed = True, 1, True
            sl, tg = lv[i - 1], (uv[i] if hv[i] >= bv[i] else bv[i])
        if short_c[i] and i > 0:
            if pos != -1:
                se[i], pos, changed = True, -1, True
            sl, tg = hv[i - 1], (dv[i] if lv[i] <= bv[i] else bv[i])
        if changed:
            continue
        if pos == 1 and (cv[i] >= tg or cv[i] <= sl):
            lx[i], pos = True, 0
        elif pos == -1 and (cv[i] <= tg or cv[i] >= sl):
            sx[i], pos = True, 0
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
