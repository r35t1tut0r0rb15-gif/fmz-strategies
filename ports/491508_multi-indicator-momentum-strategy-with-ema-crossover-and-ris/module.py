"""EMA 9 / 21 crosses confirmed by RSI 50 and MACD, with a 1 % / 2 % bracket, broker days: EMA 9 crossing above
EMA 21 with RSI 14 above 50 and the MACD line above its signal goes long; the mirror goes short; each trade has a
1 % stop and a 2 % target.
Port of FMZ strategy #491508 "均线交叉与多指标动量风险控制策略-Multi-Indicator-Momentum-Strategy-with-EMA-Crossover-and-Risk-Management" (Estrategia EMAs + RSI + MACD con SL y TP).

FMZ source id: 491508

Source
    https://www.fmz.com/strategy/491508 (PineScript v5, FMZ last modified 2025-04-21 16:00:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 200-233), EMA 9 / 21, RSI 14, MACD 12 / 26 / 9, SL 1 %, TP 2 %
    long = crossover(ema9, ema21) and rsi > 50 and macd > signal;  short = crossunder(...) and rsi < 50 and macd < signal
    on entry: exit(stop = close x (1 -+ 1 %), limit = close x (1 +- 2 %)), levels from the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop 1 %, tp_stop 2 %, re-based on the fill price (house
      rule; scalars).
    * Entries reverse (REVERSAL INTENDED); a long and a short cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, EMAs, oscillators and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_491508_ema_cross_rsi_macd_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"ema_short": 9, "ema_long": 21, "rsi_len": 14, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
                  "sl_pct": 1.0, "tp_pct": 2.0}


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
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    long_e = ((es > el) & (es.shift(1) <= el.shift(1)) & (rsi > 50) & (macd > sig)).astype(bool)
    short_e = ((es < el) & (es.shift(1) >= el.shift(1)) & (rsi < 50) & (macd < sig)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
