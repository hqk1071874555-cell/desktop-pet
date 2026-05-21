import { useEffect, useRef, useCallback } from 'react'
import { listen } from '@tauri-apps/api/event'

interface UseDeviceOptions {
  onKeyPress?: (key: string) => void
  onKeyRelease?: (key: string) => void
  onMouseMove?: (x: number, y: number) => void
  onMousePress?: (button: string) => void
  onMouseRelease?: (button: string) => void
  autoReleaseDelay?: number
}

const TOGGLE_KEYS = new Set(['CapsLock', 'NumLock', 'ScrollLock'])

const KEY_NORMALIZE_MAP: Record<string, string> = {
  KeyA: 'A', KeyB: 'B', KeyC: 'C', KeyD: 'D', KeyE: 'E',
  KeyF: 'F', KeyG: 'G', KeyH: 'H', KeyI: 'I', KeyJ: 'J',
  KeyK: 'K', KeyL: 'L', KeyM: 'M', KeyN: 'N', KeyO: 'O',
  KeyP: 'P', KeyQ: 'Q', KeyR: 'R', KeyS: 'S', KeyT: 'T',
  KeyU: 'U', KeyV: 'V', KeyW: 'W', KeyX: 'X', KeyY: 'Y', KeyZ: 'Z',
  Digit0: '0', Digit1: '1', Digit2: '2', Digit3: '3', Digit4: '4',
  Digit5: '5', Digit6: '6', Digit7: '7', Digit8: '8', Digit9: '9',
  Space: 'Space', Enter: 'Enter', Backspace: 'Backspace',
  Tab: 'Tab', Escape: 'Esc',
  ShiftLeft: 'Shift', ShiftRight: 'Shift',
  ControlLeft: 'Ctrl', ControlRight: 'Ctrl',
  AltLeft: 'Alt', AltRight: 'Alt',
  MetaLeft: 'Win', MetaRight: 'Win',
  ArrowUp: '↑', ArrowDown: '↓', ArrowLeft: '←', ArrowRight: '→',
  F1: 'F1', F2: 'F2', F3: 'F3', F4: 'F4',
  F5: 'F5', F6: 'F6', F7: 'F7', F8: 'F8',
  F9: 'F9', F10: 'F10', F11: 'F11', F12: 'F12',
}

function normalizeKey(rawKey: string): string {
  return KEY_NORMALIZE_MAP[rawKey] ?? rawKey
}

export function useDevice(options: UseDeviceOptions = {}) {
  const {
    onKeyPress, onKeyRelease,
    onMouseMove, onMousePress, onMouseRelease,
    autoReleaseDelay = 200,
  } = options

  const releaseTimers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map())
  const isWindows = useRef(navigator.platform.includes('Win'))

  const handleAutoRelease = useCallback(
    (key: string, delay: number) => {
      const existing = releaseTimers.current.get(key)
      if (existing) clearTimeout(existing)
      const timer = setTimeout(() => {
        onKeyRelease?.(key)
        releaseTimers.current.delete(key)
      }, delay)
      releaseTimers.current.set(key, timer)
    },
    [onKeyRelease],
  )

  useEffect(() => {
    let active = true
    const setup = async () => {
      const unlisten = await listen<{
        kind: string; value?: string; x?: number; y?: number
      }>('device-changed', (event) => {
        if (!active) return
        const { kind, value, x, y } = event.payload

        if (kind === 'KeyboardPress' && value) {
          const key = normalizeKey(value)
          if (TOGGLE_KEYS.has(key)) {
            onKeyPress?.(key)
            handleAutoRelease(key, 100)
          } else if (isWindows.current) {
            onKeyPress?.(key)
            handleAutoRelease(key, autoReleaseDelay)
          } else {
            onKeyPress?.(key)
          }
        }
        if (kind === 'KeyboardRelease' && value) {
          const key = normalizeKey(value)
          if (!isWindows.current && !TOGGLE_KEYS.has(key)) {
            onKeyRelease?.(key)
          }
        }
        if (kind === 'MousePress' && value) onMousePress?.(value)
        if (kind === 'MouseRelease' && value) onMouseRelease?.(value)
        if (kind === 'MouseMove' && x != null && y != null) onMouseMove?.(x, y)
      })
      return unlisten
    }
    const cleanup = setup()
    return () => {
      active = false
      cleanup.then((f) => f?.())
      releaseTimers.current.forEach((t) => clearTimeout(t))
      releaseTimers.current.clear()
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps
}
