use serde::{Deserialize, Serialize};
use rand::seq::SliceRandom;
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AffectionState {
    pub total_inputs: u64,
    pub level: u32,
    pub unlocked_expressions: Vec<String>,
    pub inputs_to_next: u32,
    expression_pool: Vec<String>,
}

impl Default for AffectionState {
    fn default() -> Self {
        Self {
            total_inputs: 0,
            level: 0,
            unlocked_expressions: vec!["normal".to_string()],
            inputs_to_next: 1000,
            expression_pool: vec![
                "love".to_string(),
                "angry".to_string(),
                "surprised".to_string(),
                "sad".to_string(),
                "annoyed".to_string(),
                "shocked".to_string(),
            ],
        }
    }
}

impl AffectionState {
    /// 记录输入。返回 Some(表情名) 表示解锁了新表情
    pub fn add_input(&mut self, count: f32) -> Option<String> {
        self.total_inputs = (self.total_inputs as f32 + count) as u64;
        let new_level = (self.total_inputs / 1000) as u32;

        if new_level > self.level {
            self.level = new_level;

            // 前 6 级：从非 love 的待解锁表情中随机选
            // 第 7 级（只剩 love 时）：解锁 love
            let pool: Vec<&String> = if self.unlocked_expressions.len() >= 6 {
                self.expression_pool
                    .iter()
                    .filter(|e| **e == "love")
                    .collect()
            } else {
                self.expression_pool
                    .iter()
                    .filter(|e| **e != "love" && !self.unlocked_expressions.contains(e))
                    .collect()
            };

            let unlocked = pool.choose(&mut rand::thread_rng()).map(|s| s.to_string());

            if let Some(ref expr) = unlocked {
                self.unlocked_expressions.push(expr.clone());
            }

            self.inputs_to_next = 1000 - (self.total_inputs % 1000) as u32;
            return unlocked;
        }

        self.inputs_to_next = 1000 - (self.total_inputs % 1000) as u32;
        None
    }
}

pub struct AffectionStore(pub Mutex<AffectionState>);
