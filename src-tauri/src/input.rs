use rdev::{listen, Event, EventType};
use tauri::Emitter;
use std::thread;

/// 启动全局键盘/鼠标监听（独立线程）
pub fn start(app_handle: tauri::AppHandle) {
    thread::spawn(move || {
        if let Err(error) = listen(move |event: Event| {
            let app = app_handle.clone();
            match event.event_type {
                EventType::KeyPress(key) => {
                    let key_name = format!("{:?}", key);
                    let _ = app.emit("device-changed", serde_json::json!({
                        "kind": "KeyboardPress",
                        "value": key_name
                    }));
                    let _ = app.emit("affection-input", serde_json::json!({
                        "count": 1.0
                    }));
                }
                EventType::KeyRelease(key) => {
                    let key_name = format!("{:?}", key);
                    let _ = app.emit("device-changed", serde_json::json!({
                        "kind": "KeyboardRelease",
                        "value": key_name
                    }));
                }
                EventType::ButtonPress(button) => {
                    let _ = app.emit("device-changed", serde_json::json!({
                        "kind": "MousePress",
                        "value": format!("{:?}", button)
                    }));
                    let _ = app.emit("affection-input", serde_json::json!({
                        "count": 0.5
                    }));
                }
                EventType::ButtonRelease(button) => {
                    let _ = app.emit("device-changed", serde_json::json!({
                        "kind": "MouseRelease",
                        "value": format!("{:?}", button)
                    }));
                }
                EventType::MouseMove { x, y } => {
                    let _ = app.emit("device-changed", serde_json::json!({
                        "kind": "MouseMove",
                        "x": x,
                        "y": y
                    }));
                }
                _ => {}
            }
        }) {
            eprintln!("rdev listen error: {:?}", error);
        }
    });
}
