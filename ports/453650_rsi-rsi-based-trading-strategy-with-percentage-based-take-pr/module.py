"""RSI 14 dips, 1-hour bars, long only: the RSI crossing under 30 buys; a close 5 % under or 20 % over the latest signal close, or the RSI crossing over 70, sells.
Port of FMZ strategy #453650 "RSI基于百分比止盈止损的交易策略-RSI-based-Trading-Strategy-with-Percentage-based-Take-Profit-and-Stop-Loss" (RSI Strategy with Adjustable TP and SL).

FMZ source id: 453650

Source
    https://www.fmz.com/strategy/453650 (PineScript v5, FMZ last modified 2024-06-07 15:04:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-159), RSI 14, levels 30 / 70; stop 5 %, target 20 % of the signal close (close tests); 10 % of equity, commission 0.1 %
    crossunder(rsi, 30) -> levels from the close, entry Buy;  long and (close <= stop or close >= target) -> close Buy;  crossover(rsi, 70) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target are bar-close tests on the close against levels from the latest signal's
      close (reset by every signal, also while long), filled at the next open. The entry and the RSI
      exit cannot meet on one bar. Long only. The 10 % of equity and the commission are stored. FREQ
      = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop / target are close tests.
    2 generic: PASS, RSI dips with close-test exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing and commission stored.
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

NAME = "fmz_453650_rsi30_crossunder_close_test_bracket_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "sl_pct": [0.05, 0.02],
    "tp_pct": [0.20, 0.05],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sl_pct": 0.05, "tp_pct": 0.20, "os": 30.0, "ob": 70.0}


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
    r = _rsi(c, int(p["rsi_len"]))
    os_, ob = float(p["os"]), float(p["ob"])
    buy = ((r < os_) & (r.shift(1) >= os_)).to_numpy()
    rx = ((r > ob) & (r.shift(1) <= ob)).to_numpy()
    cv = c.to_numpy(dtype=float)
    sl, tp = float(p["sl_pct"]), float(p["tp_pct"])
    m = len(cv)
    lx = np.zeros(m, dtype=bool)
    ref = np.nan
    for i in range(m):
        if buy[i]:
            ref = cv[i]
        lx[i] = rx[i] or (not np.isnan(ref) and (cv[i] <= ref * (1 - sl) or cv[i] >= ref * (1 + tp)))
    ix = bars_df.index
    le = pd.Series(buy, index=ix)
    lxs = pd.Series(lx, index=ix) & ~le
    false = pd.Series(False, index=ix)
    return le, lxs, false, false.copy()


def portfolio_kwargs(**params):
    return {}
