"""EMA 8 / 21 golden crosses with ADX above 25, MACD above its signal and RSI below 70, long only, with a 1.5 ATR stop,
a 2 ATR target and a 0.3 ATR trail after 0.5 ATR of profit, daily bars.
Port of FMZ strategy #482767 "多指标交叉动态止盈止损趋势跟踪策略-Multi-Indicator-Crossover-Dynamic-Stop-Loss-Trend-Following-Strategy" (Optimized Long-Only Strategy (Spot Market) - Candle Signals Only).

FMZ source id: 482767

Source
    https://www.fmz.com/strategy/482767 (PineScript v6, FMZ last modified 2025-02-27 17:52:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 107-151), EMA 8 / 21, RSI 14 (< 70), ADX 14 (> 25, RMA of DX), MACD
12 / 26 / 9, ATR 14 (stop 1.5, target 2)
    crossover(ema8, ema21) and adx > 25 and macd > signal and rsi < 70 -> entry long with
    exit(stop = close - 1.5 ATR, limit = close + 2 ATR, trail_points = 0.5 ATR, trail_offset = 0.3 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: 1.5 ATR / close and 2 ATR / close, shifted one bar
      inside stops() and re-based on the fill (house rule).
    * trail_points / trail_offset take ticks; the author passes ATR price distances, read as price distances (as
      #427592): the house trail {"type": "volatility", "atr_n": 14, "k": 0.3, "anchor": "high_low",
      "activate_after": 0.02}, the 0.5 ATR activation judged on the author's market (ETH_USDT daily ATR about 4 % of
      the price, so about 2 %; as #428795). Mark trailing_stop.
    * DI and ADX as written (RMA smoothing of ta.tr(true), no fixnan). barstate.isconfirmed is true on history.
    * Long only; no exit signal. Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the bracket and trail set at entry.
    2 generic: PASS, EMAs, ADX, MACD, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and the 0.1 % commission; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482767_ema8_21_cross_adx_macd_rsi_atr_bracket_trail_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 2.5],
    "tp_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 21, "rsi_len": 14, "rsi_ob": 70.0, "adx_len": 14, "adx_min": 25.0,
                  "atr_len": 14, "sl_mult": 1.5, "tp_mult": 2.0, "trail_k": 0.3, "trail_activate": 0.02}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # ta.tr(true) / Pine's first true range is high - low
    return tr


def _atr(bars_df, n):
    return _rma(_tr(bars_df), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    n = int(p["adx_len"])
    atr_v = _atr(bars_df, n)
    plus_di = 100 * _rma(plus_dm, n) / atr_v
    minus_di = 100 * _rma(minus_dm, n) / atr_v
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = _rma(dx, n)
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (adx > p["adx_min"]) & (macd > sig)
              & (rsi < p["rsi_ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a,
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
