---
name: "login-video-background"
description: "Documents the implementation of video background for login pages and provides strategies to preserve this feature when rolling back versions. Invoke when working with login page video backgrounds or needing to maintain video features during version control operations."
---

# 登录页面视频背景实现技能

## 功能概述

本技能详细说明了如何在登录页面实现视频背景效果，以及如何在版本回退时保留这一功能。适用于需要创建具有视觉吸引力的登录界面，同时确保在代码版本管理过程中不会丢失视频背景功能。

## 实现步骤

### 1. 视频文件准备

1. **视频文件选择**：选择适合登录页面的视频文件（建议使用MP4格式）
2. **视频文件放置**：将视频文件放置在 `utils_file` 目录中
3. **视频文件命名**：确保视频文件名清晰，如 `年年.mp4`

### 2. HTML结构实现

在 `templates/login.html` 文件中添加以下结构：

```html
<!-- 视频背景 -->
<div class="video-background">
    <video id="backgroundVideo" autoplay loop playsinline>
        <source src="/utils_file/年年.mp4" type="video/mp4">
    </video>
</div>
<!-- 背景叠加层 -->
<div class="overlay"></div>
```

### 3. CSS样式实现

在 `<style>` 标签中添加以下CSS：

```css
/* 游戏风格视频背景 */
.video-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    overflow: hidden;
}
.video-background video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(1);
    opacity: 1;
}
/* 背景叠加层 */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, rgba(0,0,0,0.7) 0%, rgba(30,30,60,0.8) 100%);
    z-index: -1;
}
```

### 4. 前端交互实现

在登录成功时暂停视频，提升用户体验：

```javascript
// 登录成功后暂停视频
if (video) {
    video.pause();
}
```

### 5. 后端路由配置

确保在 `app.py` 中配置了静态文件路由，以便前端能够访问视频文件：

```python
# ---------- 静态文件路由（用于utils_file目录）----------
@server.route('/utils_file/<path:filename>')
def utils_static(filename):
    return send_from_directory('utils_file', filename)
```

## 版本回退时的保留策略

### 策略一：使用版本控制系统标记

1. **创建分支**：在进行版本回退前，创建一个分支专门保存视频背景功能
   ```bash
   git checkout -b feature/login-video-background
   git add templates/login.html utils_file/年年.mp4
   git commit -m "Save login page video background feature"
   ```

2. **回退主分支**：在主分支上执行版本回退
   ```bash
   git checkout main
   git reset --hard <previous-commit>
   ```

3. **重新应用功能**：将视频背景功能重新应用到回退后的代码
   ```bash
   git checkout feature/login-video-background -- templates/login.html utils_file/年年.mp4
   git add templates/login.html utils_file/年年.mp4
   git commit -m "Reapply login page video background feature"
   ```

### 策略二：使用补丁文件

1. **生成补丁**：在回退前生成视频背景功能的补丁文件
   ```bash
   git diff HEAD~1 HEAD -- templates/login.html utils_file/年年.mp4 > login-video.patch
   ```

2. **执行回退**：执行版本回退操作
   ```bash
   git reset --hard <previous-commit>
   ```

3. **应用补丁**：将视频背景功能的补丁应用到回退后的代码
   ```bash
   git apply login-video.patch
   git add templates/login.html utils_file/年年.mp4
   git commit -m "Apply login page video background patch"
   ```

### 策略三：手动保存和恢复

1. **备份文件**：在版本回退前，手动备份相关文件
   - `templates/login.html`
   - `utils_file/年年.mp4`

2. **执行回退**：执行版本回退操作

3. **恢复文件**：将备份的文件复制回项目中

## 验证步骤

1. **启动应用**：确保应用能够正常启动
2. **访问登录页**：打开浏览器访问登录页面
3. **验证视频**：确认视频背景能够正常播放
4. **测试登录**：验证登录功能是否正常工作
5. **检查响应**：确保页面在不同设备上都能正常显示

## 故障排除

### 视频不播放

- **检查路径**：确认视频文件路径正确
- **检查权限**：确保视频文件有正确的读取权限
- **检查格式**：确认视频文件格式为浏览器支持的格式（MP4）

### 页面加载缓慢

- **视频优化**：考虑压缩视频文件大小
- **延迟加载**：实现视频的延迟加载
- **预加载策略**：使用适当的视频预加载策略

### 版本回退后功能丢失

- **检查文件**：确认相关文件是否被正确恢复
- **检查路由**：确认静态文件路由是否存在
- **检查权限**：确认文件权限是否正确

## 最佳实践

1. **视频选择**：选择适合品牌风格的视频，长度适中（15-30秒）
2. **性能优化**：压缩视频文件，确保加载速度
3. **兼容性**：确保视频在主流浏览器中都能正常播放
4. **用户体验**：添加视频控制选项，允许用户暂停或关闭视频
5. **可访问性**：确保登录表单在视频背景下仍然清晰可见

## 应用场景

- **企业登录门户**：提升品牌形象
- **会员系统**：增强用户体验
- **管理后台**：提供专业的视觉效果
- **活动页面**：配合活动主题的动态背景