import { useState, useEffect } from 'react'
import { listen } from '@tauri-apps/api/event'
import type { AffectionState } from '../types/affection'

const STORAGE_KEY = 'desktop-pet-affection'

function loadState(): AffectionState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore */ }
  return {
    totalInputs: 0, level: 0,
    unlockedExpressions: ['normal'], inputsToNext: 1000,
  }
}

function saveState(state: AffectionState) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function useAffection() {
  const [state, setState] = useState<AffectionState>(loadState)
  const [lastUnlocked, setLastUnlocked] = useState<string | null>(null)
  const [showUnlock, setShowUnlock] = useState(false)

  useEffect(() => {
    let active = true
    const setup = async () => {
      const unlisten = await listen<{ count: number }>(
        'affection-input',
        (event) => {
          if (!active) return
          setState((prev) => {
            const newTotal = prev.totalInputs + event.payload.count
            const newLevel = Math.floor(newTotal / 1000)
            const updated: AffectionState = {
              totalInputs: newTotal,
              level: newLevel,
              unlockedExpressions: [...prev.unlockedExpressions],
              inputsToNext: 1000 - (newTotal % 1000),
            }

            if (newLevel > prev.level) {
              const pool =
                updated.unlockedExpressions.length >= 6
                  ? ['love']
                  : ['angry','surprised','sad','annoyed','shocked']
                      .filter((e) => !updated.unlockedExpressions.includes(e))

              if (pool.length > 0) {
                const unlocked = pool[Math.floor(Math.random() * pool.length)]
                updated.unlockedExpressions.push(unlocked)
                setLastUnlocked(unlocked)
                setShowUnlock(true)
                setTimeout(() => { if (active) setShowUnlock(false) }, 3000)
              }
            }

            saveState(updated)
            return updated
          })
        },
      )
      return unlisten
    }
    const cleanup = setup()
    return () => {
      active = false
      cleanup.then((f) => f?.())
    }
  }, [])

  const progressPercent = Math.round(((state.totalInputs % 1000) / 1000) * 100)

  return {
    ...state, lastUnlocked, showUnlock, progressPercent,
  }
}
