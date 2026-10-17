"""RSI 14 leaving oversold (overbought) on the SMA 200 side, with reversals, 1-minute bars: RSI crossing above 30 with
the close above SMA 200 closes a short and goes long; RSI crossing below 70 with the close below SMA 200 closes a long
and goes short.
Port of FMZ strategy #483112 "基于RSI和趋势均线的双重过滤交易策略-RSI-and-Trend-MA-Dual-Filter-Trading-Strategy" (Leading Indicator Strategy - Daily Signals).

FMZ source id: 483112

Source
    https://www.fmz.com/strategy/483112 (PineScript v5, FMZ last modified 2025-02-21 14:05:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 121-145), RSI 14 (30 / 70), SMA 200 trend filter on
    bull = crossover(rsi, 30) and (not filter or close > sma200) -> close short, entry long
    bear = crossunder(rsi, 70) and (not filter or close < sma200) -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * close + entry is a reversal: only the entries are emitted (REVERSAL INTENDED). No stops.
    * The trend filter switch is a GRID variant. "Daily Signals" in the title is a label: FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483112_rsi_exit_extreme_sma200_reversal"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "use_trend_filter": [True, False],
    "ma_len": [200, 100],
}
DEFAULT_PARAMS = {"rsi_len": 14, "oversold": 30.0, "overbought": 70.0, "ma_len": 200, "use_trend_filter": True}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    ma = c.rolling(int(p["ma_len"])).mean()
    os_, ob = p["oversold"], p["overbought"]
    buy = (rsi > os_) & (rsi.shift(1) <= os_)
    sell = (rsi < ob) & (rsi.shift(1) >= ob)
    if p["use_trend_filter"]:
        buy, sell = buy & (c > ma), sell & (c < ma)
    false = pd.Series(False, index=bars_df.index)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
