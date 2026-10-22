"""RSI dips in an uptrend, 1-hour bars, long only: the RSI 14 under 40 with the close above the SMA 170 goes long; a 5 % stop from the fill; the SMA 170 crossing under the SMA 90 with the RSI at 50 or
more closes.
Port of FMZ strategy #442551 "The Oscillating Breakthrough Strategy" (Crypto Sniper [15min] (ST Strategy)).

FMZ source id: 442551

Source
    https://www.fmz.com/strategy/442551 (PineScript v5, FMZ last modified 2024-02-22 17:15:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-172), SMA 90 / 170; RSI 14 (40); stop 5 %; pyramiding 1; 25 % of equity, capital 10000, commission 0.03
    rsi < 40 and close > sma170 -> entry Long;  exit(stop = avg (1 - 5 %)) every bar;  crossunder(sma170, sma90) and rsi >= 50 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent every bar from the average (fill) price; on the flat signal bar it is na, so it
      is ported active from the fill bar (#440797) as a fixed fraction 0.05 of the fill. The entry
      repeats while the condition holds and is refused at pyramiding 1. Long only. Stop module:
      portfolio_kwargs {} (driver D4). The percent-of-equity size, capital and commission are sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed from the fill.
    2 generic: PASS, RSI dip with an SMA trend filter; SMA cross exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_442551_rsi_dip_sma170_trend_pct_stop_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "over_sold": [40, 30],
    "sl_pct": [0.05, 0.03],
}
DEFAULT_PARAMS = {"over_sold": 40, "sl_pct": 0.05, "sma_fast": 90, "sma_slow": 170, "rsi_len": 14}


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
    r = _rsi(c, int(p["rsi_len"]))
    sf, ss = c.rolling(int(p["sma_fast"])).mean(), c.rolling(int(p["sma_slow"])).mean()
    go = ((r < float(p["over_sold"])) & (c > ss)).to_numpy()
    out = ((ss < sf) & (ss.shift(1) >= sf.shift(1)) & (r >= 50)).to_numpy()
    s_ = float(p["sl_pct"])
    ov, lv = bars_df["open"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and lv[i] <= ov[entry_i] * (1 - s_):
            pos = 0
        if pos == 1 and i >= entry_i and out[i]:
            lx[i], pos = True, 0
        elif pos == 0 and go[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
