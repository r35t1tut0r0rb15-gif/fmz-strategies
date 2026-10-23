"""Broker days: EMA 9 over EMA 21 with the MACD line above its signal and above 0, volume above its 14-bar average, RSI 14 between 40 and 70 and the close above the EMA 9 goes long; the mirror goes short; only the short keeps the shared tick bracket (stop 200, target 400 ticks, converted to fractions of the fill); reversing.
Port of FMZ strategy #473382 "Multi Trend Momentum Crossover Strategy with Volatility Optimization System" (Estrategia Cripto - 1D).

FMZ source id: 473382

Source
    https://www.fmz.com/strategy/473382 (PineScript v5, FMZ last modified 2024-11-29 16:07:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 112-153), EMA 9 / 21; MACD 12 / 26 / 9; RSI 14; volume SMA 14; exit loss 200 / profit 400 ticks under one shared id
    longCondition = ema9 > ema21 and macd > signal and macd > 0 and volume > volMedio and 40 < rsi < 70 and close > ema9 -> entry Compra
    shortCondition = mirrored (rsi 30 .. 60) -> entry Venda
    exit("Take Profit/Stop Loss", from_entry = "Compra", loss = 200, profit = 400);  exit(same id, from_entry = "Venda", loss = 200, profit = 400)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exit calls share one id and run on every bar, so the second (from_entry "Venda") replaces the
      first: only shorts get the bracket; longs end only by reversal (as #438480). profit / loss are ticks
      from the entry price: on the header's BTC_USDT (0.1 tick, about 96000 USD at the window's end,
      2024-11-27) 40 / 20 USD, ported as fractions of the fill 4.167e-4 / 2.083e-4 (as #437390); over
      the five-year window that distance in percent varied more than tenfold, and on 1-day bars it is
      touched within a day almost always (weird case). The entries are states (an entry while in that
      position adds nothing). The Bollinger Bands only plot. REVERSAL INTENDED. No sizing code. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed tick bracket from the fill (short only).
    2 generic: PASS, EMA / MACD / RSI trend agreement on above-average volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 14; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473382_ema_macd_rsi_volume_state_short_tick_bracket_reversal"
FAMILY = "trend_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [4.167e-04, 8.333e-04],
    "sl": [2.083e-04, 4.167e-04],
}
DEFAULT_PARAMS = {"tp": 4.167e-04, "sl": 2.083e-04}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    c, v = bars_df["close"], bars_df["volume"]
    e9, e21 = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(14).mean()
    buy = (e9 > e21) & (macd > sig) & (macd > 0) & vol_ok & (r > 40) & (r < 70) & (c > e9)
    sell = (e9 < e21) & (macd < sig) & (macd < 0) & vol_ok & (r < 60) & (r > 30) & (c < e9)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    short_fill = se.shift(1, fill_value=False)          # only the 'Venda' entry keeps the shared exit
    sl_f = pd.Series(float(p["sl"]), index=bars_df.index).where(short_fill)
    tp_f = pd.Series(float(p["tp"]), index=bars_df.index).where(short_fill)
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
