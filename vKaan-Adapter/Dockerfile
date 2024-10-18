# If the harbor repo isn't accessible, the base-adapter image can be built locally.
# Go to the vmware-aria-operations-integration-sdk repository, and run the build_images.py script located at images/build_images.py
FROM projects.registry.vmware.com/vmware_aria_operations_integration_sdk/base-adapter:python-1.0.0
COPY commands.cfg .
COPY adapter_requirements.txt .
RUN pip3 install -r adapter_requirements.txt --upgrade
COPY app app