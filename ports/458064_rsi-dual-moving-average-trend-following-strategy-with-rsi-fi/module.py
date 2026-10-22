"""RSI 14 dips after 30 bars over the SMA 200, 5-minute bars, long only: an RSI under 30 with the close over the SMA 200 for at least 30 bars buys; a close 2 % over or 0.5 % under the reference close sells, where the reference is set only by a signal bar while the trade is already open.
Port of FMZ strategy #458064 "双均线趋势跟踪策略与RSI过滤器-Dual-Moving-Average-Trend-Following-Strategy-with-RSI-Filter" (SMA 200 with RSI Filter).

FMZ source id: 458064

Source
    https://www.fmz.com/strategy/458064 (PineScript v5, FMZ last modified 2024-07-29 16:45:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 202-264), SMA 200; 30 confirmation bars; RSI 14 under 30; target 2 %, stop 0.5 % of the reference close (close tests)
    close > sma200 and barssince(close <= sma200) >= 30 and rsi < 30 -> entry Long;  that and na(entryPrice) -> entryPrice = close;  no open trade -> entryPrice = na
    close >= entryPrice x 1.02 or close <= entryPrice x 0.995 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * entryPrice is set on a signal bar and reset on every bar without an open trade, so the signal
      bar that opens the trade (still flat at its close) clears it at once: the exit levels come from
      the first signal bar after the fill, and until one comes the trade has no exit, as written. The
      exits are bar-close tests filled at the next open, followed in a loop. Long only. No sizing code.
      FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exits are close tests.
    2 generic: PASS, RSI dips in a confirmed SMA uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458064_sma200_confirmed_rsi30_dip_late_ref_close_tests_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [200, 100],
    "confirm": [30, 12],
    "tp_pct": [0.02, 0.01],
}
DEFAULT_PARAMS = {"sma_len": 200, "confirm": 30, "tp_pct": 0.02, "sl_pct": 0.005, "rsi_len": 14}


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
    sma = c.rolling(int(p["sma_len"])).mean()
    above = (c > sma).to_numpy()
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    since = np.full(m, np.nan)
    last_off = -1
    for i in range(m):
        if not above[i]:
            last_off = i
        if last_off >= 0:
            since[i] = i - last_off
    conf = int(p["confirm"])
    with np.errstate(invalid="ignore"):
        go = above & (since >= conf) & (r < 30)
    tp, sl = float(p["tp_pct"]), float(p["sl_pct"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, ref = 0, 0, np.nan
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == 2:
            pos = 0
        pend = 0
        if go[i] and np.isnan(ref):
            ref = cv[i]
        if pos == 0:
            ref = np.nan                      # no open trade at this bar's close
        hit = not np.isnan(ref) and (cv[i] >= ref * (1 + tp) or cv[i] <= ref * (1 - sl))
        if go[i] and pos == 0:
            le[i], pend = True, 1
        if hit and pos == 1:
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
