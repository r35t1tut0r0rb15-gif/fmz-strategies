"""Four-hour bars: MACD crossing over its signal with the close above the EMA 50 and the session VWAP and RSI 14 under 70 goes long, the mirror short; a MACD cross back or a close through the EMA 50 closes each; a trailing stop half a tick behind the best price ends it almost at once; reversing.
Port of FMZ strategy #452276 "Dynamic Trend Momentum Trading Strategy" (Intraday Strategy (MACD / EMA 50 / RSI / VWAP)).

FMZ source id: 452276

Source
    https://www.fmz.com/strategy/452276 (PineScript v5, FMZ last modified 2024-05-23 17:57:22).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 97-144), EMA 50; MACD 12 / 26 / 9; RSI 14, 70 / 30; vwap(close); trailing offset 0.5 (ticks), trail price = close
    longCondition = crossover(macd, signal) and close > ema50 and rsi < 70 and close > vwap -> entry Long (qty 1);  shortCondition mirror -> entry Short
    longExitCondition = crossunder(macd, signal) or close < ema -> close Long;  position_size > 0 -> exit("Trailing Stop Long", trail_price = close, trail_offset = 0.5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_offset is in ticks: half a tick (0.05 on the header's BTC_USDT, about 66000 USD in the
      2024-04 window), so the trailing stop sits 7.6e-7 of the price behind the best minute high / low
      and closes the trade on the first tiny pullback (weird case). The trail activates at the latest
      close and is re-sent every bar; the port activates it at the fill (mark trailing_stop_pending).
      vwap(close) is the session VWAP, anchored at the broker-day start (as earlier ports). A close acts
      only on a position the bar's entries leave unchanged. qty 1 is sizing. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark coarse_bar_stop. FREQ = "4h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail from the fill.
    2 generic: PASS, MACD crossings with EMA, RSI and VWAP filters.
    3 crypto-exchange-only: no (exchange pair in the header only; the tick offset converted at the source's BTC price).
    4 signals only: entry qty 1 unit, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session VWAP's weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452276_macd_cross_ema50_rsi_vwap_half_tick_trail_4h_reversal"
FAMILY = "macd_variant"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [7.6e-07, 0.01],
    "ema_len": [50, 100],
}
DEFAULT_PARAMS = {"ema_len": 50, "rsi_len": 14, "ob": 70.0, "os": 30.0, "trail_pct": 7.6e-07}


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


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vwap = (c * v).groupby(day).cumsum() / cv.where(cv != 0)
    x_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    x_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    lg = (x_up & (c > ema) & (rsi < float(p["ob"])) & (c > vwap)).to_numpy()
    sh = (x_dn & (c < ema) & (rsi > float(p["os"])) & (c < vwap)).to_numpy()
    xl = (x_dn | (c < ema)).to_numpy()
    xs = (x_up | (c > ema)).to_numpy()
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and xl[i]:
                new = 0
            elif pos == -1 and xs[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
