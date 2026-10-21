"""RSI of the MACD line crossing up through 30 or 35 above the EMA 21, 3-minute bars, long only: such a crossing with the close at or above the EMA 21 buys; the RSI of MACD crossing under 15 closes.
Port of FMZ strategy #438785 "MACD指标的RSI反转策略RSI-of-MACD-Reversal-Strategy" (RSIofMACD).

FMZ source id: 438785

Source
    https://www.fmz.com/strategy/438785 (PineScript v4, FMZ last modified 2024-01-15 12:33:14).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 150-218), MACD 12 / 21 / 9; RSI of MACD 14; risk 10 %, stop 3 (sizing only); take profit off; pyramiding 1; 20 % of equity
    r = rsi(macd line, 14);  (crossover(r, 30) or crossover(r, 35)) and close >= ema(close, 21) -> entry RSIofMACD (risk-sized qty);  crossunder(r, 15) -> close all;  partial exit only with take profit on

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop-loss input only sizes the quantity (risk / stop distance); no stop order is placed. Take
      profit is off, so the partial exit never runs. pyramiding 1 holds one position. Long only. The size
      inputs are sizing. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI of MACD crossings and an EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based quantity, stop input and percent-of-equity size stored.
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

NAME = "fmz_438785_rsi_of_macd_long"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "slow": [21, 26],
}
DEFAULT_PARAMS = {"rsi_len": 14, "slow": 21, "fast": 12}


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
    c = bars_df["close"]
    sl = int(p["slow"])
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=sl, adjust=False).mean()
    r = _rsi(macd, int(p["rsi_len"]))
    ema = c.ewm(span=sl, adjust=False).mean()

    def _xo(lvl):
        return (r > lvl) & (r.shift(1) <= lvl)

    le = (_xo(30) | _xo(35)) & (c >= ema)
    lx = (r < 15) & (r.shift(1) >= 15)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
