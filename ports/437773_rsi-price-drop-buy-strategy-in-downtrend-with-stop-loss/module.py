"""Bollinger dip buys with a slow RSI, 30-minute bars: a close under the lower band (SMA 20 - 2 sigma) with the RSI 60 under 40 goes long; a close over the upper band, or a long that is 50 price units in profit,
goes short; reversing.
Port of FMZ strategy #437773 "RSI收敛破位趋势震荡停损策略Price-Drop-Buy-Strategy-in-Downtrend-with-Stop-Loss" (price drop buy in).

FMZ source id: 437773

Source
    https://www.fmz.com/strategy/437773 (PineScript v3, FMZ last modified 2024-01-05 14:18:05).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-184), RSI 60, oversold 40, "overbought" 50 (a constant, always true); BB 20 x 2; date window true
    longcondition = close < BBlower and rsi(close, 60) < 40 -> entry buy;  shortcondition = (RSIoverBought and strategy.openprofit > 50) or close > BBupper -> entry sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * RSIoverBought is the number 50, so its test is always true; the short then fires when the open profit
      exceeds 50 account units. Criterion 2: with the default quantity of one unit that is a gain of 50
      price units; the port tests the open position's gain (close against the fill price, either side)
      against profit_frac x the fill price (0.0012 reads 50 on BTC near 42000). A long in profit flips to
      short; a short in profit re-sends the short, which pyramiding 0 ignores. A bar with both conditions
      ends short (the sell entry comes last). REVERSAL INTENDED. The capital is sizing. FREQ = "30min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit open-profit test -> fraction of the entry.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital stored.
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

NAME = "fmz_437773_bb_dip_buy_profit_flip"
FAMILY = "mean_reversion"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [60, 30],
    "profit_frac": [0.0012, 0.01],
}
DEFAULT_PARAMS = {"rsi_length": 60, "profit_frac": 0.0012, "oversold": 40.0, "bb_length": 20, "bb_mult": 2.0}


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
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    lc = ((c < basis - dev) & (r < float(p["oversold"]))).to_numpy()
    up_x = (c > basis + dev).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    fr = float(p["profit_frac"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        e = ov[entry_i] if pos != 0 and entry_i <= i else np.nan
        profit = (cv[i] - e) * pos if pos != 0 else np.nan
        sc = (pos != 0 and profit > fr * e) or up_x[i]
        s = pos
        if lc[i] and s != 1:
            s = 1
        if sc and s != -1:
            s = -1
        if s == 1 and pos != 1:
            le[i] = True
        elif s == -1 and pos != -1:
            se[i] = True
        if s != pos and i + 1 < m:
            entry_i = i + 1
        pos = s
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
