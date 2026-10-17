"""Close crossing the SuperTrend line in the EMA 200 trend with an RSI 50 filter and a 1.5 ATR stop / 3 ATR target,
3-hour bars: the close crossing above the SuperTrend (10, 3) line above EMA 200 with RSI 14 above 50 goes long; the
mirror goes short.
Port of FMZ strategy #484921 "多重指标趋势确认动态止盈止损交易策略-Multi-Indicator-Trend-Confirmation-Dynamic-Risk-Management-Trading-Strategy" (Super Trend with EMA, RSI & Signals).

FMZ source id: 484921

Source
    https://www.fmz.com/strategy/484921 (PineScript v6, FMZ last modified 2025-03-05 10:19:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 327-361), SuperTrend 10 / 3, EMA 200, RSI 14 > 50 (filter on), ATR 10 x 1.5,
target 2 x the stop distance
    buy = crossover(close, st) and close > ema200 and rsi > 50;  sell = crossunder(close, st) and close < ema200 and
    rsi < 50;  entry + exit(stop = close -+ 1.5 ATR, limit = close +- 3 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend line as ta.supertrend computes it. The bracket is fixed at the signal bar: sl_stop = atr_mult x
      ATR(10) / close, tp_stop = 2 x that, shifted one bar inside stops() and re-based on the fill (house rule).
    * A same-side signal while held re-places the bracket: mark trailing_stop_pending; the port keeps the entry's.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "3h" from the backtest
      header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, SuperTrend, EMA, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484921_close_cross_supertrend_bracket"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"atr_len": 10, "factor": 3.0, "ema_len": 200, "rsi_len": 14, "use_rsi": True, "atr_mult": 1.5,
                  "tp_ratio": 2.0}


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


def _pine_supertrend_line(bars_df, factor, n):
    """ta.supertrend's line (lower band in an up-trend, upper band in a down-trend); na before the ATR exists."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    st_out = np.full(m, np.nan)
    pu = pl = 0.0
    prev_st = np.nan
    for i in range(m):
        if np.isnan(atr[i]):
            pu = pl = 0.0
            continue
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        if i > 0:
            lw = lw if (lw > pl or c[i - 1] < pl) else pl
            up = up if (up < pu or c[i - 1] > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        prev_st = lw if d == -1 else up
        pu, pl = up, lw
        st_out[i] = prev_st
    return pd.Series(st_out, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    st = _pine_supertrend_line(bars_df, float(p["factor"]), int(p["atr_len"]))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    up = (c > st) & (c.shift(1) <= st.shift(1))
    dn = (c < st) & (c.shift(1) >= st.shift(1))
    rl, rs = (rsi > 50, rsi < 50) if p["use_rsi"] else (True, True)
    long_e = (up & (c > ema) & rl).astype(bool)
    short_e = (dn & (c < ema) & rs).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
