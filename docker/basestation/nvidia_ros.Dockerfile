
# Ubuntu 20.04 image with NVIDIA CUDA + OpenGL and ROS Noetic
FROM nvidia/cudagl:11.1.1-base-ubuntu20.04

# Install basic apt packages
RUN apt-get update && apt-get install -y locales lsb-release

# Set up locale and UTF-8 encoding, mostly so setup runs without errors
ARG DEBIAN_FRONTEND=noninteractive
#RUN locale-gen en_US.UTF-8
#ENV PYTHONIOENCODING UTF-8
#ENV LC_ALL en_US.UTF-8
#ENV LANG en_US.UTF-8
#ENV LANGUAGE en_US:en
RUN dpkg-reconfigure locales

# Install ROS Noetic
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
RUN apt-get update \
 && apt-get install -y --no-install-recommends ros-noetic-desktop-full
RUN apt-get install -y --no-install-recommends python3-rosdep
RUN rosdep init \
 && rosdep fix-permissions \
 && rosdep update
RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc