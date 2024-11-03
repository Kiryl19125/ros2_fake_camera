import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class VideoPublisher(Node):
    def __init__(self, node_name: str):
        super().__init__(node_name)

        self.declare_parameter('video_path', '')

        video_path = self.get_parameter('video_path').get_parameter_value().string_value
        if video_path:
            self.get_logger().info(f"Video file path provided: {video_path}")
            self.cap = cv2.VideoCapture(video_path)
        else:
            self.get_logger().info("No video file path provided. Using webcam as the video source.")
            self.cap = cv2.VideoCapture(0)  # 0 is typically the default camera

        if not self.cap.isOpened():
            self.get_logger().error("Failed to open video source.")
            rclpy.shutdown()
            return

        self._publisher = self.create_publisher(Image, 'video_frames', 10)

        self.bridge = CvBridge()

        if self.cap.get(cv2.CAP_PROP_FPS) == 0:
            frame_rate = 30
        else:
            frame_rate = self.cap.get(cv2.CAP_PROP_FPS)

        self.timer = self.create_timer(1.0 / frame_rate, self.publish_frame)

        self.get_logger().info("Video Publisher Node has been started.")

    def publish_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().info("No more frames to read.")
            self.cap.release()
            self.destroy_node()
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")

        self._publisher.publish(msg)
        self.get_logger().info("Published a frame.")

def main(args=None):
    rclpy.init(args=args)
    video_publisher = VideoPublisher("video_publisher")
    rclpy.spin(video_publisher)

    video_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
