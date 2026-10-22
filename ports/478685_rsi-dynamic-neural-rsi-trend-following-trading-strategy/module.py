"""RSI 14 dips under 40 above the SMA 200, 15-minute bars, long only: such a bar buys, at least 10 days after the last exit; a close under a 5 % close-based ratchet or under the SMA 200 closes.
Port of FMZ strategy #478685 "动态神经网络RSI趋势跟踪交易策略-Dynamic-Neural-RSI-Trend-Following-Trading-Strategy" (200 SMA Crossover Strategy).

FMZ source id: 478685

Source
    https://www.fmz.com/strategy/478685 (PineScript v5, FMZ last modified 2025-01-17 14:19:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-152), SMA 200; RSI 14 under 40; trailing 5 % of the close (ratchet); waiting period 10 days
    close > sma200 and rsi < 40 and 10 days since the last exit and not isLong -> entry Buy, trail := na, isLong := true
    isLong -> trail := max(trail, close x 0.95);  isLong and (close < trail or close < sma200) -> close Buy, lastExit := time, isLong := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ratchet and closes are bar-close tests on the close (not broker stops), filled at the next
      open, so a loop follows the script's flag, ratchet and waiting time (bar open times, in days) as
      written. Long only. No sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI dips in an SMA 200 up-trend with a close ratchet and a cool-down.
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

NAME = "fmz_478685_sma200_up_rsi40_dip_close_ratchet_cooldown_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_pct": [5.0, 2.0],
    "waiting_days": [10, 2],
}
DEFAULT_PARAMS = {"trail_pct": 5.0, "waiting_days": 10, "sma_length": 200, "rsi_length": 14, "rsi_threshold": 40.0}


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
    sma = c.rolling(int(p["sma_length"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    base = ((c > sma) & (r < float(p["rsi_threshold"]))).to_numpy()
    below = (c < sma).to_numpy()
    cv = c.to_numpy(dtype=float)
    t = bars_df.index.tz_convert("UTC")
    days = np.asarray((t - pd.Timestamp("1970-01-01", tz="UTC")) / pd.Timedelta(days=1), dtype=float)
    keep = 1 - float(p["trail_pct"]) / 100
    wait = float(p["waiting_days"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    is_long, last_exit, trail = False, np.nan, np.nan
    for i in range(m):
        can = np.isnan(last_exit) or days[i] - last_exit > wait
        if base[i] and can and not is_long:
            le[i], trail, is_long = True, np.nan, True
        if is_long:
            trail = cv[i] * keep if np.isnan(trail) else max(trail, cv[i] * keep)
        if is_long and (cv[i] < trail or below[i]):
            lx[i], last_exit, is_long = True, days[i], False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
