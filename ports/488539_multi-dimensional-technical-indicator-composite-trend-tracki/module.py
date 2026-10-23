"""5-minute bars: an EMA 50 / 200 golden cross with RSI 14 between 40 and 65, the close above the session VWAP and the supertrend (2, 10) direction +1 (a DOWN-trend in Pine) goes long; the death-cross mirror (RSI 60-80, direction -1, an up-trend) goes short; each trade gets a 1.5 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #488539 "Multi Dimensional Technical Indicator Composite Trend Tracking Quantitative Trading Strategy" (Advanced BTC/USDT Strategy).

FMZ source id: 488539

Source
    https://www.fmz.com/strategy/488539 (PineScript v6, FMZ last modified 2025-03-28 17:22:09).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 117-194), EMA 50 / 200; RSI 14; supertrend 2 / 10; ATR 14 x 1.5, RR 2; session VWAP; 10 % of equity
    longCondition = crossover(ema50, ema200) and 40 < rsi < 65 and close > vwap and supertrendDirection == 1 -> entry Long, exit(limit = close + 3 atr, stop = close - 1.5 atr)
    shortCondition = crossunder(ema50, ema200) and 60 < rsi < 80 and close < vwap and supertrendDirection == -1 -> entry Short, exit(...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * In Pine's ta.supertrend a direction of +1 is the down-trend and -1 the up-trend, so the longs need a
      supertrend down-trend and the shorts an up-trend, as written (weird case). ta.vwap(close) restarts
      each session: the house session is the broker day (17:00 America/New_York). The bracket is sent on
      signal bars as levels from that close: ported as fractions of the fill, exact (1e-6 floor). The title
      names BTC/USDT; the header is ETH_USDT. REVERSAL INTENDED. 10 % of equity is sizing. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, golden / death crosses with RSI, VWAP and supertrend filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488539_golden_cross_rsi_vwap_supertrend_dir_atr_bracket_5m_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 2.5],
    "rr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"sl_atr": 1.5, "rr": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def _st_dir(bars_df, factor, period):
    """Direction of ta.supertrend (Pine reference implementation), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    c, v = bars_df["close"], bars_df["volume"]
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    r = _rsi(c, 14)
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    d = _st_dir(bars_df, 2.0, 10)
    buy = (e50 > e200) & (e50.shift(1) <= e200.shift(1)) & (r > 40) & (r < 65) & (c > vw) & (d == 1)
    sell = (e50 < e200) & (e50.shift(1) >= e200.shift(1)) & (r > 60) & (r < 80) & (c < vw) & (d == -1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    sl_d = float(p["sl_atr"]) * _atr(bars_df, 14)
    tp_d = sl_d * float(p["rr"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
