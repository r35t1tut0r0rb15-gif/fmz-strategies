"""RSI 5 dips and spikes in the direction of the EMA 90 / 300 order, 1-minute bars: with the EMA 90 above the EMA 300 an RSI under 45 goes long; with it below, an RSI over 85 goes short; reversing (the
take-profit and stop lines are only drawn).
Port of FMZ strategy #446556 "EMA-RSI-趋势追踪与动量策略-EMA-RSI-Trend-Following-and-Momentum-Strategy" (Bybit EMA RSI Strategy).

FMZ source id: 446556

Source
    https://www.fmz.com/strategy/446556 (PineScript v5, FMZ last modified 2024-03-29 16:30:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-192), EMA 90 / 300; RSI 5, levels 45 / 85; take profit 5 %, stop 3 % (drawn only); Bybit VIP level (commission display only)
    ema90 > ema300 and rsi < 45 -> entry Long;  else ema90 < ema300 and rsi > 85 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The take-profit and stop prices only draw lines; no exit is ever sent, so positions end at the
      opposite entry. The commission input only shifts the drawn entry price. Both conditions are
      levels, so a repeated entry on the held side is ignored. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes with an EMA trend order.
    3 crypto-exchange-only: no (exchange pair in the header only; the Bybit level is display only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446556_rsi5_dip_spike_ema90_300_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [90, 50],
    "rsi_lower": [45.0, 30.0],
}
DEFAULT_PARAMS = {"fast": 90, "rsi_lower": 45.0, "slow": 300, "rsi_len": 5, "rsi_upper": 85.0}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (f > s) & (r < float(p["rsi_lower"]))
    se = (f < s) & (r > float(p["rsi_upper"])) & ~le
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
