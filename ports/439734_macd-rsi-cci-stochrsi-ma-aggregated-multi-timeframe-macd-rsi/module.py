"""MACD crossings confirmed by RSI, CCI, stochastic and the SMA 200, 1-minute bars: a MACD cross up with RSI under 70, CCI under 100, %K above its 3-bar average and the close above the SMA 200 goes long; the
mirror (RSI over 30, CCI over 0) goes short; reversing.
Port of FMZ strategy #439734 "聚合多时间帧MACD-RSI-CCI-StochRSI-MA线性交易策略Aggregated-Multi-timeframe-MACD-RSI-CCI-StochRSI-MA-Linear-Trading-Strategy" (MACD RSI CCI StochRSI MA Strategy).

FMZ source id: 439734

Source
    https://www.fmz.com/strategy/439734 (PineScript v4, FMZ last modified 2024-01-23 14:11:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-213), MACD 12 / 26 / 9; RSI 14 level 70; CCI 14 level 100; stochastic 14, D 3 (K input unused); SMA 200
    buy = crossover(macd, signal) and rsi < 70 and cci < 100 and stoch > sma(stoch, 3) and close > sma200;  sell = crossunder and rsi > 30 and cci > 0 and stoch < D and close < sma200
    entry Buy on buy;  close Buy on sell;  entry Sell on sell;  close Sell on buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short tests use 100 - level, so the CCI test is cci > 0, as written. The close of the long and
      the short entry share the sell bar: the position reverses (and the mirror on a buy bar), so the
      closes change nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings and oscillator filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG439734 (2 members, best partner #440297, Jaccard 0.819); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439734_macd_cross_rsi_cci_stoch_sma200"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_level": [70, 60],
    "ma_len": [200, 100],
}
DEFAULT_PARAMS = {"rsi_level": 70, "ma_len": 200, "fast": 12, "slow": 26, "signal": 9, "rsi_len": 14,
                  "cci_len": 14, "cci_level": 100, "stoch_len": 14, "stoch_d": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (c - ma) / (0.015 * dev)
    k = int(p["stoch_len"])
    ll, hh = lo.rolling(k).min(), h.rolling(k).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    sd = st.rolling(int(p["stoch_d"])).mean()
    s200 = c.rolling(int(p["ma_len"])).mean()
    rl, cl = float(p["rsi_level"]), float(p["cci_level"])
    buy = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r < rl) & (cci < cl) & (st > sd) & (c > s200)
    sell = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r > 100 - rl) & (cci > 100 - cl) & (st < sd)
            & (c < s200))
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
