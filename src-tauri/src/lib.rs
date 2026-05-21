mod input;
mod gamepad;
mod affection;

#[allow(unused_imports)]
use tauri::Manager;
use std::sync::Mutex;
use affection::AffectionStore;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

pub fn run() {
    tauri::Builder::default()
        .manage(AffectionStore(Mutex::new(affection::AffectionState::default())))
        .setup(|app| {
            let handle = app.handle().clone();

            // 启动键盘/鼠标全局监听
            input::start(handle.clone());

            // 启动手柄监听
            gamepad::start(handle);

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
