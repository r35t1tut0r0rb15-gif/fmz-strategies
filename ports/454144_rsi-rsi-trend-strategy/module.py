"""RSI 9 dips from flat, 1-hour bars, long only: the RSI crossing under 30 buys with a 1 % stop from the signal close; the RSI crossing over 70 sells, and a trade older than 24 hours is closed.
Port of FMZ strategy #454144 "RSI趋势策略-RSI-Trend-Strategy" (Simple RSI Strategy).

FMZ source id: 454144

Source
    https://www.fmz.com/strategy/454144 (PineScript v5, FMZ last modified 2024-06-14 15:28:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-171), RSI 9, levels 30 / 70 (strategies 1 = 'achieved'); stop 1 %; max duration 24 h; order size 20 USDT, capital 20, commission 0.1 %
    flat and crossunder(rsi, 30) -> entry Long, exit(stop = close x 0.99);  long and crossover(rsi, 70) -> close Long
    long and (time - entry time) / 60000 > 1440 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is fixed on the signal bar from its close: ported as the fixed fraction 0.01 of the fill
      (as #437751). Entries only from flat, so the loop follows the stop on each bar's low. The
      duration test is a bar-close test on the bar's open time against the fill bar's open time
      (strictly over 24 hours), filled at the next open. The hard-coded start date is unused. Long only.
      Stop module: portfolio_kwargs {} (driver D4). The order size, capital and commission are stored.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop as a fixed fraction; the time exit as a close test.
    2 generic: PASS, RSI dips with RSI and time exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the order size, capital and commission stored.
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

NAME = "fmz_454144_rsi9_dip_from_flat_stop_time_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [9, 14],
    "sl_pct": [0.01, 0.03],
    "max_hours": [24, 48],
}
DEFAULT_PARAMS = {"rsi_len": 9, "sl_pct": 0.01, "max_hours": 24, "os": 30.0, "ob": 70.0}


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


def _run(bars_df, p):
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    os_, ob = float(p["os"]), float(p["ob"])
    buy = ((r < os_) & (r.shift(1) >= os_)).to_numpy()
    rx = ((r > ob) & (r.shift(1) <= ob)).to_numpy()
    sl = float(p["sl_pct"])
    maxd = pd.Timedelta(hours=float(p["max_hours"]))
    ov, lv = bars_df["open"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    tm = bars_df.index
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, fi = 0, 0, -1
    for i in range(m):
        if pend == 1:
            pos, fi = 1, i
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == 1 and lv[i] <= ov[fi] * (1 - sl):
            pos = 0                              # the stop order fills inside the bar
        if buy[i] and pos == 0 and i + 1 < m:
            le[i], pend = True, 1
        elif pos == 1 and (rx[i] or tm[i] - tm[fi] > maxd):
            lx[i], pend = True, 2
    return le, lx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
