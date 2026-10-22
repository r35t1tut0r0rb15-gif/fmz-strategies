"""EMA 9 / 21 crossings with RSI 14 under 70 / over 30 and the MACD 12 / 26 / 9 side, 2-day bars: the up-cross goes long and the down-cross goes short, each with a 1 % stop and a 2 % target from the fill; reversing.
Port of FMZ strategy #483124 "Multi Indicator Cross Intelligence Trend Trading Strategy" (BTCUSD Intraday - AI-like Strategy).

FMZ source id: 483124

Source
    https://www.fmz.com/strategy/483124 (PineScript v5, FMZ last modified 2025-02-27 16:54:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-205), EMA 9 / 21; RSI 14; MACD 12 / 26 / 9; target 2 %; stop 1 %; 10 % of equity, capital 10000, commission 0.1 %; MPL 2.0 notice (egidiopalmieri)
    crossover(ema9, ema21) and rsi < 70 and macd > signal -> entry Long;  crossunder and rsi > 30 and macd < signal -> entry Short
    position long -> exit(stop = avg x 0.99, limit = avg x 1.02);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent from the fill bar's close around the average price; it is ported as fixed
      fractions of the fill, active from the fill bar (as #440797). An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour:
      mark coarse_bar_stop. The 10 % of equity size and the capital are sizing; the commission is a cost
      (the house cost model applies). The MPL 2.0 notice is kept with the verbatim copy (ported, stated).
      Bars are blocks of two broker days (17:00 America/New_York) counted from 1970-01-01, stamped with
      their first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, EMA crossings with RSI and MACD filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483124_ema9_21_cross_rsi_macd_1_2pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_perc": [1.0, 2.0],
    "take_profit_perc": [2.0, 4.0],
}
DEFAULT_PARAMS = {"stop_loss_perc": 1.0, "take_profit_perc": 2.0, "ema_short": 9, "ema_long": 21, "rsi_period": 14,
                  "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    es, el = ema(c, p["ema_short"]), ema(c, p["ema_long"])
    r = _rsi(c, int(p["rsi_period"]))
    macd = ema(c, 12) - ema(c, 26)
    sig = ema(macd, 9)
    le = (es > el) & (es.shift(1) <= el.shift(1)) & (r < 70) & (macd > sig)
    se = (es < el) & (es.shift(1) >= el.shift(1)) & (r > 30) & (macd < sig)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss_perc"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["take_profit_perc"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
