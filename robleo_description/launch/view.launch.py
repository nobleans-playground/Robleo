import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    rviz_config_dir = os.path.join(get_package_share_directory('robleo_description'),
                                   'rviz', 'model.rviz')

    urdf = os.path.join(get_package_share_directory('robleo_description'),
                        'urdf', 'robleo.urdf')

    # Hack to solve rviz not rendering cylinders 
    # (https://answers.ros.org/question/374069/rviz2-only-render-boxes/)
    os.environ["LC_NUMERIC"] = "en_US.UTF-8"

    # Read robot description
    with open(urdf, 'r') as infp:
        robot_desc = infp.read()

    rsp_params = {'robot_description': robot_desc}

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[rsp_params]),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            output='screen',
            parameters=[rsp_params]),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            output='screen')
    ])
