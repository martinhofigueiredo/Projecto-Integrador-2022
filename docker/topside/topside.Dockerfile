FROM ros:noetic
ENV DEBIAN_FRONTEND=noninteractive

# Install MAVROS and some other dependencies for later
RUN apt-get update && apt-get install -y apt-utils \
  ros-noetic-mavros \
  ros-noetic-mavros-extras   \
  ros-noetic-mavros-msgs \
  vim wget screen net-tools \
  iputils-ping \
  nvidia-container-toolkit
  
# Dependency from https://github.com/mavlink/mavros/blob/master/mavros/README.md
RUN wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh
RUN chmod +x install_geographiclib_datasets.sh
RUN ./install_geographiclib_datasets.sh

# Fix the broken apm_config.yaml
COPY apm_config.yaml /opt/ros/noetic/share/mavros/launch/apm_config.yaml
COPY pymavlinkIMU.py /
RUN apt-get update && apt-get install -y \
  cmake \
  g++ \
  git \
  gnupg gnupg1 gnupg2 \
  libcanberra-gtk* \
  python3-catkin-tools \
  python3-pip \
  python3-tk \
  wget \
  libsdl2-dev \
  gstreamer1.0-gl \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-libav \
  libqt5gui5


RUN pip3 install pymavlink


RUN wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage
RUN chmod +x ./QGroundControl.AppImage

#RUN ./QGroundControl.AppImage --appimage-extract-and-run

# MAVLink Input
EXPOSE 14550

# Envs ROV IP ADDRESS
ENV FCUURL=udp://@192.168.2.2:9000

# Finally the command
COPY entrypoint_topside.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh ${FCUURL}

