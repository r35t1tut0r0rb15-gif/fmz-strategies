"""CCI zero crossings against a mean-reversion channel, 3-minute bars: a CCI zero cross after an overbought RSI with the bar entirely under the EMA 200
goes long (and the mirror after an oversold RSI over the EMA goes short), with a fixed stop; any touch of the outer bands (EMA 200 +- 1.6 sd)
closes the position.
Port of FMZ strategy #435969 "Reverse Mean Breakthrough Strategy" (BroTheJo Strategy (inverted)).

FMZ source id: 435969

Source
    https://www.fmz.com/strategy/435969 (PineScript v5, FMZ last modified 2023-12-20 14:48:57).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 171-233), CCI 10; RSI 14 at 35 / 65 within the last 4 bars; EMA 200 and 1.6 sd bands; stop 10 pips
    cross = ta.cross(cci, 0) (both directions; the "Down" variant is the same event);  longEntry = cross and overboughtAgo and prevHigh <= ema and prevLow <= ema;  shortEntry = cross and oversoldAgo and prevHigh >= ema and prevLow >= ema
    entry long, exit(stop = close - 10);  entry short, exit(stop = close + 10);  closeAll = high >= upper band or low <= lower band

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross(x, 0) and ta.cross(0, x) are the same event (a crossing in either direction), so the
      entry side comes from the RSI and the mean position, as written (an inverted fade). Criterion 2: the
      stop is 10 price units ("pips"): the port uses sl_stop = k_atr x ATR / close of the signal bar,
      shifted one bar inside stops() (re-based on the fill); 0.05 is the reading of a small stop on a
      3-minute bar, 1.0 a volatility-sized stop. prevHigh / prevLow are the current bar's high / low
      (highest(high, 1)). The close_all is a rule on bar closes (the band touch), filled at the next open: a
      close-based exit signal; a bar with an entry and a band touch is flat (the entry is dropped).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 3-minute bars: not coarse.
      FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, price-unit stop -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the pip stop input quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430176 (2 members, best partner #430176, Jaccard 0.766); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435969_cci_cross_mean_channel_fade"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.05, 1.0],
    "band_mult": [1.6, 2.0],
}
DEFAULT_PARAMS = {"k_atr": 0.05, "band_mult": 1.6, "cci_len": 10, "rsi_len": 14, "ob": 65, "os": 35, "ema_period": 200,
                  "atr_len": 14}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        cci = (c - ma) / (0.015 * md)
    crossed = ((cci > 0) & (cci.shift(1) <= 0)) | ((cci < 0) & (cci.shift(1) >= 0))
    r = int(p["rsi_len"])
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / r, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / r, adjust=False).mean()
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn))), index=c.index)
    ob, os_ = float(p["ob"]), float(p["os"])
    oversold = pd.concat([rsi.shift(k) <= os_ for k in range(4)], axis=1).any(axis=1)
    overbought = pd.concat([rsi.shift(k) >= ob for k in range(4)], axis=1).any(axis=1)
    ep = int(p["ema_period"])
    mean = c.ewm(span=ep, adjust=False).mean()
    sd = c.rolling(ep).std(ddof=0)
    upper, lower = mean + sd * float(p["band_mult"]), mean - sd * float(p["band_mult"])
    short_e = crossed & oversold & (h >= mean) & (lo >= mean)
    long_e = crossed & overbought & (h <= mean) & (lo <= mean)
    close_all = ((h >= upper) | (lo <= lower)).fillna(False)
    return (long_e.fillna(False) & ~close_all), (short_e.fillna(False) & ~close_all), close_all


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, ca = _signals(bars_df, p)
    return le.astype(bool), ca.astype(bool), se.astype(bool), ca.astype(bool)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f}


def portfolio_kwargs(**params):
    return {}
