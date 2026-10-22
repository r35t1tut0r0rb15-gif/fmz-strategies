"""RSI 14 and Bollinger 20 / 2 extremes filtered by the EMA 100 regime, 3-hour bars: an RSI under 30 with the close under the lower band while the EMA 100 is flat or over the EMA 50 goes long, the mirror goes short; reversing.
Port of FMZ strategy #471659 "Multi Technical Indicator Based Mean Reversion and Trend Following Strategy" (BTC Dominance Analysis Strategy (Improved)).

FMZ source id: 471659

Source
    https://www.fmz.com/strategy/471659 (PineScript v5, FMZ last modified 2024-11-12 10:44:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-155), RSI 14, levels 30 / 70; BB 20, 2 sd; EMA 100 / 50 (EMA 30 unused); flat = |EMA 100 - SMA 10 of it| < its 10-bar sd
    rsi < 30 and close < lower and (flat or ema100 > ema50) -> entry Buy;  rsi > 70 and close > upper and (flat or ema100 < ema50) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script is written for a BTC-dominance chart but uses only the chart's own prices; the rules
      are generic. The tests are states: repeated entries while held do nothing. There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the
      backtest header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and band extremes with an EMA regime filter.
    3 crypto-exchange-only: no (exchange pair in the header only (BTC dominance named in the title)).
    4 signals only: no sizing code.
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

NAME = "fmz_471659_rsi_bb_extreme_ema100_regime_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_period": [20, 50],
    "rsi_period": [14, 7],
}
DEFAULT_PARAMS = {"bb_period": 20, "rsi_period": 14, "bb_std": 2.0}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_period"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_std"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_period"]))
    e100, e50 = c.ewm(span=100, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    flat = (e100 - e100.rolling(10).mean()).abs() < e100.rolling(10).std(ddof=0)
    le = (r < 30) & (c < basis - dev) & (flat | (e100 > e50))
    se = (r > 70) & (c > basis + dev) & (flat | (e100 < e50))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
