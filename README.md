# 基于多种智能算法的python迷宫游戏

## 动态生成迷宫
使用深度优先遍历算法生成迷宫，可以在settings.py中设置生成迷宫的动画显示。

```python
# 是否显示迷宫生成过程
self.SHOW_DRAW = True
```

环境要求：
python3.8以上版本，pygame
```bash
pip install pygame

# 启动命令
python start.py
```

显示的动态效果如下：

![迷宫生成](https://s2.loli.net/2023/09/02/4Qmn69oF7Kv3bHe.gif)

## 控制模式

### 左侧小球

左侧小球由WASD方向键控制

### 右侧小球

右侧小球的控制模式有4种：

- 手动模式（MAN）：由键盘右侧的方向键控制
- AI1模式：随机方向控制策略，这种策略下，AI随机选择方向（很笨）
- AI2模式：广度优先策略找路径，这种方式找的路径不一定是最好的，但是一定可以走通，每一步操作做了200毫秒的延时，可以跟一般的人类玩家打平手。
- AI3模式：使用A*算法，找到的是最短的路径，每步操作延时50毫秒，人工玩家很难取胜。

**在游戏过程中可以随时切换四种控制模式（用鼠标点击即可）。**

游戏演示：

![](https://s2.loli.net/2023/09/02/Ts8ZAKgBuPmHqjU.gif)

### 如果对你有用，请我喝杯咖啡吧

![donate](https://s2.loli.net/2023/09/02/RAPpBsr38XTzCoy.png)

交流请联系我：wangshuxianmvp@gmail.com

