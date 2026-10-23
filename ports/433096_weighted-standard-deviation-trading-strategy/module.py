"""45-minute bars: a low at or under the volume-weighted mean of 20 closes minus 2 volume-weighted standard deviations goes long, a high at or over the mean plus 2 deviations goes short; a 3.11 % stop and a 7.5 % target from the fill; reversing.
Port of FMZ strategy #433096 "Weighted Standard Deviation Trading Strategy" ([cache_that_pass] 1m 15m Function - Weighted Standard Deviation).

FMZ source id: 433096

Source
    https://www.fmz.com/strategy/433096 (PineScript v4, FMZ last modified 2023-11-24 13:54:58).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 122-244), len 20; bands mean +- 2 sd (volume-weighted, from series); SL 3.11 %, TP 7.5 %
    [m, v, d] = f_weighted_sd_from_series(close, volume, 20): m = sum(close x volume, 20) / sum(volume, 20), variance = sum(volume x (m - close)^2) / ((nonzero - 1) x sum(volume) / nonzero)
    low <= m - 2 d -> entry LE;  high >= m + 2 d -> entry SE;  position_size > 0 -> exit(stop = avg x 0.9689, limit = avg x 1.075), short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands are the series version (weights = volume); the array version (linear weights) only feeds
      plots. "nonzero" counts the bars with non-zero volume in the window, as written. When both band
      touches happen on one bar the later call (short) is taken. The exits are sent once a position exists
      (from the bar after the fill in the script, from the fill in the port). REVERSAL INTENDED. 20 % of
      equity and the commission are sizing and costs. Stop module: portfolio_kwargs {} (driver D4). FREQ
      = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, volume-weighted band touches.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 20 % of equity, capital 10000, commission 0.075 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of the 20-bar mean and standard deviation; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433096_volume_weighted_sd_band_touch_pct_bracket_reversal"
FAMILY = "weighted_bands"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "band_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "band_mult": 2.0, "sl": 0.0311, "tp": 0.075}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["length"])
    sw = v.rolling(n).sum()
    mean = (c * v).rolling(n).sum() / sw.where(sw != 0)
    cv, vv, mv = c.to_numpy(dtype=float), v.to_numpy(dtype=float), mean.to_numpy(dtype=float)
    m = len(cv)
    dev = np.full(m, np.nan)
    if m >= n:
        wc = np.lib.stride_tricks.sliding_window_view(cv, n)
        wv = np.lib.stride_tricks.sliding_window_view(vv, n)
        sq = (wv * (mv[n - 1:, None] - wc) ** 2).sum(axis=1)
        nz = (wv != 0).sum(axis=1)
        swv = wv.sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            var = sq / ((nz - 1) * swv / nz)
        dev[n - 1:] = np.sqrt(var)
    d = pd.Series(dev, index=c.index)
    k = float(p["band_mult"])
    lt = (lo <= mean - d * k).to_numpy()
    st = (h >= mean + d * k).to_numpy()
    le = lt & ~st
    se = st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
