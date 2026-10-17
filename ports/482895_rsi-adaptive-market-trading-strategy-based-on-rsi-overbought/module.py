"""RSI 14 extremes between 06:00 and 17:00 UTC with a 1 % stop / 2 % target, 1-minute bars: RSI below 30 inside the
window goes long; above 70 goes short.
Port of FMZ strategy #482895 "基于RSI超买超卖的自适应市场交易策略-Adaptive-Market-Trading-Strategy-Based-on-RSI-Overbought-Oversold" (Gold Trading RSI).

FMZ source id: 482895

Source
    https://www.fmz.com/strategy/482895 (PineScript v6, FMZ last modified 2025-02-27 17:28:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 88-123), RSI 14 (70 / 30), SL 1 %, TP 2 %
    window = 6 <= hour(time) < 17; long = window and rsi < 30; short = window and rsi > 70
    entry + exit(stop = close x (1 -+ 1 %), limit = close x (1 +- 2 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule (C6): hour(time) is the bar's open hour in the chart's zone, UTC on the author's Binance chart: entries
      06:00-16:59 UTC (no DST: UTC). "Gold" in the title is a label.
    * The bracket is placed with the entry from the signal close: 1 % / 2 % re-based on the fill (house rule). Every bar
      in the zone is a signal and re-places it while held: mark trailing_stop_pending; the port keeps the entry's
      bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, RSI and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (an entry window 06:00-17:00 UTC by bar open time, declared above).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482895_rsi_extremes_utc_window_pct_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 0.5],
    "tp_pct": [2.0, 1.0],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "sl_pct": 1.0, "tp_pct": 2.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    hr = bars_df.index.tz_convert(p["session_tz"]).hour
    window = pd.Series((hr >= 6) & (hr < 17), index=c.index)
    long_e = (window & (rsi < p["rsi_os"])).astype(bool)
    short_e = (window & (rsi > p["rsi_ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
