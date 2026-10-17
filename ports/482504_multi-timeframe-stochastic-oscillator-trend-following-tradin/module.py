"""The 3-bar SMA of the daily stochastic (14) crossing up through 20 above the EMA 50 goes long, crossing down through
80 below it goes short, with a 1.5 ATR stop and a 3 ATR target, three-hour bars.
Port of FMZ strategy #482504 "多时框随机震荡趋势跟踪交易策略-Multi-Timeframe-Stochastic-Oscillator-Trend-Following-Trading-Strategy" (Ultimate fairas Oil).

FMZ source id: 482504

Source
    https://www.fmz.com/strategy/482504 (PineScript v5, FMZ last modified 2025-02-18 17:53:04).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-158), stochastic 14 on "D", smooth 3, EMA 50, ATR 14 x 1.5, target 2x
    stoch_d = request.security("D", ta.stoch(close, high, low, 14)); k = sma(stoch_d, 3) on the chart
    crossover(k, 20) and close > ema50 -> entry long with exit(stop = close - 1.5 ATR, limit = close + 3 ATR,
    trail_points = 1.5 ATR); crossunder(k, 80) and close < ema50 -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * Higher timeframe (house rule, #490787): the stochastic of the last COMPLETED broker day (17:00
      America/New_York) as of each three-hour bar's close; the 3-bar SMA runs on the chart's bars, as written.
    * trail_points without trail_offset is inert (lane convention): no trail.
    * The bracket is placed with the entry from the signal bar: 1.5 ATR / close and 3 ATR / close, shifted one bar
      inside stops() and re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "3h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry; the daily value without look-ahead.
    2 generic: PASS, a stochastic, an EMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 2 % risk sizing quoted; the bracket via stops(), in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily stochastic; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482504_daily_stoch_cross_ema50_atr_bracket_3h"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "ema_len": [50, 100],
}
DEFAULT_PARAMS = {"k_period": 14, "smooth_k": 3, "ob": 80.0, "os": 20.0, "atr_mult": 1.5, "ema_len": 50}
K_PERIOD = 14


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.resample(FREQ, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    lab = broker_day(ohlc.index)
    d = ohlc.groupby(lab).agg({"high": "max", "low": "min", "close": "last"}).dropna(how="all")
    ll, hh = d["low"].rolling(K_PERIOD).min(), d["high"].rolling(K_PERIOD).max()
    st = 100 * (d["close"] - ll) / (hh - ll)
    end = (d.index + pd.Timedelta(hours=17)).tz_localize("America/New_York").tz_convert("UTC")
    daily = pd.DataFrame({"end": end, "stoch_d": st.to_numpy()}).sort_values("end")
    bar_end = pd.DataFrame({"end": bars.index + pd.Timedelta(FREQ)})
    got = pd.merge_asof(bar_end, daily, on="end", direction="backward")   # last broker day completed by the bar's close
    bars["stoch_d"] = got["stoch_d"].to_numpy()
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    k = bars_df["stoch_d"].rolling(int(p["smooth_k"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    long_e = ((k > p["os"]) & (k.shift(1) <= p["os"]) & (c > ema)).astype(bool)
    short_e = ((k < p["ob"]) & (k.shift(1) >= p["ob"]) & (c < ema)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, 14) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": 2 * sl}


def portfolio_kwargs(**params):
    return {}
