"""Band crossings confirmed by an EMA 3 crossing and the RSI, 1-minute bars: the close crossing over the lower band (20, 2) and over the EMA 3 with the RSI 14 under 30 goes long; the close crossing over the
upper band while crossing under the EMA 3 with the RSI over 70 goes short; reversing.
Port of FMZ strategy #444338 "Bollinger Bands and Moving Average Combined with Relative Strength Index Trading Strategy" (Custom Strategy (Bollinger Bands, EMA 3 and RSI)).

FMZ source id: 444338

Source
    https://www.fmz.com/strategy/444338 (PineScript v5, FMZ last modified 2024-03-11 11:02:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 155-187), BB 20 / 2 on close; EMA 3; RSI 14, levels 30 / 70
    crossover(close, lower) and crossover(close, ema3) and rsi < 30 -> entry Buy;  crossover(close, upper) and crossunder(close, ema3) and rsi > 70 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both conditions are ported as written; the short needs the close above the upper band and under
      the EMA 3 at once, so it is rare. No exit is sent: positions end at the opposite entry. Pine's
      stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band, EMA and RSI crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_444338_band_ema3_rsi_cross_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"length": 20, "rsi_length": 14, "mult": 2.0, "ema_len": 3, "os": 30.0, "ob": 70.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    lower, upper = basis - dev, basis + dev
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    c1 = c.shift(1)
    xo_low = (c > lower) & (c1 <= lower.shift(1))
    xo_up = (c > upper) & (c1 <= upper.shift(1))
    xo_e = (c > e) & (c1 <= e.shift(1))
    xu_e = (c < e) & (c1 >= e.shift(1))
    le = xo_low & xo_e & (r < float(p["os"]))
    se = xo_up & xu_e & (r > float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
