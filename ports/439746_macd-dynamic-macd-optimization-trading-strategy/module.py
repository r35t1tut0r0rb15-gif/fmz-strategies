"""Hourly bars: the MACD 16 / 34 / 10 crossing over its signal above zero with the RSI 19 under 70 and volume above its 13-bar average goes long, the mirror below zero with the RSI above 30 goes short; each with a 10.5 % stop and a 0.3 % target from the signal close; reversing.
Port of FMZ strategy #439746 "经典动态MACD优化交易策略Dynamic-MACD-Optimization-Trading-Strategy" (优化版MACD交易策略 (optimised MACD)).

FMZ source id: 439746

Source
    https://www.fmz.com/strategy/439746 (PineScript v5, FMZ last modified 2024-01-23 14:40:38).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 158-194), MACD 16 / 34 / 10; RSI 19, 70 / 30; volume SMA 13; stop 10.5 %, target 0.3 %
    longCondition = crossover(macd, signal) and macd > 0 and rsi < 70 and volume > sma(volume, 13) -> entry, exit(stop = close x 0.895, limit = close x 1.003)
    shortCondition = crossunder(macd, signal) and macd < 0 and rsi > 30 and volume > volumeAvg -> entry, exit(stop = close x 1.105, limit = close x 0.997)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are sent on the signal bar only, as price levels from that bar's close: ported as
      fractions of the fill, exact (stop 1 - close / open x 0.895, target close / open x 1.003 - 1 for a
      long); a level the fill has already passed is taken at once (a 1e-6 floor). A repeated signal while
      already in that position re-sends the bracket from its own close; the port keeps the first. The
      stop is 35 times the target, as written (weird case). REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket at the signal close as fractions of the fill.
    2 generic: PASS, MACD signal crossings with RSI and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 13; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439746_macd16_34_10_rsi_volume_wide_stop_tight_target_reversal"
FAMILY = "macd_variant"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.105, 0.03],
    "tp_pct": [0.003, 0.01],
}
DEFAULT_PARAMS = {"fast": 16, "slow": 34, "signal": 10, "rsi_len": 19, "vol_len": 13, "sl_pct": 0.105,
                  "tp_pct": 0.003}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    le = up & (macd > 0) & (r < 70) & vol_ok
    se = dn & (macd < 0) & (r > 30) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, se.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    sl, tp = float(p["sl_pct"]), float(p["tp_pct"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl)).mask(sf, k * (1 + sl) - 1)
    tp_f = pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1).mask(sf, 1 - k * (1 - tp))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
