import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from threading import Thread
from pathlib import Path


class PyInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyInstaller 打包工具")
        self.root.geometry("850x950")

        # 设置窗口图标
        try:
            self.root.iconbitmap(default='pyinstaller.ico')
        except:
            pass

        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', padding=5)
        self.style.configure('TLabel', padding=5)
        self.style.configure('TButton', padding=5)
        self.style.configure('TEntry', padding=5)
        self.style.configure('TCombobox', padding=3)
        self.style.configure('TCheckbutton', padding=5)
        self.style.map('TButton',
                       foreground=[('active', 'black'), ('!active', 'black')],
                       background=[('active', '#d9d9d9'), ('!active', '#f0f0f0')])

        # 主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 项目设置面板
        self.create_project_settings()

        # 打包选项面板
        self.create_build_options()

        # 输出面板
        self.create_output_section()

        # 状态栏
        self.create_status_bar()

        # 检查PyInstaller是否安装
        self.check_pyinstaller()

        # 检查Pillow是否安装
        self.check_pillow()

        # 自动检测ico文件
        self.auto_detect_icon()

    def create_project_settings(self):
        """创建项目设置部分"""
        frame = ttk.LabelFrame(self.main_frame, text="项目设置", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # 项目文件夹
        ttk.Label(frame, text="项目文件夹:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.project_folder = ttk.Entry(frame, width=60)
        self.project_folder.grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_project_folder).grid(row=0, column=2)

        # 入口脚本 (主程序文件，如 main.py)
        ttk.Label(frame, text="入口脚本 (如 main.py):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.script_path = ttk.Entry(frame, width=60)
        self.script_path.grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_script).grid(row=1, column=2)

        # 图标文件
        ttk.Label(frame, text="图标文件 (.ico):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.icon_path = ttk.Entry(frame, width=60)
        self.icon_path.grid(row=2, column=1, sticky=tk.EW, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_icon).grid(row=2, column=2)

        # 输出目录
        ttk.Label(frame, text="输出目录:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.output_dir = ttk.Entry(frame, width=60)
        self.output_dir.grid(row=3, column=1, sticky=tk.EW, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_output_dir).grid(row=3, column=2)

        # 让列1可以扩展
        frame.columnconfigure(1, weight=1)

    def create_build_options(self):
        """创建打包选项部分"""
        frame = ttk.LabelFrame(self.main_frame, text="打包选项", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # 目标平台 (多选)
        ttk.Label(frame, text="目标平台:").grid(row=0, column=0, sticky=tk.W, pady=3)
        platforms_frame = ttk.Frame(frame)
        platforms_frame.grid(row=0, column=1, sticky=tk.W)

        self.platform_vars = {
            'win64': tk.BooleanVar(value=sys.platform == 'win32' and sys.maxsize > 2 ** 32),
            'win32': tk.BooleanVar(value=sys.platform == 'win32' and sys.maxsize <= 2 ** 32)
            #'linux': tk.BooleanVar(value=sys.platform == 'linux'),
            #'darwin': tk.BooleanVar(value=sys.platform == 'darwin')
        }

        ttk.Checkbutton(platforms_frame, text="Windows 64位", variable=self.platform_vars['win64']).pack(side=tk.LEFT,
                                                                                                         padx=5)
        ttk.Checkbutton(platforms_frame, text="Windows 32位", variable=self.platform_vars['win32']).pack(side=tk.LEFT,
                                                                                                         padx=5)
        #ttk.Checkbutton(platforms_frame, text="Linux", variable=self.platform_vars['linux']).pack(side=tk.LEFT, padx=5)
        #ttk.Checkbutton(platforms_frame, text="MacOS", variable=self.platform_vars['darwin']).pack(side=tk.LEFT, padx=5)

        # 打包方式
        ttk.Label(frame, text="打包方式:").grid(row=1, column=0, sticky=tk.W, pady=3)
        build_mode_frame = ttk.Frame(frame)
        build_mode_frame.grid(row=1, column=1, sticky=tk.W)

        self.onefile = tk.BooleanVar(value=True)
        ttk.Checkbutton(build_mode_frame, text="单个可执行文件", variable=self.onefile).pack(side=tk.LEFT, padx=5)

        self.console = tk.BooleanVar(value=False)
        ttk.Checkbutton(build_mode_frame, text="显示控制台窗口", variable=self.console).pack(side=tk.LEFT, padx=5)

        # 闪屏选项
        ttk.Label(frame, text="闪屏图片:").grid(row=2, column=0, sticky=tk.W, pady=3)
        splash_frame = ttk.Frame(frame)
        splash_frame.grid(row=2, column=1, sticky=tk.EW, padx=5)

        self.splash_path = ttk.Entry(splash_frame, width=60)
        self.splash_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(splash_frame, text="浏览...", command=self.browse_splash).pack(side=tk.LEFT, padx=5)

        # 额外参数
        ttk.Label(frame, text="额外参数:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.additional_args = ttk.Entry(frame, width=60)
        self.additional_args.grid(row=3, column=1, sticky=tk.EW, padx=5)

        # 让列1可以扩展
        frame.columnconfigure(1, weight=1)

    def create_output_section(self):
        """创建输出部分"""
        frame = ttk.LabelFrame(self.main_frame, text="输出信息", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 状态显示
        self.status = ttk.Label(frame, text="就绪", foreground="blue")
        self.status.pack(anchor=tk.W, pady=5)

        # 输出日志
        self.output_log = scrolledtext.ScrolledText(frame, height=10, wrap=tk.WORD)
        self.output_log.pack(fill=tk.BOTH, expand=True, pady=5)

        # 生成的命令
        ttk.Label(frame, text="生成的命令:").pack(anchor=tk.W)
        cmd_frame = ttk.Frame(frame)
        cmd_frame.pack(fill=tk.X, pady=5)

        self.cmd_display = scrolledtext.ScrolledText(cmd_frame, height=3, wrap=tk.WORD)
        self.cmd_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Button(cmd_frame, text="复制", command=self.copy_command).pack(side=tk.RIGHT, padx=5)

        # 执行按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="开始打包", command=self.start_packaging,
                   style='Accent.TButton').pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="清除日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.main_frame, height=25)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))

        self.pyinstaller_status = ttk.Label(self.status_bar, text="检测PyInstaller: 未知")
        self.pyinstaller_status.pack(side=tk.LEFT, padx=5)

        self.pillow_status = ttk.Label(self.status_bar, text="Pillow: 未知")
        self.pillow_status.pack(side=tk.LEFT, padx=5)

        ttk.Button(self.status_bar, text="安装PyInstaller", command=self.install_pyinstaller).pack(side=tk.RIGHT,
                                                                                                   padx=5)
        ttk.Button(self.status_bar, text="安装Pillow", command=self.install_pillow).pack(side=tk.RIGHT, padx=5)

    def auto_detect_icon(self):
        """自动检测当前目录下的ico文件"""
        try:
            current_dir = os.getcwd()
            for file in os.listdir(current_dir):
                if file.lower().endswith('.ico'):
                    self.icon_path.delete(0, tk.END)
                    self.icon_path.insert(0, os.path.join(current_dir, file))
                    break
        except Exception as e:
            self.append_output(f"自动检测图标文件时出错: {str(e)}\n")

    def browse_project_folder(self):
        """浏览项目文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.project_folder.delete(0, tk.END)
            self.project_folder.insert(0, folder)

            # 自动设置输出目录为项目文件夹下的dist
            output_dir = os.path.join(folder, 'dist')
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, output_dir)

            # 自动设置入口脚本
            if not self.script_path.get():
                py_files = [f for f in os.listdir(folder) if f.endswith('.py')]
                if len(py_files) == 1:
                    self.script_path.insert(0, os.path.join(folder, py_files[0]))
                elif py_files:
                    for file in py_files:
                        if file.lower().startswith('main'):
                            self.script_path.insert(0, os.path.join(folder, file))
                            break

    def browse_script(self):
        """浏览脚本文件"""
        initial_dir = self.project_folder.get() if self.project_folder.get() else None
        file = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Python Files", "*.py")])
        if file:
            self.script_path.delete(0, tk.END)
            self.script_path.insert(0, file)

    def browse_output_dir(self):
        """浏览输出目录"""
        initial_dir = self.output_dir.get() if self.output_dir.get() else None
        folder = filedialog.askdirectory(initialdir=initial_dir)
        if folder:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, folder)

    def browse_icon(self):
        """浏览图标文件"""
        initial_dir = self.project_folder.get() if self.project_folder.get() else None
        file = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Icon Files", "*.ico")])
        if file:
            self.icon_path.delete(0, tk.END)
            self.icon_path.insert(0, file)

    def browse_splash(self):
        """浏览闪屏图片文件"""
        initial_dir = self.project_folder.get() if self.project_folder.get() else None
        filetypes = [("PNG Files", "*.png")]
        if hasattr(self, 'pillow_installed') and self.pillow_installed:
            filetypes.extend([
                ("JPEG Files", "*.jpg *.jpeg"),
                ("BMP Files", "*.bmp"),
                ("GIF Files", "*.gif"),
                ("All Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")
            ])

        file = filedialog.askopenfilename(initialdir=initial_dir, filetypes=filetypes)
        if file:
            self.splash_path.delete(0, tk.END)
            self.splash_path.insert(0, file)

    def check_pyinstaller(self):
        """检查PyInstaller是否安装"""
        try:
            subprocess.run(['pyinstaller', '--version'], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            self.pyinstaller_status.config(text="PyInstaller: 已安装", foreground="green")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.pyinstaller_status.config(text="PyInstaller: 未安装", foreground="red")
            return False

    def check_pillow(self):
        """检查Pillow是否安装"""
        try:
            import PIL
            self.pillow_installed = True
            self.pillow_status.config(text="Pillow: 已安装", foreground="green")
            return True
        except ImportError:
            self.pillow_installed = False
            self.pillow_status.config(text="Pillow: 未安装", foreground="red")
            return False

    def install_pyinstaller(self):
        """安装PyInstaller"""

        def install_thread():
            try:
                self.append_output("正在安装PyInstaller...\n")
                # 设置环境变量，防止子进程继承导致重复启动GUI
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                env["PYTHONDONTWRITEBYTECODE"] = "1"

                # 使用subprocess.run并设置适当的参数
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
                    check=True,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                self.append_output("PyInstaller安装成功!\n")
                self.root.after(0, lambda: self.pyinstaller_status.config(
                    text="PyInstaller: 已安装", foreground="green"))
            except subprocess.CalledProcessError as e:
                self.append_output(f"安装失败: {e}\n")
                self.root.after(0, lambda: self.pyinstaller_status.config(
                    text="PyInstaller: 安装失败", foreground="red"))

        Thread(target=install_thread, daemon=True).start()

    def install_pillow(self):
        """安装Pillow"""

        def install_thread():
            try:
                self.append_output("正在安装Pillow...\n")
                # 设置环境变量，防止子进程继承导致重复启动GUI
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                env["PYTHONDONTWRITEBYTECODE"] = "1"

                # 使用subprocess.run并设置适当的参数
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 'pillow'],
                    check=True,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                self.append_output("Pillow安装成功!\n")
                self.root.after(0, lambda: self.pillow_status.config(
                    text="Pillow: 已安装", foreground="green"))
                self.root.after(0, lambda: setattr(self, 'pillow_installed', True))
            except subprocess.CalledProcessError as e:
                self.append_output(f"安装失败: {e}\n")
                self.root.after(0, lambda: self.pillow_status.config(
                    text="Pillow: 安装失败", foreground="red"))

        Thread(target=install_thread, daemon=True).start()

    def start_packaging(self):
        """开始打包"""
        project_dir = self.project_folder.get()
        if not project_dir:
            messagebox.showerror("错误", "请先选择项目文件夹!")
            return

        script_path = self.script_path.get()
        if not script_path:
            messagebox.showerror("错误", "请指定入口脚本文件!")
            return

        # 获取应用名称（默认为入口脚本名称不含扩展名）
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        app_name = simpledialog.askstring("应用名称",
                                          "请输入应用名称:",
                                          initialvalue=script_name)
        if app_name is None:  # 用户点击取消
            return

        # 检查至少选择了一个平台
        selected_platforms = [p for p, var in self.platform_vars.items() if var.get()]
        if not selected_platforms:
            messagebox.showwarning("警告", "未选择任何目标平台，将使用当前系统平台")
            # 根据当前系统自动选择平台
            if sys.platform == 'win32':
                selected_platforms = ['win64' if sys.maxsize > 2 ** 32 else 'win32']
            #elif sys.platform == 'linux':
            #    selected_platforms = ['linux']
            #elif sys.platform == 'darwin':
            #    selected_platforms = ['darwin']

        # 确保输出目录存在
        output_dir = self.output_dir.get()
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 为每个选中的平台执行打包
        for platform in selected_platforms:
            self.execute_packaging_for_platform(project_dir, script_path, platform, app_name)

    def execute_packaging_for_platform(self, project_dir, script_path, platform, app_name):
        """为指定平台执行打包"""
        # 构建命令
        cmd = ['pyinstaller']

        # 添加应用名称参数
        cmd.extend(['--name', app_name])

        if self.onefile.get():
            cmd.append('--onefile')

        if not self.console.get():
            cmd.append('--windowed')

        icon_path = self.icon_path.get()
        if icon_path:
            cmd.extend(['--icon', icon_path])

        splash_path = self.splash_path.get()
        if splash_path:
            cmd.extend(['--splash', splash_path])

        output_dir = self.output_dir.get()
        if output_dir:
            # 为不同平台创建子目录
            platform_output_dir = os.path.join(output_dir, platform)
            if not os.path.exists(platform_output_dir):
                os.makedirs(platform_output_dir)
            cmd.extend(['--distpath', platform_output_dir])

        # 平台特定处理
        if platform.startswith('win'):
            # Windows平台不需要特殊处理，默认生成.exe
            pass
        #elif platform == 'linux':
            # Linux平台不需要扩展名
        #    pass
        #elif platform == 'darwin':
            # Mac平台需要.app bundle
        #    cmd.extend(['--osx-bundle-identifier', f'com.example.{app_name.replace(" ", "_")}'])

        additional_args = self.additional_args.get()
        if additional_args:
            cmd.extend(additional_args.split())

        cmd.append(script_path)

        # 显示命令
        cmd_str = ' '.join(cmd)
        self.append_output(f"\n=== 为平台 {platform} 执行打包 ===\n")
        self.append_output(f"命令: {cmd_str}\n")
        self.cmd_display.delete(1.0, tk.END)
        self.cmd_display.insert(tk.END, cmd_str)
        self.status.config(text=f"正在为 {platform} 打包...", foreground="blue")

        # 执行打包
        Thread(target=self.execute_command, args=(cmd, project_dir, platform), daemon=True).start()

    def execute_command(self, cmd, cwd, platform):
        """执行命令"""
        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            for line in process.stdout:
                self.append_output(line)

            process.wait()
            if process.returncode == 0:
                self.append_output(f"\n{platform} 平台打包成功完成!\n")
                self.root.after(0, lambda: self.status.config(
                    text=f"{platform} 平台打包成功!", foreground="green"))
            else:
                self.append_output(f"\n{platform} 平台打包失败，返回码: {process.returncode}\n")
                self.root.after(0, lambda: self.status.config(
                    text=f"{platform} 平台打包失败", foreground="red"))
        except Exception as e:
            self.append_output(f"\n执行错误: {str(e)}\n")
            self.root.after(0, lambda: self.status.config(
                text=f"执行错误: {str(e)}", foreground="red"))

    def append_output(self, text):
        """追加输出到日志"""
        self.output_log.insert(tk.END, text)
        self.output_log.see(tk.END)
        self.output_log.update()

    def clear_log(self):
        """清除日志"""
        self.output_log.delete(1.0, tk.END)
        self.status.config(text="就绪", foreground="blue")

    def copy_command(self):
        """复制命令到剪贴板"""
        cmd = self.cmd_display.get(1.0, tk.END)
        if cmd.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            self.status.config(text="命令已复制到剪贴板", foreground="green")
            self.root.after(2000, lambda: self.status.config(text="就绪", foreground="blue"))


if __name__ == "__main__":
    root = tk.Tk()

    # 设置窗口居中
    window_width = 850
    window_height = 950
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    # 创建自定义样式
    style = ttk.Style()
    style.configure('Accent.TButton', foreground='white', background='#0078d7')
    style.map('Accent.TButton',
              foreground=[('active', 'white'), ('!active', 'white')],
              background=[('active', '#005499'), ('!active', '#0078d7')])

    app = PyInstallerGUI(root)
    root.mainloop()