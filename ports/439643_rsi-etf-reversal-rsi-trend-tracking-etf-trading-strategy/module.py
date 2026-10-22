"""RSI 2 three-bar declines above the EMA 200, long only, 3-minute bars: with the close above the EMA 200, an RSI 2 that fell three bars in a row to under 10 (from under 60 three bars back) goes long; the RSI
crossing over 70 closes.
Port of FMZ strategy #439643 "反转向量RSI趋势跟踪ETF交易策略Reversal-RSI-Trend-Tracking-ETF-Trading-Strategy" (R3 ETF Strategy).

FMZ source id: 439643

Source
    https://www.fmz.com/strategy/439643 (PineScript v5, FMZ last modified 2024-01-22 17:15:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-156), RSI 2; today's max 10, 3-bar-ago max 60, exit 70; EMA 200; date range true
    Rule1 = close > ema 200;  Rule2 = rsi[3] < 60 and rsi < 10;  Rule3 = rsi < rsi[1] < rsi[2] < rsi[3];  entry Long when all;  close Long on crossover(rsi, 70)

Interpretation choices (Pine rules in SURVEY_README.md)
    * InDateRange is true. The entry and the close cannot share a bar. Long only. No sizing code. FREQ =
      "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI sequences and an EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_439643_r3_rsi2_three_bar_decline_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [2, 3],
    "exit_rsi": [70, 60],
}
DEFAULT_PARAMS = {"rsi_len": 2, "exit_rsi": 70, "today_min": 10, "day3_max": 60, "ema_len": 200}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r1, r2, r3 = r.shift(1), r.shift(2), r.shift(3)
    le = (c > e) & (r3 < float(p["day3_max"])) & (r < float(p["today_min"])) & (r < r1) & (r1 < r2) & (r2 < r3)
    x = float(p["exit_rsi"])
    lx = (r > x) & (r1 <= x)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
