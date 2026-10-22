"""RSI 2 dips under 10 above the SMA 200, 1-hour bars, long only, with a bracket from the signal bar's low: target 6 % above it, stop 3 % below it.
Port of FMZ strategy #449811 "RSI2策略之日内反转胜率回测-RSI2-Strategy-Intraday-Reversal-Win-Rate-Backtest" (RSI2 strategy Raj).

FMZ source id: 449811

Source
    https://www.fmz.com/strategy/449811 (PineScript v5, FMZ last modified 2024-04-29 14:02:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-146), RSI 2, oversold 10 (overbought 90 unused); SMA 200; stop 3 %, target 6 % of the signal bar's low; qty 1; margins 100 / 100
    close > sma200 and rsi2 < 10 -> entry Long (qty 1), ent_dat = bar time;  on that bar: bp = low, tar = bp x 1.06, los = bp x 0.97;  later bars -> exit(limit = tar, stop = los)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels come from the signal bar's low: sl_stop = (close - 0.97 low) / close and tp_stop =
      (1.06 low - close) / close of the signal bar, shifted one bar inside stops() and re-based on the
      fill; the exit is sent from the bar after the signal on (active from the fill, as #440797). A
      repeated signal inside the trade re-bases the levels on its own low: not expressible (mark
      trailing_stop_pending). Long only. Stop module: portfolio_kwargs {} (driver D4). The qty 1 and
      margins are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar (re-sent levels marked).
    2 generic: PASS, RSI 2 dips in an uptrend with a low-based bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the qty 1 and margins stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_449811_rsi2_dip_above_sma200_low_bracket_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "max_loss": [3.0, 1.5],
    "target": [6.0, 3.0],
}
DEFAULT_PARAMS = {"max_loss": 3.0, "target": 6.0, "rsi_len": 2, "os": 10.0, "sma_len": 200}


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
    r = _rsi(c, int(p["rsi_len"]))
    le = (c > c.rolling(int(p["sma_len"])).mean()) & (r < float(p["os"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, lo = bars_df["close"], bars_df["low"]
    sl = (c - lo * (1 - float(p["max_loss"]) / 100)) / c
    tp = (lo * (1 + float(p["target"]) / 100) - c) / c
    return {"sl_stop": sl.shift(1), "tp_stop": tp.where(tp > 0).shift(1)}


def portfolio_kwargs(**params):
    return {}
