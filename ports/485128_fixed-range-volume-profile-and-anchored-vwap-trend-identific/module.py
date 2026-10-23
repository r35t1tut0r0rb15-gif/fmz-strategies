"""Hourly bars: the close crossing over the session VWAP above the EMA 200 with RSI 14 over 30, MACD over its signal and above-average volume goes long with a stop 1.5 ATR 14 under the signal close; the mirror goes short; reversing.
Port of FMZ strategy #485128 "Fixed Range Volume Profile And Anchored VWAP Trend Identification Strategy With Dynamic Stop Loss" (FRVP + AVWAP Improved By NgashCT).

FMZ source id: 485128

Source
    https://www.fmz.com/strategy/485128 (PineScript v5, FMZ last modified 2025-03-06 11:14:10).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 188-239), session VWAP ("AVWAP"); EMA 200; RSI 14; MACD 12 / 26 / 9; volume SMA 20; ATR 14 x 1.5; trail_points = 2 ATR (no offset); 10 % of equity
    longCondition = crossover(close, vwap) and close > ema200 and rsi > 30 and macd > signal and volume > sma(volume, 20) -> entry Long, exit(stop = close - 1.5 atr, trail_points = 2 atr)
    shortCondition mirrored (rsi < 70) -> entry Short, exit(stop = close + 1.5 atr, trail_points = 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_points without a trail_offset places no trailing stop (as #441084), so the exit is the stop
      sent on the signal bar from that close: ported as a fraction of the fill, exact (1e-6 floor); there
      is no target. The "AVWAP" is ta.vwap(close), which restarts each session: the house session is the
      broker day (17:00 America/New_York). The volume-profile levels only compute. REVERSAL INTENDED.
      10 % of equity is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at the signal close as a fraction of the fill.
    2 generic: PASS, session-VWAP crossings in the EMA 200 trend with RSI / MACD / volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the VWAP weights and against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485128_session_vwap_cross_ema200_rsi_macd_volume_atr_stop_1h_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 2.5],
    "ema_len": [200, 100],
}
DEFAULT_PARAMS = {"sl_atr": 1.5, "ema_len": 200}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    vol_ok = v > v.rolling(20).mean()
    buy = (c > vw) & (c.shift(1) <= vw.shift(1)) & (c > ema) & (r > 30) & (macd > sig) & vol_ok
    sell = (c < vw) & (c.shift(1) >= vw.shift(1)) & (c < ema) & (r < 70) & (macd < sig) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    d = float(p["sl_atr"]) * _atr(bars_df, 14)
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - d).shift(1) / o)
            .mask(sf, (c + d).shift(1) / o - 1))
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
