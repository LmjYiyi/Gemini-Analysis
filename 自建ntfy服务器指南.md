# 自建 ntfy 服务器指南

## 为什么需要自建 ntfy 服务器

公共的 ntfy.sh 服务存在以下限制：
- 免费账户每小时最多发送 100 条消息（大约每 36 秒一条）
- 每天最多发送 500 条消息
- 附件大小限制为 10MB
- 连接数限制

通过自建 ntfy 服务器，您可以：
- 突破消息数量限制，实现无限制发送
- 提高隐私安全性，数据不经过第三方服务器
- 自定义配置参数，满足特定需求
- 消除网络延迟问题，提高响应速度

## Windows 系统下部署 ntfy 服务器

### 前提条件
- Windows 10/11 系统
- 安装 Docker Desktop

### 安装 Docker Desktop
1. 访问 [Docker Desktop 官网](https://www.docker.com/products/docker-desktop/) 下载安装程序
2. 或使用命令行安装：
   ```powershell
   winget install Docker.DockerDesktop
   ```
3. 安装完成后重启电脑
4. 启动 Docker Desktop 应用

### 部署 ntfy 服务器
1. 创建一个新文件夹用于存储 ntfy 数据：
   ```powershell
   mkdir D:\ntfy-data
   mkdir D:\ntfy-data\cache
   mkdir D:\ntfy-data\attachments
   ```

2. 在该文件夹中创建 `docker-compose.yml` 文件，内容如下：
   ```yaml
version: "3.8" # 你可以保留或移除这行，它已过时但通常无害

services:
  ntfy:
    image: binwiederhier/ntfy
    container_name: ntfy
    command: serve
    environment:
      - TZ=Asia/Shanghai
      - NTFY_LOG_LEVEL=info
      - NTFY_BASE_URL=http://your serverip # 保持不变，已正确设置
      - NTFY_ATTACHMENT_CACHE_DIR=/var/cache/ntfy/attachments # 明确指定附件缓存目录
      - NTFY_MAX_REQUEST_BODY_SIZE=10M # 保留：请求体大小限制
      # - NTFY_ENABLE_ATTACHMENTS=yes # 移除：根据文档，设置 cache-dir 和 base-url 就足够启用附件
    volumes:
      - D:/ntfy-data/cache:/var/cache/ntfy # 保留：ntfy 内部缓存
      # 修改：将外部目录映射到正确的附件缓存目录
      - D:/ntfy-data/attachments:/var/cache/ntfy/attachments
    ports:
      - 80:80
    restart: unless-stopped
   ```

3. 在 `docker-compose.yml` 所在目录打开 PowerShell，执行：
   ```powershell
   docker-compose up -d
   ```

4. 查看本机 IP 地址：
   ```powershell
   ipconfig
   ```
   记录下您电脑的本地 IP 地址（通常以 192.168.x.x 开头）

5. 配置 Windows 防火墙，允许 80 端口进入：
   ```powershell
   netsh advfirewall firewall add rule name="ntfy_server" dir=in action=allow protocol=TCP localport=80
   ```

## 修改客户端代码

需要将 `desktop_sender.py` 和 `receiver.html` 中的 ntfy.sh 地址修改为您的私有服务器地址：

### 修改 desktop_sender.py

将文件中所有 `https://ntfy.sh/` 替换为 `http://你的IP地址/`，例如：
```python
response = requests.post(f"http://192.168.1.100/{TOPIC}", 
    data=image_bytes, 
    headers={"Content-Type": "image/png", "Filename": "screenshot.png"}
)
```

### 修改 receiver.html

将文件中所有 `https://ntfy.sh/` 替换为 `http://你的IP地址/`，例如：
```javascript
const eventSource = new EventSource("http://192.168.1.100/your-unique-topic");
```

## 注意事项

1. 确保部署 ntfy 服务器的电脑与运行客户端的设备在同一个局域网中
2. 服务器电脑需保持开机状态才能正常使用
3. 如果需要外网访问，请考虑设置端口转发或使用内网穿透工具
4. 为了安全起见，可以在 docker-compose.yml 中添加基本的身份验证配置

## 自定义高级配置

如需更复杂的配置（如用户认证、HTTPS 支持等），请参考 [ntfy 官方文档](https://docs.ntfy.sh/config/)，创建自定义配置文件并挂载到容器中。 