import { useAffection } from '../hooks/useAffection'
import { EXPRESSION_NAMES } from '../types/affection'

const EMOJIS: Record<string, string> = {
  normal: '😊', love: '😍', angry: '😠',
  surprised: '😲', sad: '😢', annoyed: '🙄', shocked: '😱',
}

export function AffectionBar() {
  const {
    level, totalInputs, inputsToNext, progressPercent,
    unlockedExpressions, showUnlock, lastUnlocked,
  } = useAffection()

  return (
    <div style={{
      position: 'absolute',
      bottom: 8,
      left: '50%',
      transform: 'translateX(-50%)',
      width: 220,
      background: 'rgba(0,0,0,0.6)',
      backdropFilter: 'blur(8px)',
      borderRadius: 12,
      padding: '8px 12px',
      color: '#fff',
      fontSize: 11,
      fontFamily: 'system-ui, sans-serif',
      pointerEvents: 'none',
    }}>
      {/* 等级 + 次数 */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', marginBottom: 4,
      }}>
        <span style={{ color: '#ff6b9d', fontWeight: 700 }}>❤️ Lv.{level}</span>
        <span style={{ opacity: 0.7 }}>{totalInputs} 次</span>
      </div>

      {/* 进度条 */}
      <div style={{
        width: '100%', height: 6, background: 'rgba(255,255,255,0.15)',
        borderRadius: 3, overflow: 'hidden', marginBottom: 4,
      }}>
        <div style={{
          width: `${progressPercent}%`, height: '100%',
          background: 'linear-gradient(90deg, #ff6b9d, #ffa751)',
          borderRadius: 3, transition: 'width 0.3s ease',
        }} />
      </div>

      <div style={{ textAlign: 'center', opacity: 0.5, fontSize: 9 }}>
        距下一级还需 {inputsToNext} 次
      </div>

      {/* 表情列表 */}
      <div style={{
        display: 'flex', gap: 4, marginTop: 6, justifyContent: 'center', flexWrap: 'wrap',
      }}>
        {unlockedExpressions.map((id) => (
          <span key={id} title={EXPRESSION_NAMES[id]}
            style={{ fontSize: 15, cursor: 'default' }}>
            {EMOJIS[id]}
          </span>
        ))}
        {Array.from({ length: 7 - unlockedExpressions.length }).map((_, i) => (
          <span key={i} style={{ fontSize: 15, opacity: 0.25, filter: 'grayscale(1)' }}>
            🔒
          </span>
        ))}
      </div>

      {/* 解锁提示 */}
      {showUnlock && lastUnlocked && (
        <div style={{
          position: 'absolute', top: -45, left: '50%',
          transform: 'translateX(-50%)',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          color: '#fff', padding: '6px 14px', borderRadius: 20,
          fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap',
          boxShadow: '0 4px 15px rgba(102,126,234,0.4)',
          animation: 'unlockPop 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55)',
        }}>
          🎉 {EXPRESSION_NAMES[lastUnlocked]} {EMOJIS[lastUnlocked]}
        </div>
      )}

      <style>{`
        @keyframes unlockPop {
          0% { opacity: 0; transform: translateX(-50%) translateY(15px) scale(0.5); }
          50% { transform: translateX(-50%) translateY(-8px) scale(1.1); }
          100% { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
        }
      `}</style>
    </div>
  )
}
