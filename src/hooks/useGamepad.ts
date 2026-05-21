import { useEffect } from 'react'
import { listen } from '@tauri-apps/api/event'

interface UseGamepadOptions {
  onAxisChange?: (axis: string, value: number) => void
  onButtonPress?: (button: string) => void
  onButtonRelease?: (button: string) => void
  deadZone?: number
}

const BUTTON_TO_KEY_MAP: Record<string, string> = {
  South: 'A', East: 'B', West: 'X', North: 'Y',
  DPadUp: '↑', DPadDown: '↓', DPadLeft: '←', DPadRight: '→',
  LeftTrigger: 'LT', RightTrigger: 'RT',
  LeftThumb: 'L3', RightThumb: 'R3',
  Start: 'Start', Select: 'Select',
}

export function useGamepad(options: UseGamepadOptions = {}) {
  const { onAxisChange, onButtonPress, onButtonRelease, deadZone = 0.15 } = options

  useEffect(() => {
    let active = true
    const setup = async () => {
      const unlisten = await listen<{
        type: string; axis?: string; value?: number; button?: string
      }>('gamepad-changed', (event) => {
        if (!active) return
        const { type, axis, value, button } = event.payload

        if (type === 'Axis' && axis != null && value != null) {
          if (Math.abs(value) < deadZone) {
            onAxisChange?.(axis, 0)
          } else {
            onAxisChange?.(axis, value)
          }
        }
        if (type === 'ButtonPress' && button) {
          onButtonPress?.(button)
          const mappedKey = BUTTON_TO_KEY_MAP[button]
          if (mappedKey) onButtonPress?.(`Gamepad_${mappedKey}`)
        }
        if (type === 'ButtonRelease' && button) {
          onButtonRelease?.(button)
          const mappedKey = BUTTON_TO_KEY_MAP[button]
          if (mappedKey) onButtonRelease?.(`Gamepad_${mappedKey}`)
        }
      })
      return unlisten
    }
    const cleanup = setup()
    return () => {
      active = false
      cleanup.then((f) => f?.())
    }
  }, [deadZone])
}
