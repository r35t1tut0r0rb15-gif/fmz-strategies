"""Pullback buys in a long-term uptrend with volatility-unit exits, broker days, long only: with the RSI 200 above 51 and two closes in a row not above the one before, go long; close once a close is one "BHD unit"
(the 100-bar SMA of the 50-bar 2-sigma width) above the entry price, or two units below it.
Port of FMZ strategy #437022 "Dynamic Take Profit Following Trend Strategy" (Take Profit On Trend (by BHD_Trade_Bot)).

FMZ source id: 437022

Source
    https://www.fmz.com/strategy/437022 (PineScript v4, FMZ last modified 2023-12-29 16:06:54).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 129-199), RSI 200 > 51, two falling closes; BHD unit = sma(2 stdev(close, 50), 100); TP 1 unit, SL 2 units; backtest window 2021-2050
    entry = rsi(close, 200) > 51 and all_body_decrease(2) (close[i] <= close[i + 1] for i = 0, 1) -> entry long;  TAKE_PROFIT = close > avg price + bhd_unit;  STOP_LOSS = close < avg price - 2 bhd_unit -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The BHD unit is a volatility width in price units of the instrument itself, so it scales with it.
      The exits are tested on bar closes against the position's average price (the fill price, one
      entry): close-based exits from simulate() (rule 3). The backtest window and the "last bar" close
      (true only on a live last bar) are dropped. An entry while long is ignored (pyramiding 0). Long only.
      The cash order size and commission are sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits tested on closes.
    2 generic: PASS, volatility-unit exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash quantity, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437022_rsi200_pullback_bhd_exits"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [200, 100],
    "sl_units": [2.0, 1.0],
}
DEFAULT_PARAMS = {"rsi_len": 200, "sl_units": 2.0, "rsi_level": 51.0, "tp_units": 1.0, "bb_len": 50,
                  "unit_len": 100, "falling": 2}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    unit = (2 * c.rolling(int(p["bb_len"])).std(ddof=0)).rolling(int(p["unit_len"])).mean().to_numpy()
    k = int(p["falling"])
    fall = pd.Series(True, index=c.index)
    for i in range(k):
        fall = fall & ~(c.shift(i) > c.shift(i + 1))
    entry = ((r > float(p["rsi_level"])) & fall).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tpu, slu = float(p["tp_units"]), float(p["sl_units"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pos == 1 and i >= entry_i:
                e = ov[entry_i]
                if cv[i] > e + tpu * unit[i] or cv[i] < e - slu * unit[i]:
                    lx[i] = True
                    pos = 0
                    continue
            if pos == 0 and entry[i] and i + 1 < m:
                le[i] = True
                pos, entry_i = 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
