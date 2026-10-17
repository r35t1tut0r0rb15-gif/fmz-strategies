"""EMA 5 / SMA 10 golden crosses, long only, closed at a death cross or an RSI 14 below 50, three-day bars.
Port of FMZ strategy #482832 "双均线交叉结合RSI强弱过滤交易策略-Dual-Moving-Average-Crossover-with-RSI-Strength-Filter-Trading-Strategy" (EMA and SMA Crossover with RSI14 Filtering).

FMZ source id: 482832

Source
    https://www.fmz.com/strategy/482832 (PineScript v5, FMZ last modified 2025-02-20 14:50:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 165-226), EMA 5, SMA 10, RSI 14 (60 / 50)
    crossover(ema5, sma10) and not active_buy: enter long unless close < rsi14 (nested test that can never pass);
    active_buy := true
    crossunder(ema5, sma10) and not active_sell: enter short unless close > rsi14; active_sell := true
    active_buy and (crossunder or rsi < 50) -> close long, active_buy := false
    active_sell and (crossover or rsi > 60) -> close short, active_sell := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The filters compare the PRICE with the RSI value (a price level, criterion 2). On the author's ETH_USDT the close
      is always above any RSI: the long filter always passes (dropped as inert) and the short entry can never fire
      (dropped with it, as #492009 / #490798). The port is long only.
    * The flag active_buy is kept as written: it blocks a new cross while set and is cleared by the close test even on
      the entry's own bar, where the close cannot undo the entry (#430850); the position is then held until a later
      cross sets the flag again and the close test fires.
    * Signal module, no stops. Three-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as
      #426509); FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an EMA, an SMA and RSI levels (the price-vs-RSI filters are inert and dropped).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in three-day blocks; no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482832_ema5_sma10_cross_rsi50_exit_long_3d"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [10, 20],
    "rsi_exit": [50.0, 40.0],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 10, "rsi_len": 14, "rsi_exit": 50.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=3):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    weak = (_rsi(c, int(p["rsi_len"])) < p["rsi_exit"]).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, active = 0, False
    for i in range(m):
        start = pos
        if up[i] and not active:
            if pos != 1:
                le[i], pos = True, 1
            active = True
        if active and (dn[i] or weak[i]):
            if start == 1 and pos == 1:
                lx[i], pos = True, 0
            active = False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
