"""RSI 14 crossing its 14-bar SMA, from flat, with close-checked exits and a two-loss lockout, 4-hour bars: RSI
crossing above its average goes long, below goes short; a close that falls an ATR-scaled trail below the best close,
the opposite cross, or a close beyond the 2.5 % target / 1.5 % stop from the signal close exits. After two counted
losses no new trade opens (the source's 09:15 reset never matches a 4-hour bar; the grid also tries a daily reset).
Port of FMZ strategy #491890 "RSI-MA-交叉摆动交易策略与追踪止损系统-RSI-MA-Crossover-Swing-Trading-Strategy-with-Trailing-Stop-System" (RX Swing).

FMZ source id: 491890

Source
    https://www.fmz.com/strategy/491890 (PineScript v5, FMZ last modified 2025-04-24 16:51:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 125-250), RSI 14, SMA 14 of RSI, SL 1.5 %, TP 2.5 %, trail 10 points
    entry (lossCount < 2, not in a trade): crossover(rsi, rsiMA) -> long, else crossunder -> short; entryPrice = close
    in trade: trailHigh = max(trailHigh, close); close <= trailHigh - 10 -> close, lossCount + 1 (shorts mirrored)
    opposite cross -> close (lossCount + 1 only if the position is on the other side: never)
    position open: close >= entry x 1.025 -> close (TP); close <= entry x 0.985 -> close, lossCount + 1 (shorts mirrored)
    hour == 9 and minute == 15 -> lossCount = 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * All exits are checked on bar closes: close-based exit signals (rule 3), never stops. The statements run in
      source order on each bar: entry block, trail, reversal, target / stop (the last only once the position is
      filled, i.e. from the bar after the entry signal), as written.
    * Criterion 2: the 10-point trail (Nifty option points per the inputs) becomes trail_atr x Wilder ATR(14) of
      the current bar (judgement before any backtest; on the author's DOGE_USDT the 10 points were unreachable).
    * Session open (check 9 / C6): the reset at 09:15 is in the chart's time zone; on 4-hour bars (UTC 00, 04, ...)
      no bar opens at 09:15 in UTC or in Asia/Kolkata, so as written the counter never resets and trading stops
      after the second counted loss (daily_reset False, the default). daily_reset True is the evident intent
      (NSE open 09:15 Asia/Kolkata): the counter resets on the first bar whose open is at or after 09:15
      Asia/Kolkata each day. Both are in the GRID (declared before any backtest).
    * The trail counts every trail exit as a loss, as written.
    * Entries only from flat: Opposite entries cannot occur. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked exits.
    2 generic: ADAPT, the point trail -> ATR multiple; percentage target and stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital per trade and lot size quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:15 Asia/Kolkata (NSE open; no DST) as the loss-counter reset, only with daily_reset True; never matched on 4-hour bars as written.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_491890_rsi_sma_cross_swing_lockout"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_atr": [1.0, 2.0],
    "daily_reset": [False, True],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ma_len": 14, "ma_type": "SMA", "sl_pct": 1.5, "tp_pct": 2.5, "trail_atr": 1.0,
                  "atr_len": 14, "max_losses": 2, "daily_reset": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _reset_bars(index):
    """First bar each Asia/Kolkata day whose open is at or after 09:15 local (the NSE open)."""
    loc = index.tz_convert("Asia/Kolkata")
    after = (loc.hour * 60 + loc.minute) >= 9 * 60 + 15
    day = loc.normalize()
    out = np.zeros(len(index), dtype=bool)
    seen = set()
    for i in range(len(index)):
        if after[i] and day[i] not in seen:
            out[i] = True
            seen.add(day[i])
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    ma = rsi.rolling(int(p["ma_len"])).mean() if p["ma_type"] == "SMA" else rsi.ewm(span=int(p["ma_len"]),
                                                                                      adjust=False).mean()
    up = ((rsi > ma) & (rsi.shift(1) <= ma.shift(1))).to_numpy()
    dn = ((rsi < ma) & (rsi.shift(1) >= ma.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    trail = (p["trail_atr"] * _atr(bars_df, int(p["atr_len"]))).to_numpy(dtype=float)
    reset = _reset_bars(bars_df.index) if p["daily_reset"] else np.zeros(len(cv), dtype=bool)
    tp, sl = p["tp_pct"] / 100, p["sl_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    in_trade, side, entry, best, losses, held = False, 0, np.nan, np.nan, 0, 0
    for i in range(m):
        exit_now = False
        if losses < p["max_losses"] and not in_trade:
            if up[i]:
                in_trade, side, entry, best = True, 1, cv[i], cv[i]
            elif dn[i]:
                in_trade, side, entry, best = True, -1, cv[i], cv[i]
        filled = held                          # strategy.position_size: the position held at this bar
        if in_trade and side == 1:
            best = max(best, cv[i])
            if cv[i] <= best - trail[i]:
                exit_now, in_trade, losses = True, False, losses + 1
        if in_trade and side == -1:
            best = min(best, cv[i])
            if cv[i] >= best + trail[i]:
                exit_now, in_trade, losses = True, False, losses + 1
        if in_trade and ((side == 1 and dn[i]) or (side == -1 and up[i])):
            exit_now, in_trade = True, False
        if in_trade and filled == 1:
            if cv[i] >= entry * (1 + tp):
                exit_now, in_trade = True, False
            elif cv[i] <= entry * (1 - sl):
                exit_now, in_trade, losses = True, False, losses + 1
        if in_trade and filled == -1:
            if cv[i] <= entry * (1 - tp):
                exit_now, in_trade = True, False
            elif cv[i] >= entry * (1 + sl):
                exit_now, in_trade, losses = True, False, losses + 1
        if reset[i]:
            losses = 0
        tgt[i] = side if in_trade else 0
        held = side if (in_trade and not exit_now) else 0
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
