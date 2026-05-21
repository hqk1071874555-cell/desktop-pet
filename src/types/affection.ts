export interface AffectionState {
  totalInputs: number
  level: number
  unlockedExpressions: string[]
  inputsToNext: number
}

export const EXPRESSION_NAMES: Record<string, string> = {
  normal: '普通微笑',
  love: '爱心眼',
  angry: '愤怒冒火',
  surprised: '惊讶',
  sad: '悲伤',
  annoyed: '翻白眼',
  shocked: '惊恐灰白',
}
