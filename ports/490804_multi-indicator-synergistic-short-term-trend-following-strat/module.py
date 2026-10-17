"""MACD 6 / 13 / 6 crosses on the EMA 20 side with an RSI band, a 1 % target and an ATR trail, broker days: a MACD
cross up with the close above EMA 20 and RSI 9 between 40 and 75 goes long; a cross down below EMA 20 with RSI under
60 goes short; each trade has a 1 % target and a trail 0.8 ATR behind the best price.
Port of FMZ strategy #490804 "多指标协同短线趋势跟踪策略-Multi-Indicator-Synergistic-Short-Term-Trend-Following-Strategy" (Scalping Pro Balance (EMA + MACD + RSI + Trailing TP)).

FMZ source id: 490804

Source
    https://www.fmz.com/strategy/490804 (PineScript v5, FMZ last modified 2025-04-16 15:56:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 167-194), EMA 20, MACD 6 / 13 / 6, RSI 9, TP 1 %, trail 0.8 x ATR(14)
    long = close > ema and crossover(macd, signal) and 40 < rsi < 75;  short = close < ema and crossunder and rsi < 60
    on entry: exit(limit = close x (1 +- 1 %), trail_points = trail_offset = ATR x 0.8)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is placed on the signal bar: tp_stop 1 % of the fill (scalar, house rule).
    * trail_points / trail_offset take ticks; the author passes ATR price distances, read as price distances (as
      #427592): from 0.8 ATR of profit a stop 0.8 ATR behind the best price. Ported natively (mark trailing_stop):
      {"type": "volatility", "atr_n": 14, "k": 0.8, "anchor": "high_low", "activate_after": 0.024}. Stated
      approximations: the distances are fixed at the entry bar's ATR in Pine; the 0.8-ATR activation becomes a 2.4 %
      gain (0.8 daily ATR on the author's BTC_USDT; judgement before any backtest), so on that market the 1 % target
      usually comes first, as in the source.
    * Every signal bar is an entry; entries reverse (REVERSAL INTENDED). A long and a short cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at the signal bar; the trail a house trail (approximations stated).
    2 generic: PASS, EMA, MACD, RSI, a percentage and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the exits ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_490804_macd_ema_rsi_target_atr_trail"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [1.0, 3.0],
    "atr_mult": [0.8, 1.6],
}
DEFAULT_PARAMS = {"ema_len": 20, "rsi_len": 9, "tp_pct": 1.0, "atr_mult": 0.8, "atr_len": 14,
                  "trail_activate": 0.024}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=6, adjust=False).mean() - c.ewm(span=13, adjust=False).mean()
    sig = macd.ewm(span=6, adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    long_e = ((c > ema) & up & (rsi > 40) & (rsi < 75)).astype(bool)
    short_e = ((c < ema) & dn & (rsi < 60)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": p["tp_pct"] / 100,
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["atr_mult"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
