import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature
import serial


class TempSerialPublisher(Node):
    def __init__(self):
        super().__init__('temp_serial_publisher')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('frame_id', 'temp_sensor')

        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value
        self.frame_id = self.get_parameter('frame_id').value

        self.publisher_ = self.create_publisher(Temperature, 'temperature', 10)
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=0)
        self.buffer = ''
        self.timer = self.create_timer(0.05, self.read_serial)  # 20Hz로 시리얼 확인
        self.get_logger().info(f"start: {port} @ {baudrate}")

    def read_serial(self):
        data = self.ser.read(self.ser.in_waiting or 1)
        if not data:
            return
        self.buffer += data.decode(errors='ignore')

        # 줄 단위로 끊어서 처리 (아두이노 Serial.println -> "25.00\r\n")
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            line = line.strip()
            if not line:
                continue
            try:
                value = float(line)
            except ValueError:
                self.get_logger().warn(f"숫자가 아닌 데이터 무시: '{line}'")
                continue

            msg = Temperature()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self.frame_id
            msg.temperature = value
            msg.variance = 0.0
            self.publisher_.publish(msg)
            self.get_logger().info(f"temperature: {value:.2f}")

    def destroy_node(self):
        self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TempSerialPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
