"""Dip buys above the SMA 9 with a weak RSI, 30-minute bars, long only: the close above the SMA 9 with the RSI 14 under 40 goes long; a 1.5 % stop and a 3 % target from the fill.
Port of FMZ strategy #442119 "Momentum Moving Average Reversal Strategy" (MARSI).

FMZ source id: 442119

Source
    https://www.fmz.com/strategy/442119 (PineScript v4, FMZ last modified 2024-02-19 14:59:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-156), MA 9; RSI 14 (40); stop 1.5 %, target 3 %; dates 2020-2112 (window() true); 100 % of equity, capital 1000
    MAshort < close and RSI < 40 -> entry long;  position open -> strategy.exit(stop = avg (1 - 1.5 %), limit = avg (1 + 3 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fraction of the average price, placed while a position is open: fixed fractions
      0.015 / 0.03 of the fill; the script's is first placed at the fill bar's close, the port's is active
      from the fill bar (as #440797). The condition is a level; an entry while long does nothing. Long only.
      Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size and capital are sizing. FREQ =
      "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, SMA side, RSI level and percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
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

NAME = "fmz_442119_sma9_side_rsi40_pct_bracket_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.015, 0.03],
    "tp": [0.03, 0.06],
}
DEFAULT_PARAMS = {"sl": 0.015, "tp": 0.03, "ma_len": 9, "rsi_len": 14, "rsi_level": 40}


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
    go = ((c.rolling(int(p["ma_len"])).mean() < c) & (_rsi(c, int(p["rsi_len"])) < float(p["rsi_level"]))).to_numpy()
    s_, t_ = float(p["sl"]), float(p["tp"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and go[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
