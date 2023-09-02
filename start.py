import tkinter as tk
from maze import MazeGenerator

def start_game():
    maze_width = int(maze_width_entry.get())
    maze_width = 35 if maze_width > 35 else maze_width
    maze_width = 1 if maze_width < 1 else maze_width

    maze_height = int(maze_height_entry.get())
    maze_height = 16 if maze_height > 16 else maze_height
    maze_height = 1 if maze_height < 1 else maze_height

    root.destroy()  # 关闭参数输入窗口
    mg = MazeGenerator(maze_width, maze_height)
    mg.run_game()


if __name__ == '__main__':
    # 创建参数输入窗口
    root = tk.Tk()
    root.title("Game Configuration")
    root.geometry("300x200")
    root.resizable(False, False)

    # 添加标签和输入框
    width_label = tk.Label(root, text="Width:")
    width_label.place(x=50, y=50)  # 设置标签的摆放位置

    maze_width_entry = tk.Entry(root)
    maze_width_entry.place(x=100, y=50)  # 设置输入框的摆放位置
    maze_width_entry.insert(0, "20")  # 默认宽度

    height_label = tk.Label(root, text="Height:")
    height_label.place(x=50, y=80)  # 设置标签的摆放位置

    maze_height_entry = tk.Entry(root)
    maze_height_entry.place(x=100, y=80)  # 设置输入框的摆放位置
    maze_height_entry.insert(0, "16")  # 默认高度

    # 添加开始按钮
    start_button = tk.Button(root, text="Start Game", command=start_game, )
    start_button.place(x=130, y=120)  # 设置按钮的摆放位置

    root.mainloop()

