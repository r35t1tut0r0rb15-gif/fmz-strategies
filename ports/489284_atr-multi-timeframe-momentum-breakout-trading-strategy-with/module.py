"""Five-bar breakouts in the EMA 20 / 50 trend with an RSI filter, an ATR stop and an ATR trail, broker days: a close
above the previous five bars' highest high with EMA 20 above EMA 50 and RSI 14 below 70 goes long; the mirror goes
short; each trade has a stop 1.5 ATR from the entry and a trail 1.5 ATR behind the best price once 1.5 ATR ahead.
Port of FMZ strategy #489284 "多时间框架动量突破交易策略结合趋势跟踪与ATR风险管理-Multi-Timeframe-Momentum-Breakout-Trading-Strategy-with-Trend-Following-and-ATR-Risk-Management" (Ruben.Ramiro - Momentum Breakout Strategy).

FMZ source id: 489284

Source
    https://www.fmz.com/strategy/489284 (PineScript v6, FMZ last modified 2025-04-03 15:17:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 214-261), EMA 20 / 50, RSI 14 (70 / 30), breakout 5, ATR 14 x 1.5 / 1.5
    long = close > highest(high, 5)[1] and ema20 > ema50 and rsi < 70;  short = close < lowest(low, 5)[1] and ema20 < ema50 and rsi > 30
    in a position, every bar: exit(stop = avg price -+ 1.5 ATR, trail_points = trail_offset = 1.5 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-issued every bar from the average price and the current ATR (a moving level): mark
      trailing_stop_pending; the port fixes it at the signal bar's ATR: sl_stop = 1.5 x ATR / close, shifted one bar
      inside stops(), re-based on the fill.
    * trail_points / trail_offset take ticks; the author passes ATR price distances, read as price distances (as
      #427592). Ported natively (mark trailing_stop): {"type": "volatility", "atr_n": 14, "k": 1.5, "anchor":
      "high_low", "activate_after": 0.06}. Stated approximation: the 1.5-ATR activation becomes a 6 % gain (1.5
      daily ATR on the author's BNB_USDT; judgement before any backtest).
    * Every condition bar is an entry; entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (mark); the trail a house trail.
    2 generic: PASS, EMAs, RSI, channel breakouts and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the exits ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489284_breakout_ema_trend_atr_stop_trail"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "breakout": [5, 20],
    "atr_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"ema_fast": 20, "ema_slow": 50, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "breakout": 5,
                  "atr_len": 14, "atr_mult": 1.5, "trail_activate": 0.06}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["breakout"])
    res, sup = h.rolling(n).max().shift(1), lo.rolling(n).min().shift(1)
    long_e = ((c > res) & (ef > es) & (rsi < p["rsi_ob"])).astype(bool)
    short_e = ((c < sup) & (ef < es) & (rsi > p["rsi_os"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": frac.shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["atr_mult"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
