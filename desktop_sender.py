import keyboard
from PIL import ImageGrab, Image # Keep PIL
import requests
import base64
import io
import json
import time
import sys

# --- 配置 ---
# NTFY_TOPIC_URL = "https://ntfy.sh/loxieL"  # 已注释原配置 在ntfy.sh创建你的唯一topic  NTFY_TOPIC_URL = "https://ntfy.sh/your-unique-topic"
# 使用私有 ntfy 服务器配置
SERVER_URL = "http://your-serverip"  # 自建服务器 IP 地址
TOPIC = "loxieL"  # 保持原来的主题名称
NTFY_TOPIC_URL = f"{SERVER_URL}/{TOPIC}"  # 完整的 URL
# This prompt is sent but *not* used by receiver.html for the final Gemini call
ORIGINAL_PROMPT = "Screenshot for Gemini analysis"

# --- 热键配置 --- (保持不变)
HOTKEY_CAPTURE = "ctrl+shift"
HOTKEY_GEMINI_PRO_EXP = "ctrl+alt+p"
HOTKEY_GEMINI_FLASH_THINK = "ctrl+alt+f"
HOTKEY_SCROLL_UP = "ctrl+alt+up"
HOTKEY_SCROLL_DOWN = "ctrl+alt+down"
HOTKEY_SCROLL_LEFT = "ctrl+alt+left"
HOTKEY_SCROLL_RIGHT = "ctrl+alt+right"
HOTKEY_CLEAR_HISTORY = "ctrl+alt+backspace"

# --- 函数：发送控制消息 (保持不变) ---
def send_control_message(command, value=None):
    control_payload = {"type": "control", "command": command}
    if value is not None: control_payload["value"] = value
    message_body = json.dumps(control_payload)
    print(f"[*] 发送控制消息: {message_body}")
    try:
        headers = {"Title": f"Control Command: {command}", "Tags": "control"}
        response = requests.post(NTFY_TOPIC_URL, json=control_payload, headers=headers)
        response.raise_for_status()
        print(f"[*] 控制消息发送成功。")
    except requests.exceptions.RequestException as e:
        print(f"发送控制消息到 ntfy 时出错: {e}", file=sys.stderr)
    except Exception as e:
        print(f"发送控制消息时发生未知错误: {e}", file=sys.stderr)

# --- 热键处理函数 (保持不变) ---
def set_gemini_pro(): send_control_message("set_gemini_model", "gemini-2.5-pro-exp-03-25")
def set_gemini_flash_exp(): send_control_message("set_gemini_model", "gemini-2.0-flash-thinking-exp")
def clear_history(): send_control_message("clear_history")
def scroll_page_up(): send_control_message("scroll", "up")
def scroll_page_down(): send_control_message("scroll", "down")
def scroll_page_left(): send_control_message("scroll", "left")
def scroll_page_right(): send_control_message("scroll", "right")

# --- 函数：全屏截图、打包并发送 (修改回只发送 JSON Base64) ---
def capture_and_send():
    """全屏截图，打包占位符 Prompt 和图片 Base64 并发送"""
    print(f"检测到热键 '{HOTKEY_CAPTURE}'。正在进行全屏截图...")
    try:
        # --- 1. 全屏截图 ---
        screenshot = ImageGrab.grab()
        print("全屏截图完成。")

        # --- 2. Base64 编码全屏截图 ---
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        print("全屏截图已编码为 Base64。")

        # --- 3. 准备要发送的 JSON 数据 ---
        # 保持原来的格式，便于 HTML 接收端处理
        payload = {
            "prompt": ORIGINAL_PROMPT,
            "image_base64": img_base64
        }
        message_body = json.dumps(payload) # 将 Python 字典转换为 JSON 字符串

        # --- 4. 发送到 ntfy 服务器 ---
        print(f"正在发送数据到 {NTFY_TOPIC_URL}...")

        # 使用简单的文本消息方式发送，不使用附件
        headers = {
            "Title": "Screenshot for Gemini",
            "Tags": "screenshot,gemini"
            # 不需要 Content-Type，ntfy 会将其视为普通文本
            # 不需要 Filename
        }

        # 发送 JSON 字符串作为普通消息内容
        response = requests.post(
            NTFY_TOPIC_URL,
            data=message_body,  # 发送 JSON 字符串
            headers=headers
        )

        # --- 5. 检查响应状态 ---
        response.raise_for_status()
        print(f"数据发送成功！状态码: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"发送数据到 ntfy 时出错: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误响应：{e.response.text}", file=sys.stderr)
    except PermissionError:
        print("错误：截屏权限不足。请检查程序是否有屏幕捕捉权限。", file=sys.stderr)
    except ImportError as e:
        print(f"错误：缺少必要的库 ({e.name})。请确保已安装 Pillow, requests, keyboard。", file=sys.stderr)
    except Exception as e:
        print(f"在 capture_and_send 中发生未知错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

# --- 主程序入口 (保持不变) ---
if __name__ == "__main__":
    print("--- 全屏截图发送 + Gemini 模型切换 + 页面控制 ---")
    # ... (省略了打印热键和检查库的代码) ...
    print(f"[*] 发送目标 ntfy 主题: {NTFY_TOPIC_URL}")

    # Register all hotkeys
    try:
        keyboard.add_hotkey(HOTKEY_CAPTURE, capture_and_send)
        keyboard.add_hotkey(HOTKEY_GEMINI_PRO_EXP, set_gemini_pro)
        keyboard.add_hotkey(HOTKEY_GEMINI_FLASH_THINK, set_gemini_flash_exp)
        keyboard.add_hotkey(HOTKEY_SCROLL_UP, scroll_page_up)
        keyboard.add_hotkey(HOTKEY_SCROLL_DOWN, scroll_page_down)
        keyboard.add_hotkey(HOTKEY_SCROLL_LEFT, scroll_page_left)
        keyboard.add_hotkey(HOTKEY_SCROLL_RIGHT, scroll_page_right)
        keyboard.add_hotkey(HOTKEY_CLEAR_HISTORY, clear_history)
        print("\n[*] 所有热键监听已激活，等待触发...")
    except Exception as e:
        print(f"\n错误：无法注册热键。可能是权限不足或热键已被占用。", file=sys.stderr)
        print(f"   错误详情: {e}", file=sys.stderr)
        sys.exit(1)

    # Main loop and cleanup
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: print("\n[*] 检测到 Ctrl+C，正在退出...")
    except Exception as e: print(f"\n[*] 发生意外错误导致主循环退出: {e}", file=sys.stderr)
    finally:
        print("[*] 正在清理资源...")
        try:
            keyboard.unhook_all()
            print("[*] 热键已注销。")
        except Exception as e: print(f"[*] 清理热键时出错: {e}", file=sys.stderr)
        print("[*] 脚本已退出。")


#python desktop_sender.py