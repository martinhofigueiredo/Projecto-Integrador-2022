# Overlay Development Image for TurtleBot3 Simulation
FROM bluerov_base:latest

# Create an overlay Catkin workspace
RUN source /opt/ros/noetic/setup.bash \
 && mkdir -p /overlay_ws/src \
 && cd /overlay_ws \ 
 && catkin_init_workspace
COPY ./tb3_autonomy/ /overlay_ws/src/tb3_autonomy/
COPY ./tb3_worlds/ /overlay_ws/src/tb3_worlds/
RUN source /opt/ros/noetic/setup.bash \
 && cd /overlay_ws \
 && catkin config --extend /turtlebot3_ws/devel \
 && catkin build -j4

# Set up the work directory and entrypoint
WORKDIR /overlay_ws
COPY ./docker/entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]