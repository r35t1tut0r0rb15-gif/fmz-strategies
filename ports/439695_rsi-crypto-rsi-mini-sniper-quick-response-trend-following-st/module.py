"""RSI 14 extremes on the SMA 400 side, 1-hour bars: above the SMA 400 an RSI under 35 goes long and an RSI over 80 closes it; below it an RSI over 65 goes short and an RSI under 20 closes it; each trade has
a 2 % stop and a 5 % target; reversing.
Port of FMZ strategy #439695 "快速响应型加密货币RSI趋势跟踪策略Crypto-RSI-Mini-Sniper-Quick-Response-Trend-Following-Strategy" (Crypto RSI mini-Sniper [5min]).

FMZ source id: 439695

Source
    https://www.fmz.com/strategy/439695 (PineScript v5, FMZ last modified 2024-01-23 10:46:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 228-263), RSI 14, oversold 35, overbought 65; SMA 400; take profit 5 %, stop 2 %
    long = rsi < 35 and close > sma400 -> entry Long;  rsi > 80 and close > sma400 -> close Long;  exit(stop = avg x 0.98, limit = avg x 1.05)
    short = rsi > 65 and close < sma400 -> entry Short;  rsi < 20 and close < sma400 -> close Short;  exit(stop = avg x 1.02, limit = avg x 0.95)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fixed 2 % / 5 % of the average (fill) price, re-sent every bar at the same levels:
      the port starts it at the fill (sl_stop 0.02, tp_stop 0.05). A side's entry and its close cannot
      share a bar (RSI levels), nor can the two entries (SMA side). strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the fill.
    2 generic: PASS, RSI levels and an SMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent inputs stored.
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

NAME = "fmz_439695_rsi_mini_sniper_sma400_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.05, 0.03],
    "sl": [0.02, 0.01],
}
DEFAULT_PARAMS = {"tp": 0.05, "sl": 0.02, "rsi_len": 14, "oversold": 35, "overbought": 65, "sma_len": 400}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    s = c.rolling(int(p["sma_len"])).mean()
    above, below = c > s, c < s
    le = (r < float(p["oversold"])) & above
    lx = (r > 80) & above
    se = (r > float(p["overbought"])) & below
    sx = (r < 20) & below
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
