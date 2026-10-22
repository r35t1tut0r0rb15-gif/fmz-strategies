"""Five-indicator reversal bars, hourly: RSI 14 under 30, MACD over its signal, Stochastic %K 14 under 20 and the close jumping from under the lower Bollinger 20 / 2 band to over its basis goes long; the mirror goes short; reversing, no other exit.
Port of FMZ strategy #482897 "Multi Technical Indicator Moving Average Crossover Trend Following Quantitative Trading Strategy" (TradingBot Strategy).

FMZ source id: 482897

Source
    https://www.fmz.com/strategy/482897 (PineScript v5, FMZ last modified 2025-02-20 16:56:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-185), SMA 14 (plot only); RSI 14; Bollinger 20 x 2; MACD 12 / 26 / 9; Stochastic %K 14 (raw), %D 3 (plot only); lot size 0.1; 1 % of equity
    rsi < 30 and macd > signal and k < 20 and close > bbMiddle and close[1] < bbLower -> entry Buy
    rsi > 70 and macd < signal and k > 80 and close < bbMiddle and close[1] > bbUpper -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * %K is the raw Stochastic (no smoothing), as written. Entries only: each reverses the other side
      (REVERSAL INTENDED), no other exit. The SMA, %D and labels are drawing only. The lot size 0.1 and
      the 1 % of equity default are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI / MACD / Stochastic / Bollinger confluence.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot size 0.1 and 1 % of equity stored, not ported.
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

NAME = "fmz_482897_rsi_macd_stoch_bb_lower_to_basis_jump_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_period": [20, 40],
    "rsi_period": [14, 7],
}
DEFAULT_PARAMS = {"bb_period": 20, "rsi_period": 14, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
                  "stoch_k": 14}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_period"]))
    n = int(p["bb_period"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = mid + 2 * sd, mid - 2 * sd

    def ema(x, k):
        return x.ewm(span=int(k), adjust=False).mean()

    macd = ema(c, p["macd_fast"]) - ema(c, p["macd_slow"])
    sig = ema(macd, p["macd_signal"])
    kk = int(p["stoch_k"])
    rng = h.rolling(kk).max() - lo.rolling(kk).min()
    k = 100 * (c - lo.rolling(kk).min()) / rng.where(rng > 0)
    le = (r < 30) & (macd > sig) & (k < 20) & (c > mid) & (c.shift(1) < dn.shift(1))
    se = (r > 70) & (macd < sig) & (k > 80) & (c < mid) & (c.shift(1) > up.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
