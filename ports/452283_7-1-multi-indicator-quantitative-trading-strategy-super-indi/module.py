"""Three-hour bars: RSI 14 under 30 with the stochastic 14 under 20, the low under the lower Bollinger band (20, 2) and MACD under 0 (or the near-miss / extreme variants, or exactly four of those five tests) goes long with a 0.25 % stop and a 0.14 % target from the signal close; the mirror goes short; reversing.
Port of FMZ strategy #452283 "多指标量化交易策略-7合1超级指标策略-Multi-Indicator-Quantitative-Trading-Strategy-Super-Indicator-7-in-1-Strategy" (Super Indicator 7 in 1).

FMZ source id: 452283

Source
    https://www.fmz.com/strategy/452283 (PineScript v5, FMZ last modified 2024-05-23 18:20:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 99-190), BB 20 x 2; RSI 14; MACD 12 / 26 / 9; stochastic 14; volume SMA 1; TP 0.14 %, SL 0.25 %; hours 0 .. 24
    buy = min_buy_signal or buy_signal or max_buy_signal or buy_condition (exactly 4 of rsi < 30, stoch < 20, macd < 0, low < lower, volume >= sma(volume, 1)) -> entry Open Long, exit("TP/SL Long", limit = close x 1.0014, stop = close x 0.9975)
    sell mirror -> entry Open Short, exit("TP/SL Short", limit = close x 0.9986, stop = close x 1.0025)

Interpretation choices (Pine rules in SURVEY_README.md)
    * volume >= sma(volume, 1) is always true, so volume feeds nothing (held for volume, not used) and
      "exactly 4 of 5" means exactly three of the four price tests. The exits have no from_entry and are
      sent on the signal bars only, as levels from that close: ported as fractions of the fill for the
      side just entered, exact (1e-6 floor); an older exit of the other side left pending is not
      followed. The hour filter (0 .. 24) is always true. REVERSAL INTENDED. Cash order size is sizing.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark coarse_bar_stop. FREQ = "3h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tight bracket at the signal close as fractions of the fill.
    2 generic: PASS, oversold / overbought confluence counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): cash 10000 per order, capital 100, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (the 0 .. 24 hour filter is always true).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_452283_seven_in_one_extremes_count_tight_bracket_3h_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.0014, 0.005],
    "sl_pct": [0.0025, 0.01],
}
DEFAULT_PARAMS = {"tp_pct": 0.0014, "sl_pct": 0.0025}


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
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    sma20 = c.rolling(20).mean()
    dev = 2.0 * c.rolling(20).std(ddof=0)
    upper, lower = sma20 + dev, sma20 - dev
    r = _rsi(c, 14)
    hh, ll = h.rolling(14).max(), lo.rolling(14).min()
    st = 100 * (c - ll) / (hh - ll).where(hh != ll)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    vol_ok = v >= v.rolling(1).mean()
    mn_b = (r < 33) & (r > 30) & (st < 22) & (st > 20) & (lo < lower) & (macd < 0) & vol_ok
    mn_s = (r > 63) & (r < 70) & (st > 72) & (st < 80) & (h > upper) & (macd > 0) & vol_ok
    b = (r < 30) & (st < 20) & (lo < lower) & (macd < 0) & vol_ok
    s = (r > 70) & (st > 80) & (h > upper) & (macd > 0) & vol_ok
    mx_b = (r < 27) & (st < 18) & (lo < lower) & (macd < 0) & vol_ok
    mx_s = (r > 77) & (st > 80) & (h > upper) & (macd > 0) & vol_ok
    cnt_b = (r < 30).astype(int) + (st < 20).astype(int) + (macd < 0).astype(int) + (lo < lower).astype(int) + vol_ok.astype(int)
    cnt_s = (r > 70).astype(int) + (st > 80).astype(int) + (macd > 0).astype(int) + (h > upper).astype(int) + vol_ok.astype(int)
    buy = mn_b | b | mx_b | (cnt_b == 4)
    sell = mn_s | s | mx_s | (cnt_s == 4)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (buy & ~sell).astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    tp, sl = float(p["tp_pct"]), float(p["sl_pct"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl)).mask(sf, k * (1 + sl) - 1)
    tp_f = pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1).mask(sf, 1 - k * (1 - tp))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
