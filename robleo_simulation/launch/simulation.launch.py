import os
import pathlib
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch.substitutions.path_join_substitution import PathJoinSubstitution
from launch import LaunchDescription
from launch_ros.actions import Node
import launch
from ament_index_python.packages import get_package_share_directory
from webots_ros2_driver.webots_launcher import WebotsLauncher


def generate_launch_description():
    simulation_dir = get_package_share_directory('robleo_simulation')
    world = LaunchConfiguration('world')
    webots_description = pathlib.Path(os.path.join(simulation_dir, 'resource', 'robleo_webots.urdf')).read_text()
    ros2_control_params = os.path.join(simulation_dir, 'resource', 'ros2control.yml')
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    webots = WebotsLauncher(
        world=PathJoinSubstitution([simulation_dir, 'worlds', world])
    )

    controller_manager_timeout = ['--controller-manager-timeout', '50'] if os.name == 'nt' else []
    controller_manager_prefix = 'python.exe' if os.name == 'nt' else "bash -c 'sleep 10; $0 $@' "

    diffdrive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner.py',
        output='screen',
        prefix=controller_manager_prefix,
        arguments=['diffdrive_controller'] + controller_manager_timeout,
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner.py',
        output='screen',
        prefix=controller_manager_prefix,
        arguments=['joint_state_broadcaster'] + controller_manager_timeout,
    )

    robleo_driver = Node(
        package='webots_ros2_driver',
        executable='driver',
        output='screen',
        parameters=[
            {'robot_description': webots_description,
             'use_sim_time': use_sim_time},
            ros2_control_params
        ],
        remappings=[
            ('/diffdrive_controller/cmd_vel_unstamped', '/cmd_vel')
        ]
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': '<robot name=""><link name=""/></robot>'
        }],
    )

    footprint_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint'],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='world.wbt',
            description='Example office world'
        ),
        joint_state_broadcaster_spawner,
        diffdrive_controller_spawner,
        webots,
        robot_state_publisher,
        robleo_driver,
        footprint_publisher,
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=webots,
                on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
            )
        )
    ])
