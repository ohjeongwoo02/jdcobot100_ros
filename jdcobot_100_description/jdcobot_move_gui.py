import math
import threading
import tkinter as tk

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

JOINT_NAMES = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
MOVE_JOINTS = ['Base', 'Shoulder', 'Upper arm', 'Fore arm']   # joint_1 ~ joint_4
HOME_DEG = [90.0, 90.0, 90.0, 90.0]                           # 아두이노 시작 자세와 동일
JOINT_5_RAD = 1.5708    # 서보 없음 (RViz 표시용)
JOINT_6_POS = 0.002     # prismatic 관절 (RViz 표시용)


class MoveGuiNode(Node):
    def __init__(self):
        super().__init__('jdcobot_move_gui')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        self.lock = threading.Lock()

        self.current = list(HOME_DEG)   # 현재 각도 (도)
        self.start = list(HOME_DEG)     # 이동 시작 각도
        self.target = list(HOME_DEG)    # 목표 각도
        self.duration = 0.0
        self.t0 = 0.0
        self.moving = False

        # 50Hz 로 발행 (jdcobot_control 은 5개 중 1개만 아두이노로 보내므로 약 10Hz 로 전달됨)
        self.timer = self.create_timer(0.02, self.update)

    def now(self):
        return self.get_clock().now().nanoseconds / 1e9

    def move_to(self, target_deg, speed_deg_s):
        with self.lock:
            self.start = list(self.current)
            self.target = [min(max(a, 0.0), 180.0) for a in target_deg]
            max_delta = max(abs(t - s) for t, s in zip(self.target, self.start))
            self.duration = max_delta / max(speed_deg_s, 1.0)
            self.t0 = self.now()
            self.moving = self.duration > 0.0
        self.get_logger().info(
            f"move -> {[round(a) for a in self.target]} ({self.duration:.1f}s)")

    def stop(self):
        with self.lock:
            self.target = list(self.current)
            self.moving = False
        self.get_logger().info("stop")

    def update(self):
        with self.lock:
            if self.moving:
                ratio = min((self.now() - self.t0) / self.duration, 1.0)
                ease = ratio * ratio * (3 - 2 * ratio)   # 천천히 출발 -> 천천히 정지
                self.current = [s + (t - s) * ease for s, t in zip(self.start, self.target)]
                if ratio >= 1.0:
                    self.moving = False
            angles = list(self.current)

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        msg.position = [math.radians(a) for a in angles] + [JOINT_5_RAD, JOINT_6_POS]
        self.publisher_.publish(msg)


class MoveGui:
    def __init__(self, node):
        self.node = node
        self.root = tk.Tk()
        self.root.title('jdcobot move')

        self.target_vars = []
        for i, name in enumerate(MOVE_JOINTS):
            tk.Label(self.root, text=name, width=10, anchor='w').grid(row=i, column=0, padx=6)
            var = tk.DoubleVar(value=HOME_DEG[i])
            tk.Scale(self.root, variable=var, from_=0, to=180, orient='horizontal',
                     length=300, resolution=1).grid(row=i, column=1)
            tk.Spinbox(self.root, textvariable=var, from_=0, to=180, width=5).grid(row=i, column=2, padx=6)
            self.target_vars.append(var)

        row = len(MOVE_JOINTS)
        tk.Label(self.root, text='Speed (°/s)', width=10, anchor='w').grid(row=row, column=0, padx=6)
        self.speed_var = tk.DoubleVar(value=20)
        tk.Scale(self.root, variable=self.speed_var, from_=5, to=90, orient='horizontal',
                 length=300, resolution=1).grid(row=row, column=1)

        buttons = tk.Frame(self.root)
        buttons.grid(row=row + 1, column=0, columnspan=3, pady=8)
        tk.Button(buttons, text='Move', width=10, command=self.on_move).pack(side='left', padx=4)
        tk.Button(buttons, text='Stop', width=10, command=self.node.stop).pack(side='left', padx=4)
        tk.Button(buttons, text='Home (90°)', width=10, command=self.on_home).pack(side='left', padx=4)

        self.status = tk.Label(self.root, text='', anchor='w')
        self.status.grid(row=row + 2, column=0, columnspan=3, sticky='w', padx=6, pady=(0, 8))

        self.root.protocol('WM_DELETE_WINDOW', self.root.quit)
        self.refresh_status()

    def on_move(self):
        try:
            target = [float(v.get()) for v in self.target_vars]
        except (tk.TclError, ValueError):
            self.status.config(text='각도는 0~180 숫자로 입력하세요')
            return
        self.node.move_to(target, self.speed_var.get())

    def on_home(self):
        for var, deg in zip(self.target_vars, HOME_DEG):
            var.set(deg)
        self.on_move()

    def refresh_status(self):
        with self.node.lock:
            current = [round(a) for a in self.node.current]
            moving = self.node.moving
        state = '이동 중' if moving else '정지'
        self.status.config(text=f'현재 각도: {current}   [{state}]')
        self.root.after(100, self.refresh_status)

    def run(self):
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    node = MoveGuiNode()
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    MoveGui(node).run()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
