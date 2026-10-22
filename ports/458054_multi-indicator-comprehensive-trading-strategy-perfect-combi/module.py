"""MACD crossings or RSI 14 extremes inside the Bollinger bands, 1-hour bars: a MACD cross up or an RSI crossing under 30, with the close over the lower band, goes long with a 2 % stop and 5 % target from the signal close; the mirror goes short; reversing.
Port of FMZ strategy #458054 "Multi Indicator Comprehensive Trading Strategy Perfect Combination of Momentum Overbought Oversold and Volatility" (Multi-Indicator Strategy (MACD / RSI / Bollinger)).

FMZ source id: 458054

Source
    https://www.fmz.com/strategy/458054 (PineScript v5, FMZ last modified 2024-07-29 15:45:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 211-270), MACD 12 / 26 / 9; RSI 14 (70 / 30); Bollinger 20 / 2; stop 2 %, target 5 % of the signal close
    (crossover(macd, signal) or crossunder(rsi, 30)) and close > lower -> entry Long, exit(limit = close x 1.05, stop = close x 0.98)
    (crossunder(macd, signal) or crossover(rsi, 70)) and close < upper -> entry Short, exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed on the signal bar from its close: ported as the fixed fractions 0.02 / 0.05
      of the fill (as #437751). A repeat signal inside a trade re-issues them, which stops() cannot
      express: the opening levels are kept and the module is marked trailing_stop_pending (as
      #434428). A bar meeting both entries ends short (the later call wins, as #437773). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the bracket as fixed fractions; re-issued levels pending (mark).
    2 generic: PASS, MACD / RSI triggers inside the bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458054_macd_or_rsi_trigger_inside_bands_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [14, 7],
    "sl_pct": [0.02, 0.01],
    "tp_pct": [0.05, 0.03],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sl_pct": 0.02, "tp_pct": 0.05}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    basis = c.rolling(20).mean()
    dev = 2.0 * c.rolling(20).std(ddof=0)
    m_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    m_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    r_dn30 = (r < 30) & (r.shift(1) >= 30)
    r_up70 = (r > 70) & (r.shift(1) <= 70)
    le = (m_up | r_dn30) & (c > basis - dev)
    se = (m_dn | r_up70) & (c < basis + dev)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
