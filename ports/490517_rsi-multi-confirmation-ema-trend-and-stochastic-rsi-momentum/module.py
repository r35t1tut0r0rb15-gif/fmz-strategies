"""EMA 11 / 50 crosses confirmed by the stochastic RSI, long only, 1-minute bars: EMA 11 crossing above EMA 50 with %K
above %D goes long; EMA 11 crossing below EMA 50 with %K below %D closes the long.
Port of FMZ strategy #490517 "多重确认变动平均趋势与随机RSI动量交易策略-Multi-Confirmation-EMA-Trend-and-Stochastic-RSI-Momentum-Trading-Strategy" (Haze EMA Signal).

FMZ source id: 490517

Source
    https://www.fmz.com/strategy/490517 (PineScript v6, FMZ last modified 2025-04-14 11:25:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 215-248), EMA 11 / 50, stochastic RSI 10 / 10, %K 15, %D 7
    rsi = RSI 10; stoch = stoch(rsi, rsi, rsi, 10); k = SMA 15 of stoch; d = SMA 7 of k
    buy = crossover(ema11, ema50) and k > d -> entry long;  sell = crossunder(ema11, ema50) and k < d -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch(rsi, rsi, rsi, 10) = 100 x (rsi - lowest 10) / (highest 10 - lowest 10), windows including the
      current bar; na when the range is 0.
    * A buy and a sell cannot fall on one bar. Long only. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and an oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_490517_ema_11_50_cross_stoch_rsi_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [11, 20],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 11, "slow": 50, "stoch_len": 10, "k_len": 15, "d_len": 7}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["stoch_len"])
    rsi = _rsi(c, n)
    lo, hi = rsi.rolling(n).min(), rsi.rolling(n).max()
    rng = hi - lo
    stoch = (100 * (rsi - lo) / rng).where(rng != 0)
    k = stoch.rolling(int(p["k_len"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    buy = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (k > d)).astype(bool)
    sell = ((ef < es) & (ef.shift(1) >= es.shift(1)) & (k < d)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
