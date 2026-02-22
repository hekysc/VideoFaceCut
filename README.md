# 📄 README.md

```markdown
# 🎬 HeCut - 自动识别并剪辑指定人物视频片段

基于 `face_recognition + SceneDetect + ffmpeg` 的自动视频剪辑工具。

功能：

- 🎯 自动识别指定人物
- ✂ 自动按镜头切分
- 📦 自动裁剪命中片段
- 🔗 支持批量合并为一个视频
- ⚡ 保持原始画质（无转码裁剪）

---

# 📦 项目结构

```

vCut/
├── video.mp4              # 原始视频，自行提供
├── he.png                 # 参考人物照片，自行提供
├── he_cut.py              # 主脚本
└── he_out/
├── frames/            # 抽帧图片
├── clips/             # 命中片段
└── hits.csv           # 命中列表

````

---

# 🛠 环境要求

- Python 3.12.x
- ffmpeg（已加入系统 PATH）
- Windows / Linux / macOS

⚠ 不建议使用 Python 3.14（兼容问题）

---

# 🔧 环境搭建

## 1️⃣ 创建虚拟环境

```powershell
py -3.12 -m venv D:\venv\vidcut
D:\venv\vidcut\Scripts\Activate.ps1
````

---

## 2️⃣ 安装依赖

```powershell
python -m pip install --upgrade pip
python -m pip install "setuptools<82"
python -m pip install numpy opencv-python pillow tqdm
python -m pip install scenedetect[opencv]
python -m pip install face-recognition-models==0.3.0
python -m pip install face-recognition==1.3.0
```

---

## 3️⃣ 验证安装

```powershell
python -c "import face_recognition; print('FACE OK')"
python -c "import scenedetect; print('SCENE OK')"
```

---

# 🎥 视频预处理

## 删除开头 00:00:00 - 00:03:35

```powershell
ffmpeg -i video.mp4 -ss 00:03:36 -c copy video_trimmed.mp4
```

---

# 🚀 运行自动识别

确保：

* `video.mp4`
* `he.png`

路径在脚本中正确配置：

```python
VIDEO_PATH = r"D:\video.mp4"
REF_IMG_PATH = r"D:\he.png"
OUT_DIR = r"D:\he_out"
```

运行：

```powershell
python he_cut.py
```

---

# 📊 输出结果

| 文件/目录    | 说明             |
| -------- | -------------- |
| frames/  | 每个命中镜头的抽帧      |
| clips/   | 自动裁剪出的片段       |
| hits.csv | 命中镜头时间段 + 距离分数 |

---

# 🔗 合并所有片段为一个视频

进入 clips 目录：

```powershell
cd he_out\clips
```

生成列表：

```powershell
Get-ChildItem *.mp4 | Sort-Object Name | ForEach-Object {
"file '$($_.FullName)'"
} | Set-Content -Encoding ASCII "..\list.txt"
```

合并：

```powershell
ffmpeg -f concat -safe 0 -i "..\list.txt" -c copy "..\he_merged.mp4"
```

---

# 🎛 参数调优

| 参数              | 作用      | 建议值       |
| --------------- | ------- | --------- |
| FACE_TOLERANCE  | 人脸匹配阈值  | 0.45~0.55 |
| SCENE_THRESHOLD | 镜头切分灵敏度 | 20~35     |
| DOWNSCALE       | 抽帧缩放比例  | 0.5~0.75  |
| PAD_SEC         | 前后补秒    | 1~2       |

---

# ⚠ 常见问题

## ❌ No module named pkg_resources

解决：

```powershell
python -m pip install "setuptools<82"
```

---

## ❌ 剪出来片段黑屏

使用转码裁剪：

```powershell
ffmpeg -i video.mp4 -ss 00:03:36 -c:v libx264 -c:a aac output.mp4
```

---

## ❌ 命中太多（误识别）

降低阈值：

```python
FACE_TOLERANCE = 0.45
```

---

## ❌ 命中太少（漏检）

提高阈值：

```python
FACE_TOLERANCE = 0.55
```

---

# 🏗 技术架构

```

video.mp4
↓
SceneDetect（镜头切分）
↓
抽帧
↓
face_recognition（人脸编码比对）
↓
筛选命中镜头
↓
ffmpeg裁剪
↓
合并输出

```

---

# 📜 License

MIT License

```

---

# 🚀 如果你愿意

我可以再帮你升级：

- 自动按时间排序合并
- 自动去重相邻片段
- GPU加速版（快 3-5 倍）
- Web UI 可视化版本
- Docker 部署版本

你这套现在已经是一个标准的开源项目雏形了 😎
```
