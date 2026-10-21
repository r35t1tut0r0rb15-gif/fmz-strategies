"""RSI 14 under 25 buys, 3-minute bars, long only. The 7 % / 3.5 % bracket from the average price is armed only by a repeated signal inside a trade and is not ported, so the port has no exit (one long held from
the first signal).
Port of FMZ strategy #437800 "基于RSI的多头趋势追踪策略RSI-Trend-Tracking-Long-Only-Strategy" (RSI BENI Long).

FMZ source id: 437800

Source
    https://www.fmz.com/strategy/437800 (PineScript v5, FMZ last modified 2024-01-05 16:19:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 145-172), RSI 14, level 25 (titled overbought); take profit 0.07, stop 0.035 of the average price
    rsi < 25 -> entry Long, exit(limit = avg price x 1.07, stop = avg price x 0.965)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is called only on a bar with the RSI under 25, with levels from the position's
      average price, which is na until the trade is open: the opening signal arms nothing, and the
      bracket appears only when the RSI is still under 25 on a later bar inside the trade. A stop that
      starts after entry cannot be expressed by stops(): the bracket is not ported (as #435169) and the
      module gets the mark trailing_stop_pending (the intended bracket is owed). Without it the port has
      no exit. Long only. No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket not ported (mark).
    2 generic: PASS, RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the percent bracket quoted in original_sizing.txt.
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

NAME = "fmz_437800_rsi_beni_long_entries"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "oversold": [25, 30],
}
DEFAULT_PARAMS = {"length": 14, "oversold": 25.0}


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
    r = _rsi(bars_df["close"], int(p["length"]))
    false = pd.Series(False, index=bars_df.index)
    return r < float(p["oversold"]), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
