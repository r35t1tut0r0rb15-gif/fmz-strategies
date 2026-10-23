"""Broker days: the close crossing over the EMA 21 on volume 10 % above its EMA 21 with RSI 14 over 50 goes long; the close crossing under on volume below that threshold with RSI under 50 goes short; each with a stop 1.5 ATR 14 from the signal close; reversing.
Port of FMZ strategy #444002 "基于21日EMA成交量和RSI的趋势动量策略Trend-Momentum-Strategy-Based-on-21-EMA-Volume-and-RSI" (Enhanced 21 EMA Strategy with Volume and RSI).

FMZ source id: 444002

Source
    https://www.fmz.com/strategy/444002 (PineScript v5, FMZ last modified 2024-03-08 14:59:14).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 148-181), EMA 21; volume threshold 10 %; RSI 14; ATR 14 x 1.5
    buySignal = crossover(close, ema21) and volume > ema(volume, 21) x 1.1 and rsi > 50 -> entry Buy, exit("Sell", "Buy", stop = close - 1.5 x atr)
    sellSignal = crossunder(close, ema21) and volume < threshold and rsi < 50 -> entry Sell, exit("Buy", "Sell", stop = close + 1.5 x atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are sent on the signal bar only, as levels from that bar's close and ATR: ported as
      fractions of the fill, exact (a level the fill has passed is taken at once, 1e-6 floor). The exit
      ids reuse the entry names of the other side, as written. REVERSAL INTENDED. No sizing code. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at the signal close as a fraction of the fill.
    2 generic: PASS, EMA 21 crossings with volume and RSI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.1 x its EMA 21; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_444002_ema21_cross_volume_rsi_atr_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "vol_pct": [10, 25],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"vol_pct": 10, "rsi_len": 14, "atr_len": 14, "atr_mult": 1.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    ema = c.ewm(span=21, adjust=False).mean()
    thr = v.ewm(span=21, adjust=False).mean() * (1 + float(p["vol_pct"]) / 100)
    rsi = _rsi(c, int(p["rsi_len"]))
    buy = (c > ema) & (c.shift(1) <= ema.shift(1)) & (v > thr) & (rsi > 50)
    sell = (c < ema) & (c.shift(1) >= ema.shift(1)) & (v < thr) & (rsi < 50)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    dist = float(p["atr_mult"]) * _atr(bars_df, int(p["atr_len"]))
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_long = 1 - (c - dist).shift(1) / o
    sl_short = (c + dist).shift(1) / o - 1
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, sl_long).mask(sf, sl_short)
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
