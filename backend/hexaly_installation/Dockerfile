FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget

ARG HX_MAJOR_VERSION=14_0
ARG HX_RELEASE_DATE=20251029
ARG HX_VERSION=${HX_MAJOR_VERSION}_${HX_RELEASE_DATE}

RUN wget -v https://www.hexaly.com/downloads/${HX_VERSION}/Hexaly_${HX_VERSION}_Linux64.run

# Make the installer executable
RUN chmod +x ./Hexaly_${HX_VERSION}_Linux64.run

# Install Hexaly in silent mode
RUN ./Hexaly_${HX_VERSION}_Linux64.run --nointeractive

COPY license.dat /opt/hexaly_${HX_MAJOR_VERSION}/license.dat

WORKDIR /workspace

CMD ["bash"]