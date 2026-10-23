"""1-minute bars, long only: a close above both (undisplaced) Ichimoku leading spans with the script's ADX 14 over 25 and the close above the session VWAP goes long; a close below both spans with ADX over 25 and the close below the VWAP closes it.
Port of FMZ strategy #482782 "Multi Indicator Trend Recognition and Momentum Validation Trading Strategy" (Ichimoku + ADX + VWAP Strategy).

FMZ source id: 482782

Source
    https://www.fmz.com/strategy/482782 (PineScript v5, FMZ last modified 2025-02-20 10:48:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 107-178), Ichimoku 9 / 26 / 52 (spans compared undisplaced); manual ADX 14 (RMA); session VWAP; 10 % of equity
    buyCondition = close > leadingSpanA and close > leadingSpanB and adx > 25 and close > vwap -> entry Long
    sellCondition = close < leadingSpanA and close < leadingSpanB and adx > 25 and close < vwap -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are compared on their own bar (the 26-bar offset is only in the plot). The ADX uses Wilder
      RMAs of the usual directional moves over the RMA of ta.tr(true). ta.vwap(close) restarts each
      session: the house session is the broker day (17:00 America/New_York). An entry while long adds
      nothing; a buy and a sell never meet on one bar. The header names TRUMP_USDT; the rules are
      generic. Long only. 10 % of equity is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku cloud side with ADX strength and a VWAP filter.
    3 crypto-exchange-only: no (exchange pair in the header only (TRUMP_USDT)).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482782_ichimoku_cloud_adx_session_vwap_1m_long_only"
FAMILY = "ichimoku"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [25.0, 20.0],
    "base": [26, 52],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span_b": 52, "adx_min": 25.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    mid = lambda n: (h.rolling(n).max() + lo.rolling(n).min()) / 2
    span_a = (mid(int(p["conv"])) + mid(int(p["base"]))) / 2
    span_b = mid(int(p["span_b"]))
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    trr = _rma(tr, 14)
    pdi, mdi = _rma(pdm, 14) / trr * 100, _rma(mdm, 14) / trr * 100
    adx = _rma((pdi - mdi).abs() / (pdi + mdi) * 100, 14)
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    strong = adx > float(p["adx_min"])
    buy = (c > span_a) & (c > span_b) & strong & (c > vw)
    sell = (c < span_a) & (c < span_b) & strong & (c < vw)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
