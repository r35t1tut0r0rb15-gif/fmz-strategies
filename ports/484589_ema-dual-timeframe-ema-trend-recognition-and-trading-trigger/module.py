"""EMA 12 / 26 crosses (or 5 % candles) in the direction of the daily EMA 5 / 30 trend, with a 10-bar extreme stop,
1-hour bars: with the last completed day's EMA 5 above its EMA 30, an hourly EMA 12 cross above EMA 26 (or a candle
up more than 5 %) goes long with a stop at the 10-bar low; the mirror goes short with a stop at the 10-bar high.
Port of FMZ strategy #484589 "双时间框架EMA趋势识别与交易触发量化策略-Dual-Timeframe-EMA-Trend-Recognition-and-Trading-Trigger-Quantitative-Strategy" (EMA Trend & Trigger Strategy).

FMZ source id: 484589

Source
    https://www.fmz.com/strategy/484589 (PineScript v5, FMZ last modified 2025-03-03 10:28:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 252-290), daily EMA 5 / 30, hourly EMA 12 / 26, 5 % candle, 10-bar extremes
    uptrend = security("1D", ema5) > security("1D", ema30);  buy = crossover(ema12, ema26) and uptrend
    highVolatilityUp = (close - open) / open x 100 > 5 and uptrend
    buy or highVolatilityUp -> entry long + exit(stop = lowest(low, 10))  (short mirrored with highest(high, 10))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily EMAs are the last completed broker day's (house rule for a higher timeframe, as #430771), from the
      port's bars grouped by broker day; request.security("60") on the 1-hour chart is the bar's own value.
    * The stop is fixed at the signal bar: sl_stop = (close - lowest(low, 10)) / close (short: (highest(high, 10) -
      close) / close), shifted one bar inside stops() and re-based on the fill; a signal whose level is not beyond the
      close (zero distance) emits no entry (as #491035). A same-side signal while held re-places the stop: mark
      trailing_stop_pending; the port keeps the entry's stop.
    * Both directions on one bar: the short, written last, wins. Entries reverse (REVERSAL INTENDED). Stop module:
      portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop from the signal bar (re-placement marked).
    2 generic: PASS, EMAs, a percentage move and rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the stop ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily EMAs; no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484589_daily_ema_trend_hourly_cross_stop"
FAMILY = "ma_trend_filter"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "d_short": [5, 10],
    "move_pct": [5.0, 3.0],
}
DEFAULT_PARAMS = {"d_short": 5, "d_long": 30, "h_short": 12, "h_long": 26, "move_pct": 5.0, "extreme_len": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    lab = broker_day(bars_df.index)
    dc = pd.Series(c.to_numpy(), index=lab).groupby(level=0).last()
    de_s = dc.ewm(span=int(p["d_short"]), adjust=False).mean().shift(1)     # the last completed broker day
    de_l = dc.ewm(span=int(p["d_long"]), adjust=False).mean().shift(1)
    ds, dl = de_s.reindex(lab).to_numpy(), de_l.reindex(lab).to_numpy()
    up, dn = ds > dl, ds < dl
    hs = c.ewm(span=int(p["h_short"]), adjust=False).mean()
    hl = c.ewm(span=int(p["h_long"]), adjust=False).mean()
    x_up = ((hs > hl) & (hs.shift(1) <= hl.shift(1))).to_numpy()
    x_dn = ((hs < hl) & (hs.shift(1) >= hl.shift(1))).to_numpy()
    chg = ((c - o) / o * 100).to_numpy()
    n = int(p["extreme_len"])
    sl_l = ((c - lo.rolling(n).min()) / c).to_numpy()
    sl_s = ((h.rolling(n).max() - c) / c).to_numpy()
    go_s = ((x_dn & dn) | ((chg < -p["move_pct"]) & dn)) & (sl_s > 0)
    go_l = ((x_up & up) | ((chg > p["move_pct"]) & up)) & (sl_l > 0) & ~go_s
    sl = np.where(go_l, sl_l, np.where(go_s, sl_s, np.nan))
    idx = bars_df.index
    return pd.Series(go_l, index=idx), pd.Series(go_s, index=idx), pd.Series(sl, index=idx)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _signals(bars_df, p)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
