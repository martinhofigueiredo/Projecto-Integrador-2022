FROM ros:noetic
ENV DEBIAN_FRONTEND=noninteractive

# Install MAVROS and some other dependencies for later
RUN apt-get update && apt-get install -y apt-utils ros-noetic-mavros ros-noetic-mavros-extras ros-noetic-mavros-msgs vim wget screen qgroundcontrol

# Dependency from https://github.com/mavlink/mavros/blob/master/mavros/README.md
RUN wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh
RUN chmod +x install_geographiclib_datasets.sh
RUN ./install_geographiclib_datasets.sh

# Fix the broken apm_config.yaml
COPY apm_config.yaml /opt/ros/noetic/share/mavros/launch/apm_config.yaml

# MAVLink Input
EXPOSE 5760

# Envs ROV IP ADDRESS
ENV FCUURL=tcp://192.168.2.2:5760 

# Finally the command
COPY entrypoint_topside.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh ${FCUURL}

