/**
 * useIdleTimeout (S001-F-007)
 *
 * Watches user activity (mousemove, keydown, scroll, click) and fires a
 * caller-supplied callback when no activity occurs for ``minutes`` minutes.
 *
 * The default timeout is read from VITE_SESSION_IDLE_TIMEOUT_MINUTES so the
 * sprint-1 demo can be reconfigured without a rebuild. If the env var is unset
 * or unparsable the hook falls back to 10 minutes, matching the backend
 * SESSION_IDLE_TIMEOUT_MINUTES default in backend/config.py.
 */
import { useEffect, useRef } from 'react';

const ACTIVITY_EVENTS: Array<keyof WindowEventMap> = [
  'mousemove',
  'keydown',
  'scroll',
  'click',
];

const DEFAULT_TIMEOUT_MINUTES = 10;

function resolveTimeoutMinutes(override?: number): number {
  if (typeof override === 'number' && Number.isFinite(override) && override > 0) {
    return override;
  }
  const raw = import.meta.env.VITE_SESSION_IDLE_TIMEOUT_MINUTES;
  if (typeof raw === 'string' && raw.trim() !== '') {
    const parsed = Number(raw);
    if (Number.isFinite(parsed) && parsed > 0) {
      return parsed;
    }
  }
  return DEFAULT_TIMEOUT_MINUTES;
}

/**
 * Register an idle-timeout watcher.
 *
 * @param onTimeout - invoked when ``minutes`` elapses with no user activity.
 * @param minutes  - optional override; falls back to
 *                   VITE_SESSION_IDLE_TIMEOUT_MINUTES, then 10.
 */
export function useIdleTimeout(
  onTimeout: () => void,
  minutes?: number,
): void {
  const callbackRef = useRef(onTimeout);
  callbackRef.current = onTimeout;

  useEffect(() => {
    const timeoutMinutes = resolveTimeoutMinutes(minutes);
    const timeoutMs = Math.round(timeoutMinutes * 60 * 1000);

    let timerId: ReturnType<typeof setTimeout> | null = null;

    const fireTimeout = () => {
      timerId = null;
      try {
        callbackRef.current();
      } catch (err) {
        // Don't let a buggy callback take down the listener cleanup path.
        console.error('useIdleTimeout callback threw:', err);
      }
    };

    const resetTimer = () => {
      if (timerId !== null) {
        clearTimeout(timerId);
      }
      timerId = setTimeout(fireTimeout, timeoutMs);
    };

    // Start the clock immediately and reset it on any tracked activity.
    resetTimer();
    for (const event of ACTIVITY_EVENTS) {
      window.addEventListener(event, resetTimer, { passive: true });
    }

    return () => {
      if (timerId !== null) {
        clearTimeout(timerId);
        timerId = null;
      }
      for (const event of ACTIVITY_EVENTS) {
        window.removeEventListener(event, resetTimer);
      }
    };
  }, [minutes]);
}

export default useIdleTimeout;
