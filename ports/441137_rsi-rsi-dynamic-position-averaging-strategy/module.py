"""RSI 14 under 30 dip buys with a 0.5 % close target, 1-hour bars, long only: from no open cycle, the RSI under 30 goes long; the close 0.5 % above the fill closes everything and ends the cycle.
Port of FMZ strategy #441137 "基于RSI动态加仓策略RSI-Dynamic-Position-Averaging-Strategy" (RSI Martingale Strategy).

FMZ source id: 441137

Source
    https://www.fmz.com/strategy/441137 (PineScript v5, FMZ last modified 2024-02-06 09:44:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-144), RSI 14, oversold 30; profit target 0.5 %; initial investment 5 % of equity (cash qty); martingale adds at -0.5 % and -1 %
    rsi < 30 and na(initialEntryPrice) -> initialEntryPrice = close, entry Initial Buy (5 % of equity)
    close < initialEntryPrice 0.995 -> entry Martingale Buy 1 (x 2);  close < initialEntryPrice 0.990 -> entry Martingale Buy 2 (x 4)
    position open and (close - position_avg_price) / position_avg_price >= 0.5 % -> close_all, initialEntryPrice = na

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy() leaves pyramiding at its default 0, so only one entry in a direction can be open: the
      two martingale entries are refused while the first buy is open, and the position never adds. The
      target is a bar-close test of the close against the fill price (the average price of one entry),
      sent at the next open. The cycle flag is reset only by the target, so no new buy comes before it.
      Long only. The cash quantities (5 % of equity, x 2, x 4) are sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level and close-vs-fill target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash quantity rules stored.
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

NAME = "fmz_441137_rsi30_dip_close_target_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [30, 20],
    "target": [0.005, 0.01],
}
DEFAULT_PARAMS = {"oversold": 30, "target": 0.005, "rsi_length": 14}


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
    sig = (_rsi(c, int(p["rsi_length"])) < float(p["oversold"])).to_numpy()
    tg = float(p["target"])
    cv = c.to_numpy(dtype=float)
    ov = bars_df["open"].to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cycle, held, entry_i = False, 0, -1
    for i in range(m):
        if sig[i] and not cycle and i + 1 < m:
            le[i], cycle, entry_i = True, True, i + 1
        if held == 1 and i >= entry_i and (cv[i] - ov[entry_i]) / ov[entry_i] >= tg:
            lx[i], cycle, held = True, False, 0
        elif le[i]:
            held = 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
