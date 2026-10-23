"""Broker days: OBV crossing over its 20-bar SMA with RSI 14 under 70 goes long, crossing under with RSI over 30 goes short; each trade gets a 2 % stop and a 4 % target from the signal close; reversing.
Port of FMZ strategy #473395 "基于OBV-SMA交叉和RSI过滤的多维度动量交易策略-OBV-SMA-Crossover-with-RSI-Filter-Multi-Dimensional-Momentum-Trading-Strategy" (OBV Strategy with SMA, RSI, SL and TP (Improved Visualization)).

FMZ source id: 473395

Source
    https://www.fmz.com/strategy/473395 (PineScript v5, FMZ last modified 2024-11-29 16:31:19).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 100-151), OBV = cum(sign(change) x volume); OBV SMA 20; RSI 14; SL 2 %, TP 4 % from the signal close
    longCondition = crossover(obv, obvSMA) and rsi < 70 -> entry Buy, exit("Take Profit/Stop Loss", "Buy", stop = close x 0.98, limit = close x 1.04)
    shortCondition = crossunder(obv, obvSMA) and rsi > 30 -> entry Sell, exit(same id, "Sell", stop = close x 1.02, limit = close x 0.96)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars only, as levels from that close: ported as fractions of the
      fill, exact (1e-6 floor). Both sides share one exit id, but the calls only happen on their own
      signal bars (which never coincide), so each trade keeps its own bracket until the opposite entry
      reverses it. The first bar's OBV step is 0. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, OBV / SMA crossings with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) in the OBV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473395_obv_sma20_cross_rsi_2_4pct_bracket_reversal"
FAMILY = "obv"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "obv_len": [20, 50],
    "sl": [0.02, 0.03],
}
DEFAULT_PARAMS = {"obv_len": 20, "sl": 0.02, "tp": 0.04}


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
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    obv = (np.sign(c.diff()) * v).fillna(0.0).cumsum()
    ma = obv.rolling(int(p["obv_len"])).mean()
    r = _rsi(c, 14)
    buy = (obv > ma) & (obv.shift(1) <= ma.shift(1)) & (r < 70)
    sell = (obv < ma) & (obv.shift(1) >= ma.shift(1)) & (r > 30)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    sl, tp = float(p["sl"]), float(p["tp"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl))
            .mask(sf, k * (1 + sl) - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
