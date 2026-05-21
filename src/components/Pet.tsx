import { useState, useRef, useEffect, useCallback } from 'react'
import { useDevice } from '../hooks/useDevice'
import { useGamepad } from '../hooks/useGamepad'
import { useAffection } from '../hooks/useAffection'
import { AffectionBar } from './AffectionBar'
import { KeyOverlay } from './KeyOverlay'

// 表情对应的贴图路径（使用拆分结果中的表情图片）
const EXPRESSION_IMAGES: Record<string, string> = {
  normal: '/assets/character_original.jpg',
  love: '/assets/character_original.jpg',
  angry: '/assets/character_original.jpg',
  surprised: '/assets/character_original.jpg',
  sad: '/assets/character_original.jpg',
  annoyed: '/assets/character_original.jpg',
  shocked: '/assets/character_original.jpg',
}

export default function Pet() {
  const [currentExpression, setCurrentExpression] = useState('normal')
  const [pressedKeys, setPressedKeys] = useState<string[]>([])
  const [bounce, setBounce] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const isDragging = useRef(false)
  const dragStart = useRef({ x: 0, y: 0, posX: 0, posY: 0 })

  const pressedKeysRef = useRef<Set<string>>(new Set())
  const {
    unlockedExpressions,
    level,
  } = useAffection()

  // 键盘处理
  useDevice({
    onKeyPress: (key) => {
      pressedKeysRef.current.add(key)
      setPressedKeys(Array.from(pressedKeysRef.current))
      setBounce(true)
      setTimeout(() => setBounce(false), 150)
    },
    onKeyRelease: (key) => {
      pressedKeysRef.current.delete(key)
      setPressedKeys(Array.from(pressedKeysRef.current))
    },
    onMouseMove: (_x, _y) => {},
    onMousePress: (_button) => {
      // 左键点击切换表情
      toggleExpression()
    },
    onMouseRelease: (_button) => {},
    autoReleaseDelay: 200,
  })

  // 手柄处理
  useGamepad({
    deadZone: 0.15,
    onAxisChange: (_axis, _value) => {},
    onButtonPress: (button) => {
      pressedKeysRef.current.add(`🎮${button}`)
      setPressedKeys(Array.from(pressedKeysRef.current))
      setBounce(true)
      setTimeout(() => setBounce(false), 150)
    },
    onButtonRelease: (button) => {
      pressedKeysRef.current.delete(`🎮${button}`)
      setPressedKeys(Array.from(pressedKeysRef.current))
    },
  })

  // 随机切换表情（排除当前）
  const toggleExpression = useCallback(() => {
    if (unlockedExpressions.length <= 1) return
    const others = unlockedExpressions.filter((e) => e !== currentExpression)
    const next = others[Math.floor(Math.random() * others.length)]
    setCurrentExpression(next)
    setBounce(true)
    setTimeout(() => setBounce(false), 300)
  }, [unlockedExpressions, currentExpression])

  // 拖拽处理
  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true
    dragStart.current = { x: e.clientX, y: e.clientY, posX: position.x, posY: position.y }
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return
      const dx = e.clientX - dragStart.current.x
      const dy = e.clientY - dragStart.current.y
      setPosition({ x: dragStart.current.posX + dx, y: dragStart.current.posY + dy })
    }
    const handleMouseUp = () => {
      isDragging.current = false
    }
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [])

  return (
    <div style={{
      width: '100%',
      height: '100%',
      position: 'relative',
      background: 'transparent',
      overflow: 'hidden',
    }}>
      {/* 角色显示区域 */}
      <div
        onMouseDown={handleMouseDown}
        style={{
          position: 'absolute',
          left: '50%',
          top: '45%',
          transform: `translate(-50%, -50%) translate(${position.x}px, ${position.y}px)`,
          cursor: 'grab',
          transition: bounce ? 'none' : 'transform 0.2s ease',
        }}
      >
        {/* 角色图像 */}
        <div style={{
          width: 200,
          height: 280,
          borderRadius: 16,
          overflow: 'hidden',
          background: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(4px)',
          border: '1px solid rgba(255,255,255,0.2)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <img
            src={EXPRESSION_IMAGES[currentExpression]}
            alt="desktop pet"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: '70% 40%',
            }}
            draggable={false}
          />
        </div>

        {/* 等级标签 */}
        <div style={{
          position: 'absolute',
          top: -12,
          right: -8,
          background: 'linear-gradient(135deg, #ff6b9d, #ffa751)',
          color: '#fff',
          fontSize: 11,
          fontWeight: 700,
          padding: '2px 10px',
          borderRadius: 10,
          boxShadow: '0 2px 8px rgba(255,107,157,0.4)',
        }}>
          Lv.{level}
        </div>

        {/* 当前表情标签 */}
        <div style={{
          position: 'absolute',
          bottom: -8,
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'rgba(0,0,0,0.7)',
          color: '#fff',
          fontSize: 10,
          padding: '2px 10px',
          borderRadius: 8,
        }}>
          {currentExpression}
        </div>
      </div>

      {/* 按键叠加层 */}
      {pressedKeys.length > 0 && (
        <KeyOverlay keys={pressedKeys} />
      )}

      {/* 好感度条 */}
      <AffectionBar />

      {/* 点击提示 */}
      <div style={{
        position: 'absolute',
        bottom: 60,
        width: '100%',
        textAlign: 'center',
        color: 'rgba(255,255,255,0.3)',
        fontSize: 10,
        pointerEvents: 'none',
      }}>
        点击角色切换表情 · 拖动移动位置
      </div>
    </div>
  )
}
