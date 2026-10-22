"""Pullbacks to the EMA 20 or 50 in an EMA 20 > 50 > SMA 200 up-trend, 5-minute bars, long only: a close within 1 % of either EMA, above the previous high, with RSI 14 over 40 buys, with a 10 % stop and 25 % target from the entry price.
Port of FMZ strategy #477946 "多均线交叉趋势跟踪RSI波动策略-Multi-Moving-Average-Cross-Trend-Following-RSI-Oscillation-Strategy" (EMA/SMA Strategy).

FMZ source id: 477946

Source
    https://www.fmz.com/strategy/477946 (PineScript v5, FMZ last modified 2025-01-10 15:15:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-139), EMA 20 / 50, SMA 200; RSI 14 over 40; target +25 %, stop -10 % of strategy.position_avg_price
    ema20 > ema50 and sma200 below both and close within 1 % of ema20 or ema50 and rsi > 40 and close > high[1] -> entry Long;  in a long: exit(limit = avg x 1.25), exit(stop = avg x 0.90)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two exits each close the whole position and are sent from the average price while it is held:
      scalar fractions of the entry fill, active from the fill (as #440797). The condition is a state and
      repeats; it is ignored while long. Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing
      code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price exits as fractions of the fill.
    2 generic: PASS, EMA pullbacks in an up-trend with a wide bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the target / stop fractions stored.
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

NAME = "fmz_477946_ema20_50_pullback_sma200_trend_pct_bracket_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_threshold": [40, 50],
    "near_pct": [0.01, 0.005],
}
DEFAULT_PARAMS = {"rsi_threshold": 40, "near_pct": 0.01, "tp_pct": 0.25, "sl_pct": 0.10, "rsi_length": 14}


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
    h, c = bars_df["high"], bars_df["close"]
    e20 = c.ewm(span=20, adjust=False).mean()
    e50 = c.ewm(span=50, adjust=False).mean()
    s200 = c.rolling(200).mean()
    r = _rsi(c, int(p["rsi_length"]))
    k = float(p["near_pct"])

    def near(e):
        return (c <= e * (1 + k)) & (c >= e * (1 - k))

    trend = (e20 > e50) & (s200 < e20) & (s200 < e50)
    le = (near(e20) | near(e50)) & (r > float(p["rsi_threshold"])) & trend & (c > h.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
