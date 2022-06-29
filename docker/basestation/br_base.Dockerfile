# Base Image for TurtleBot3 Simulation
FROM nvidia_ros:latest
SHELL ["/bin/bash", "-c"]

# Install basic apt packages
RUN apt-get update && apt-get install -y \
  cmake \
  g++ \
  git \
  gnupg gnupg1 gnupg2 \
  libcanberra-gtk* \
  python3-catkin-tools \
  python3-pip \
  python3-tk \
  wget

# Install additional ROS packages
RUN apt-get install -y \
  ros-noetic-gmapping \
  ros-noetic-navigation \
  ros-noetic-py-trees \
  ros-noetic-py-trees-ros 
  
# Installs for building rqt_py_trees from source
# (Once bug is fixed, replace with apt-get install ros-noetic-rqt-py-trees)
RUN apt-get install -y graphviz graphviz-dev
RUN pip3 install pygraphviz

# Create Catkin workspace with TurtleBot3 package and behavior tree source
RUN mkdir -p /bluerov_ws/src
# RUN mkdir -p /turtlebot3_ws/src \
#  && cd /turtlebot3_ws/src \
#  && source /opt/ros/noetic/setup.bash \
#  && catkin_init_workspace \
#  && git clone -b noetic-devel https://github.com/ROBOTIS-GIT/turtlebot3.git \
#  && git clone -b noetic-devel https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git \
#  && git clone -b noetic-devel https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git \
#  && git clone -b master https://github.com/BehaviorTree/BehaviorTree.CPP.git behavior_tree_cpp \
#  && git clone -b master https://github.com/BehaviorTree/Groot.git groot \
#  && git clone -b devel https://github.com/sea-bass/rqt_py_trees.git

# Build the base Catkin workspace
RUN pip3 install osrf-pycommon
#RUN cd /turtlebot3_ws \
# && source /opt/ros/noetic/setup.bash \
# && rosdep install -y --from-paths src --ignore-src \
# && catkin build -j4

# Remove display warnings
RUN mkdir /tmp/runtime-root
ENV XDG_RUNTIME_DIR "/tmp/runtime-root"
ENV NO_AT_BRIDGE 1

# Set up the work directory and entrypoint
WORKDIR /bluerov_ws
COPY ./docker/entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]