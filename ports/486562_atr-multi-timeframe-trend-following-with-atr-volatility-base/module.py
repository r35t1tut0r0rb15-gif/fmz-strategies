"""EMA 9 / 21 crossings with the close beyond the fast EMA, RSI 14, the MACD side and the last 15-minute close against its SMA 50, hourly bars: a confirmed up-cross goes long, a confirmed down-cross goes short; reversing (the per-bar ATR bracket is pending).
Port of FMZ strategy #486562 "多时间框架趋势追踪与ATR波动率动态风险管理系统策略-Multi-Timeframe-Trend-Following-with-ATR-Volatility-Based-Dynamic-Risk-Management-System-Strategy" (Samstrategy).

FMZ source id: 486562

Source
    https://www.fmz.com/strategy/486562 (PineScript v5, FMZ last modified 2025-03-14 09:20:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-234), EMA 9 / 21; ATR 14; RSI 14; MACD 12 / 26 / 9; RR 3; security("15", close > sma(close, 50))
    crossover(ema9, ema21) and close > ema9 and rsi > 30 and macd > signal and htf -> entry Long
    crossunder(ema9, ema21) and close < ema9 and rsi < 70 and macd < signal and not htf -> entry Short
    long -> exit(limit = close + 3 atr, stop = close - 2 atr) re-sent every bar from the current close;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * "15" is a lower time frame than the hourly chart, requested without lookahead: each hour gets the
      test of its last 15-minute bar (as #436765), with the SMA 50 of 15-minute closes, built in
      precompute from the minutes.
    * The bracket is re-sent on every bar from that bar's close, so its levels follow the price: not
      ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite entry is the exit. An
      entry on the other side reverses (REVERSAL INTENDED). No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent close bracket pending.
    2 generic: PASS, EMA crossings with RSI / MACD / 15-minute trend filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_486562_ema9_21_cross_rsi_macd_15m_sma50_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [9, 5],
    "slow_length": [21, 50],
}
DEFAULT_PARAMS = {"fast_length": 9, "slow_length": 21, "rsi_length": 14, "htf_sma": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    q = _resample(raw_1m_df, "15min")
    test = (q["close"] > q["close"].rolling(int(p["htf_sma"])).mean()).astype(float)
    test[q["close"].rolling(int(p["htf_sma"])).mean().isna()] = np.nan
    last = test.groupby(q.index.floor(FREQ)).last()          # each hour's last 15-minute bar
    bars["htf_up"] = last.reindex(bars.index).to_numpy()
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    f, s = ema(p["fast_length"]), ema(p["slow_length"])
    r = _rsi(c, int(p["rsi_length"]))
    macd = ema(12) - ema(26)
    sig = macd.ewm(span=9, adjust=False).mean()
    htf = bars_df["htf_up"]
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (c > f) & (r > 30) & (macd > sig) & (htf == 1)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (c < f) & (r < 70) & (macd < sig) & (htf == 0)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
