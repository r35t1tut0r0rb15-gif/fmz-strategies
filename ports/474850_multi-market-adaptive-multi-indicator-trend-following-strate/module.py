"""Broker days: the Coppock curve (WMA 10 of ROC 11 + ROC 14) crossing over 0 with CMF 20 and the DPO 21 above 0 goes long, crossing under 0 with both below 0 goes short; each trade gets a 2 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #474850 "Multi Market Adaptive Multi Indicator Trend Following Strategy" (Multi-Market Adaptive Trading Strategy).

FMZ source id: 474850

Source
    https://www.fmz.com/strategy/474850 (PineScript v5, FMZ last modified 2024-12-12 15:23:28).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 116-189), CMF 20; DPO 21 (SMA shifted 11); Coppock 11 / 14 / 10; ATR 14; market type Crypto (factor 1.0); risk-based qty
    long_condition = cmf > 0 and dpo > 0 and coppock > 0 and crossover(coppock, 0);  and strategy.opentrades < 3 -> entry Long (qty = risk / (atr x factor) x leverage), exit(stop = close - 2 atr, limit = close + 3 atr)
    short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default market type is Crypto, so the volatility factor is 1.0 (stop 2 ATR, target 3 ATR).
      Default pyramiding holds one trade at a time, so "opentrades < 3" always holds. The bracket is sent
      on signal bars only, as levels from that close: ported as fractions of the fill, exact (1e-6
      floor). dpo_offset = floor(21 / 2) + 1 = 11 (Pine v5 divides to 10.5). The CMF's division by zero
      (high = low) is na. The risk-based quantity, leverage and 10 % of equity are sizing. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, Coppock zero crossings confirmed by CMF and DPO.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based qty, leverage and 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) in the CMF; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_474850_coppock_zero_cross_cmf_dpo_atr_bracket_reversal"
FAMILY = "coppock"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [2.0, 1.5],
    "tp_atr": [3.0, 4.5],
}
DEFAULT_PARAMS = {"cmf_len": 20, "dpo_len": 21, "roc_s": 11, "roc_l": 14, "wma_len": 10, "sl_atr": 2.0, "tp_atr": 3.0}


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


def _wma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)
        out[n - 1:] = sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    nc = int(p["cmf_len"])
    mfm = ((c - lo) - (h - c)) / (h - lo).where(h != lo)
    cmf = (mfm * v).rolling(nc).mean() / v.rolling(nc).mean()
    nd = int(p["dpo_len"])
    dpo = c - c.rolling(nd).mean().shift(nd // 2 + 1)
    rs, rl = int(p["roc_s"]), int(p["roc_l"])
    cop = _wma(100 * (c / c.shift(rs) - 1) + 100 * (c / c.shift(rl) - 1), int(p["wma_len"]))
    buy = (cmf > 0) & (dpo > 0) & (cop > 0) & (cop.shift(1) <= 0)
    sell = (cmf < 0) & (dpo < 0) & (cop < 0) & (cop.shift(1) >= 0)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
