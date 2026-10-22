"""TSI and RSI agreement, 1-hour bars, long only: the TSI (25 / 5) above its EMA 14 signal with the RSI 5 above 50 goes long; the TSI below its signal with the RSI under 50 closes.
Port of FMZ strategy #440443 "真实相对运动MA均线策略True-Relative-Movement-Moving-Average-Strategy" (TKP-TRM Strategy).

FMZ source id: 440443

Source
    https://www.fmz.com/strategy/440443 (PineScript v4, FMZ last modified 2024-01-30 16:04:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-200), TSI long 25, short 5, signal 14; RSI 5; buy level 50, sell level 50
    tsi = 100 x ema(ema(change(close), 25), 5) / ema(ema(|change(close)|, 25), 5);  signal = ema(tsi, 14)
    TRM_Buy = tsi > signal and rsi > 50 -> entry Long;  TRM_Sell = tsi < signal and rsi < 50 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are levels and cannot hold together. Long only. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TSI and RSI levels.
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

NAME = "fmz_440443_tsi_rsi_trm_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tsi_short": [5, 13],
    "rsi_len": [5, 14],
}
DEFAULT_PARAMS = {"tsi_short": 5, "rsi_len": 5, "tsi_long": 25, "tsi_signal": 14, "buy_level": 50, "sell_level": 50}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    pc = c.diff()
    lg, sh = int(p["tsi_long"]), int(p["tsi_short"])
    num = pc.ewm(span=lg, adjust=False).mean().ewm(span=sh, adjust=False).mean()
    den = pc.abs().ewm(span=lg, adjust=False).mean().ewm(span=sh, adjust=False).mean()
    tsi = 100 * num / den.where(den != 0)
    sig = tsi.ewm(span=int(p["tsi_signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    buy = (tsi > sig) & (r > float(p["buy_level"]))
    sell = (tsi < sig) & (r < float(p["sell_level"]))
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
