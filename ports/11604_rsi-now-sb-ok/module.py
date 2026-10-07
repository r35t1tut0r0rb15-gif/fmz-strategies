"""RSI zone-cross reversal. Port of FMZ strategy #11604 "RSI_now_sb_ok".

Source
    https://www.fmz.com/strategy/11604 (JavaScript, author "tfboys", FMZ last modified
    2016-03-08 16:00:06). Verbatim copy: original_source.md in this folder. Read 2026-09-29.

Original signal (original_source.md lines 87-96 and 143-146)
    rsi = TA.RSI(records, RSIPeriod); rsiValue1 = rsi[len-2]; rsiValue2 = rsi[len-3]
    buy  when rsiValue1 >= RSIBuyL  and rsiValue2 <= RSIBuyH  and rsiValue1 > rsiValue2
    sell when rsiValue2 >= RSISellL and rsiValue1 <= RSISellH and rsiValue2 > rsiValue1
    Defaults: RSIPeriod 14, all four thresholds 50 (i.e. a cross of the 50 line).

Interpretation choices
    * records[len-1] is FMZ's forming bar, so rsiValue1 is the last COMPLETED bar. The port
      evaluates on completed bar t: rsi1 = rsi[t], rsi2 = rsi[t-1]. Current bar included.
    * State machine (lines 93-182): buy -> hold -> sell condition covers the long -> back to
      idle, where the same sell condition (unchanged until the next bar) opens a short (spot:
      sells the initial coins); symmetric on the buy side. Net behaviour is always-in-market
      reversal, so the port emits entries only. REVERSAL INTENDED: portfolio_kwargs is {} and
      the engine's default opposite-entry reversal applies.
    * The four thresholds are exposed through a declared `zone` parameter (see ZONES) so the
      grid stays coarse; DEFAULT is the original's 50/50/50/50.
    * RSI is Wilder's (TA-Lib, which FMZ's TA.RSI wraps).
    * No bar size in the source; FREQ = "bar_size_pending" (rule 2026-10-07: never choose a bar
      size; until 2026-10-07 this port used the old "1h" default). Logic unchanged.
    * Sizing (all-in buy, sell-all, SlidePrice offsets, min-stock guards) is not ported; it is in
      original_sizing.txt. No costs here.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_11604_rsi_zone_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-03, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

# zone -> (RSIBuyL, RSIBuyH, RSISellL, RSISellH)
ZONES = {
    "cross50": (50.0, 50.0, 50.0, 50.0),   # the original defaults
    "30_70": (0.0, 30.0, 70.0, 100.0),     # the description's "0-30 buy, 70-100 sell"
    "20_80": (0.0, 20.0, 80.0, 100.0),
}

GRID = {
    "rsi_period": [7, 14, 21],
    "zone": ["cross50", "30_70", "20_80"],
}
DEFAULT_PARAMS = {"rsi_period": 14, "zone": "cross50"}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
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
    d = close.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    return 100.0 - 100.0 / (1.0 + up / dn)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy_l, buy_h, sell_l, sell_h = ZONES[p["zone"]]
    rsi1 = _rsi(bars_df["close"], int(p["rsi_period"]))
    rsi2 = rsi1.shift(1)
    long_entries = (rsi1 >= buy_l) & (rsi2 <= buy_h) & (rsi1 > rsi2)
    short_entries = (rsi2 >= sell_l) & (rsi1 <= sell_h) & (rsi2 > rsi1)
    false = pd.Series(False, index=bars_df.index)
    return (long_entries.fillna(False).astype(bool), false.copy(),
            short_entries.fillna(False).astype(bool), false.copy())


def portfolio_kwargs(**params):
    return {}
