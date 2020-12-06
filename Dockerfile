# Core tag comes fom build script
# Tells which image to use as a base
ARG liberty_core_tag
FROM libertycore:$liberty_core_tag

ARG DEBIAN_FRONTEND=noninteractive

# Copy over liberty code into container
COPY . /liberty

# Run Liberty Prime
WORKDIR /liberty/liberty
CMD python3 ./bot.py
