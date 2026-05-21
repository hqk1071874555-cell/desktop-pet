interface KeyOverlayProps {
  keys: string[]
}

export function KeyOverlay({ keys }: KeyOverlayProps) {
  return (
    <div style={{
      position: 'absolute',
      bottom: 80,
      left: '50%',
      transform: 'translateX(-50%)',
      display: 'flex',
      gap: 4,
      flexWrap: 'wrap',
      justifyContent: 'center',
      maxWidth: 280,
      pointerEvents: 'none',
    }}>
      {keys.slice(0, 12).map((key) => (
        <span key={key} style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          minWidth: 24, height: 24,
          padding: '0 5px',
          borderRadius: 5,
          background: 'rgba(255,255,255,0.15)',
          backdropFilter: 'blur(4px)',
          color: '#fff',
          fontSize: 11,
          fontWeight: 600,
          fontFamily: 'monospace',
          border: '1px solid rgba(255,255,255,0.25)',
          animation: 'keyPopIn 0.15s ease-out',
        }}>
          {key.startsWith('Gamepad_') ? key.replace('Gamepad_', '🎮') : key}
        </span>
      ))}
      <style>{`
        @keyframes keyPopIn {
          0% { transform: scale(0.5); opacity: 0; }
          100% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  )
}
