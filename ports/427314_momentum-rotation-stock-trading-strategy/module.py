"""Stochastic RSI breakout with a stop and a trailing stop: the stochastic of RSI 14 (K = SMA 3)
crossing up through 80 goes long, crossing down through 20 goes short (each reverses the other side);
each position has a fixed stop and a trailing stop that starts once the trade is far enough in profit.
Port of FMZ strategy #427314 "Momentum Rotation Stock Trading Strategy".

FMZ source id: 427314

Source
    https://www.fmz.com/strategy/427314 (PineScript v4, FMZ last modified 2023-09-19 22:14:24).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 158-362), pyramiding 1, SL 80 "pips", trail trigger 60, offset 60
    k = sma(stoch(rsi, rsi, rsi, 14), 3) of rsi(close, 14)
    goLong = k[1] < 80 and k >= 80; goShort = k[1] > 20 and k <= 20 (each while its unit count < 1)
    exit(loss = 800 ticks, trail_points = 600 ticks, trail_offset = 600 ticks) per side

Interpretation choices (Pine rules in SURVEY_README.md; skill 30-strategy-authoring section 7)
    * The close1..5 / far1..5 bookkeeping only re-counts open units for the pyramiding gate; with the
      default pyramiding 1 it means "enter from flat or from the other side": opposite signals
      reverse (REVERSAL INTENDED), the counts reset on a side change. Adds (pyramiding > 1) are sizing.
    * Criterion 2: the tick distances become ATR multiples (Wilder ATR 14): the stop sl_atr x ATR
      of the signal bar (shifted one bar inside stops(), re-based on the fill), and the trailing stop
      the house trail {"type": "volatility", "atr_n": 14, "k": trail_atr, "anchor": "high_low",
      "activate_after": activate} (Pine's trail follows the best high / low after trail_points of
      profit). Natively ported: mark trailing_stop. The activation is a fraction of the fill price
      (the house trail takes a fixed fraction, not an ATR multiple): declared in the grid.
    * Stop module: portfolio_kwargs {} (driver D4). Entries are emitted on their signal bars.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; stop and trail are house stops.
    2 generic: ADAPT, tick distances -> ATR multiples (activation as a price fraction).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding and the unit bookkeeping stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427314_stoch_rsi_breakout_trail"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [4.0, 2.0],
    "trail_atr": [3.0, 1.5],
    "activate": [0.003, 0.01],
}
DEFAULT_PARAMS = {"rsi_length": 14, "stoch_length": 14, "smooth_k": 3, "sl_atr": 4.0, "trail_atr": 3.0,
                  "activate": 0.003, "atr_length": 14}


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


def _rsi(close, n):
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return pd.Series(val, index=close.index)


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["rsi_length"]))
    n = int(p["stoch_length"])
    st = 100 * (r - r.rolling(n).min()) / (r.rolling(n).max() - r.rolling(n).min())
    k = st.rolling(int(p["smooth_k"])).mean()
    up = ((k.shift(1) < 80) & (k >= 80)).astype(bool)
    dn = ((k.shift(1) > 20) & (k <= 20)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false.copy(), dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = p["sl_atr"] * _atr(bars_df, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": frac.shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_length"]), "k": float(p["trail_atr"]),
                      "anchor": "high_low", "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
