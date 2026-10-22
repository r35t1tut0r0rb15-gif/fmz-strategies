"""Fast and slow RSI disagreement, 15-minute bars: a slow RSI 14 above 50 with a fast RSI 2 below 50 goes long, the mirror goes short; a long closes on a green bar, a short on a red bar.
Port of FMZ strategy #439231 "双RSI突破量化交易策略Dual-RSI-Breakthrough-Strategy" (Noro's Double RSI Strategy 1.0).

FMZ source id: 439231

Source
    https://www.fmz.com/strategy/439231 (PineScript v2, FMZ last modified 2024-01-18 15:25:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-167), long and short on; leverage 1; fast RSI 2, slow RSI 14; date inputs unused
    up = slowrsi > 50 and fastrsi < 50;  dn = slowrsi < 50 and fastrsi > 50;  exit = (long and close > open) or (short and close < open)
    if up: (if short: close_all) entry Long;  if dn: (if long: close_all) entry Short;  if exit: close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSIs are Noro's rma RSIs (down == 0 -> 100, else up == 0 -> 0). The exit test reads the
      position held at the bar close. An opposite signal closes the position and opens the other side;
      when the bar also has the exit colour, the final close_all leaves the bar flat (as #430380). A
      same-side signal while in a position is ignored. From flat the exit cannot fire and the signal
      opens. REVERSAL INTENDED. The equity / close lot is sizing. FREQ = "15min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and bar colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity / close lot and leverage stored.
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

NAME = "fmz_439231_noro_double_rsi_colour_exit"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [2, 3],
    "slow": [14, 21],
}
DEFAULT_PARAMS = {"fast": 2, "slow": 14}


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
    o, c = bars_df["open"], bars_df["close"]
    fr, sr = _rsi(c, int(p["fast"])), _rsi(c, int(p["slow"]))
    up = ((sr > 50) & (fr < 50)).to_numpy()
    dn = ((sr < 50) & (fr > 50)).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        ex = (pos == 1 and green[i]) or (pos == -1 and red[i])
        new = pos
        if up[i]:
            new = 1
        elif dn[i]:
            new = -1
        if ex:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
