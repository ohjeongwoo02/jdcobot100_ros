import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node



def generate_launch_description():
    share_dir = get_package_share_directory('jdcobot_100_description')
    urdf = os.path.join(share_dir, 'urdf', 'jdcobot_100_description.urdf')
    rviz_config = os.path.join(share_dir, 'rviz', 'rviz_set.rviz')

    with open(urdf, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='jdcobot_100_description',
            executable='jdcobot_move_gui',
            name='jdcobot_move_gui',
            output='screen'
        ),
        Node(
            package='jdcobot_100_description',
            executable='jdcobot_control',
            name='jdcobot_control',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config]
        ),
    ])
