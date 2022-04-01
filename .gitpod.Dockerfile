FROM gitpod/workspace-full

# Install custom tools, runtime, etc.
RUN sudo apt-get update \
    #&& sudo apt-get install iverilog -y \
    && sudo apt install python3-numpy python3-opencv libopencv-dev\
    && sudo apt install python3-gst-1.0 gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-libav\
    && sudo rm -rf /var/lib/apt/lists/*
    && pip3 install mavproxy