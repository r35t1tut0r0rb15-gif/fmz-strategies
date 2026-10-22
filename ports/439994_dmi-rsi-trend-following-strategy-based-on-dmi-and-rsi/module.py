"""Counter-DMI RSI extremes with a 0.5 % stop, 1-hour bars: an RSI 14 under 30 with ADX over 20 and -DI above +DI goes long; an RSI over 70 with ADX over 20 and +DI above -DI goes short; each trade has a stop
0.5 % from the fill; reversing.
Port of FMZ strategy #439994 "基于DMI和RSI的趋势跟随策略Trend-Following-Strategy-Based-on-DMI-and-RSI" (DMI and RSI Strategy).

FMZ source id: 439994

Source
    https://www.fmz.com/strategy/439994 (PineScript v5, FMZ last modified 2024-01-25 15:56:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-186), ADX 14 / DI 14; stop factor 0.5 %; RSI 14, 70 / 30; 10 % of equity
    long = rsi < 30 and adx > 20 and minus > plus -> entry Long;  short = rsi > 70 and adx > 20 and plus > minus -> entry Short;  exit(stop = avg x (1 -/+ 0.5 %)) while in the position

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trailing" stop is a fixed 0.5 % of the average (fill) price, re-sent at the same level: the
      port starts it at the fill (sl_stop 0.005). fixnan holds the last DI value, as written.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 10 %
      of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop from the fill.
    2 generic: PASS, RSI extremes and DMI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the stop factor stored.
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

NAME = "fmz_439994_dmi_rsi_counter_extremes_stop"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_factor": [0.5, 1.0],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"stop_factor": 0.5, "rsi_length": 14, "di_len": 14, "adx_len": 14, "adx_min": 20,
                  "overbought": 70, "oversold": 30}


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


def _fixnan(x):
    """Pine's fixnan: an undefined value takes the last defined one (leading values stay undefined)."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), -1)
    idx = np.maximum.accumulate(idx)
    out = np.where(idx >= 0, v[np.clip(idx, 0, None)], np.nan)
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["di_len"])
    up, dn = h.diff(), -lo.diff()
    pdm = up.where(up.isna(), np.where((up > dn) & (up > 0), up, 0.0))
    mdm = dn.where(dn.isna(), np.where((dn > up) & (dn > 0), dn, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pl = _fixnan(100 * _rma(pdm, n) / trr)
        mi = _fixnan(100 * _rma(mdm, n) / trr)
    s = pl + mi
    adx = 100 * _rma((pl - mi).abs() / s.where(s != 0, 1.0), int(p["adx_len"]))
    r = _rsi(c, int(p["rsi_length"]))
    strong = adx > float(p["adx_min"])
    le = (r < float(p["oversold"])) & strong & (mi > pl)
    se = (r > float(p["overbought"])) & strong & (pl > mi)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_factor"]) / 100}


def portfolio_kwargs(**params):
    return {}
