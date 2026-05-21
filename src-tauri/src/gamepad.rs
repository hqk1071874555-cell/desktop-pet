use gilrs::{Gilrs, Event, EventType};
use tauri::Emitter;
use std::thread;
use std::time::Duration;

/// 启动手柄轮询监听（独立线程，60FPS 间隔）
pub fn start(app_handle: tauri::AppHandle) {
    thread::spawn(move || {
        let mut gilrs = match Gilrs::new() {
            Ok(g) => g,
            Err(e) => {
                eprintln!("Failed to init gilrs: {:?}", e);
                return;
            }
        };

        loop {
            while let Some(Event { event, .. }) = gilrs.next_event() {
                match event {
                    EventType::AxisChanged(axis, value, ..) => {
                        let _ = app_handle.emit("gamepad-changed", serde_json::json!({
                            "type": "Axis",
                            "axis": format!("{:?}", axis),
                            "value": value
                        }));
                    }
                    EventType::ButtonPressed(button, ..) => {
                        let _ = app_handle.emit("gamepad-changed", serde_json::json!({
                            "type": "ButtonPress",
                            "button": format!("{:?}", button)
                        }));
                        let _ = app_handle.emit("affection-input", serde_json::json!({
                            "count": 1.0
                        }));
                    }
                    EventType::ButtonReleased(button, ..) => {
                        let _ = app_handle.emit("gamepad-changed", serde_json::json!({
                            "type": "ButtonRelease",
                            "button": format!("{:?}", button)
                        }));
                    }
                    _ => {}
                }
            }
            thread::sleep(Duration::from_millis(16));
        }
    });
}
