"""RSI 14 against Bollinger bands drawn on the RSI, 1-hour bars, long only: the RSI under its lower band (14, 2) and under 29 goes long; over its upper band and over 72 closes; a 3 % / 8 % bracket re-sent
every bar from the latest close is described and kept pending.
Port of FMZ strategy #442637 "RSI均线双金叉震荡策略RSI-Moving-Average-Double-Cross-Oscillation-Strategy" (RSI slowma Ismael).

FMZ source id: 442637

Source
    https://www.fmz.com/strategy/442637 (PineScript v5, FMZ last modified 2024-02-23 14:07:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-154), RSI 14; SMA 7 / 2 of the RSI; levels 72 / 29; BB 14 / 2 on the RSI; stop 3 %, target 8 %; 100 % of equity
    buy = (crossover(rsi, sma2(rsi)) and rsi < bbLower and rsi < 29) or (rsi < bbLower and rsi < 29) -> entry Buy;  sell = (...) or (rsi > bbUpper and rsi > 72) -> close Buy
    exit(Exit Long, Buy, stop = close (1 - 3 %), limit = close (1 + 8 %)) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each signal's second term contains its first, so the entries are the level tests alone. The
      bracket is re-sent on every bar from that bar's close, so its levels move after entry (a stop 3 %
      under and a target 8 % over the latest close, active for the next bar): stops() cannot express a
      level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). Pine's stdev is the population deviation. Long only. The 100 % of equity
      size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, RSI against its own bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442637_rsi_band_extreme_long_resent_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "bb_length": [14, 30],
}
DEFAULT_PARAMS = {"rsi_length": 14, "bb_length": 14, "bb_std": 2.0, "over_bought": 72, "over_sold": 29}


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
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["bb_length"])
    mid = r.rolling(n).mean()
    dev = float(p["bb_std"]) * r.rolling(n).std(ddof=0)
    le = (r < mid - dev) & (r < float(p["over_sold"]))
    lx = (r > mid + dev) & (r > float(p["over_bought"]))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
