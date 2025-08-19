# Camera Screenshot 节点

一个 MOFA 节点，从系统摄像头捕获图像并保存到指定的文件路径。该节点使用 OpenCV 提供实时摄像头访问和图像捕获功能，适用于计算机视觉工作流程、监控应用程序和图像处理管道。

## 功能特性

- **摄像头访问**：直接访问系统摄像头（默认摄像头索引 0）
- **图像捕获**：使用 OpenCV 进行实时图像捕获
- **文件系统集成**：将捕获的图像保存到指定的文件路径
- **错误处理**：对摄像头访问和图像捕获进行全面的错误处理
- **原生 Dora 集成**：使用原生 Dora Node API 实现高效的数据流
- **可配置参数**：支持用于任务和节点命名的命令行参数

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

该节点使用原生 Dora Node 架构，而不是 MofaAgent 基类：

### 命令行参数
- `--name`：数据流中节点的名称（默认："arrow-assert"）
- `--task`：节点所需的任务（默认："Paris Olympics"）

### 环境变量
- `CI`：对于 CI/CD 环境设置为 "true"
- `TASK`：任务参数的覆盖
- `IS_DATAFLOW_END`：控制数据流终止

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `image_path` | string | 是 | 捕获图像应保存的文件路径 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `camera_screenshot_result` | string | 结果状态和已保存的图像文件名 |

## 使用示例

### 基本数据流配置

```yaml
# camera_screenshot_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      camera_screenshot_result: camera-screenshot/camera_screenshot_result
  - id: camera-screenshot
    build: pip install -e ../../agent-hub/camera-screenshot
    path: camera-screenshot
    outputs:
      - camera_screenshot_result
    inputs:
      image_path: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### 运行节点

1. **确保摄像头访问权限：**
   ```bash
   # 在 Linux 上，您可能需要将用户添加到 video 组
   sudo usermod -a -G video $USER
   ```

2. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

3. **构建并启动数据流：**
   ```bash
   dora build camera_screenshot_dataflow.yml
   dora start camera_screenshot_dataflow.yml
   ```

4. **发送图像路径：**
   输入捕获图像的期望保存路径（例如："/path/to/save/image.jpg"）

## 代码示例

核心功能在 `main.py` 中实现：

```python
import cv2
import time
from dora import Node
from mofa.kernel.utils.util import create_agent_output
import pyarrow as pa

def main():
    node = Node(args.name)
    
    for event in node:
        if event["type"] == "INPUT":
            if event['id'] in ['image_path']:
                image_path = event["value"][0].as_py()
                
                try:
                    # 初始化摄像头
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        print("无法打开摄像头")
                        exit()
                    
                    # 让摄像头预热
                    time.sleep(1)
                    
                    # 捕获图像
                    ret, frame = cap.read()
                    if not ret:
                        print("图像捕获失败")
                        cap.release()
                        exit()
                    
                    # 保存图像
                    cv2.imwrite(image_path, frame)
                    print(f"图像已保存为 {image_path}")
                    
                except Exception as e:
                    print(f"发生错误: {e}")
                finally:
                    # 释放摄像头
                    cap.release()
                
                # 发送输出
                node.send_output("camera_screenshot_result", 
                    pa.array([create_agent_output(
                        agent_name='camera_screenshot_result',
                        agent_result='image.jpg',
                        dataflow_status=os.getenv("IS_DATAFLOW_END", True)
                    )]), event['metadata'])
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **opencv-python**：用于摄像头访问和图像处理
- **mofa**：MOFA 框架工具（在 MOFA 环境中自动可用）

## 摄像头要求

### 硬件要求
- 系统摄像头（网络摄像头、内置摄像头或 USB 摄像头）
- 摄像头必须在设备索引 0 处可访问
- 图像捕获需要充足的照明

### 软件要求
- 正确安装摄像头驱动程序
- 应用程序已获得摄像头权限
- 没有其他应用程序阻止摄像头访问

### 平台特定说明

#### Linux
```bash
# 检查可用摄像头
ls /dev/video*

# 授予摄像头权限
sudo usermod -a -G video $USER
```

#### macOS
- 在"系统偏好设置"→"安全性与隐私"→"摄像头"中授予摄像头权限

#### Windows
- 确保已安装摄像头驱动程序
- 在 Windows 设置 → 隐私 → 摄像头中授予摄像头权限

## 使用场景

### 计算机视觉工作流程
- **图像处理管道**：为实时分析捕获图像
- **物体检测**：为检测算法提供输入图像
- **质量控制**：为自动检测系统捕获图像

### 监控和监视
- **安全系统**：由事件触发捕获图像
- **延时摄影**：定期图像捕获用于创建延时视频
- **运动检测**：检测到运动时捕获图像

### 文档和存档
- **流程文档**：捕获制造过程的图像
- **库存管理**：为编目拍摄物品照片
- **科学研究**：记录实验和观察

## 故障排除

### 常见问题

1. **摄像头访问被拒绝**
   - 检查摄像头权限
   - 确保没有其他应用程序正在使用摄像头
   - 验证摄像头驱动程序是否已安装

2. **图像捕获失败**
   - 检查摄像头连接
   - 验证照明是否充足
   - 使用其他应用程序测试摄像头

3. **文件保存错误**
   - 验证目标目录的写入权限
   - 检查可用磁盘空间
   - 确保文件路径格式有效

### 调试技巧
- 启用 `WRITE_LOG: true` 记录日志
- 使用 OpenCV 独立测试摄像头
- 检查摄像头设备索引（如果 0 失败，尝试不同的值）
- 验证图像路径权限

## 贡献

1. 使用各种摄像头设备和平台进行测试
2. 添加对多个摄像头索引的支持
3. 实现额外的图像格式和质量设置
4. 添加元数据提取和 EXIF 数据支持

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [OpenCV Python 文档](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [Dora 框架](https://github.com/dora-rs/dora)