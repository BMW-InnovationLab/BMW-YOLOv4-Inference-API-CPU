# Use Python 3 base image
FROM python:3

# Add maintainer information
LABEL maintainer="antoine.charbel@inmind.ai"

# Add project
COPY src/main /main

# Install requirements
COPY docker/requirements.txt .
RUN pip install -r requirements.txt

# Set work dir
WORKDIR /main

# Set init command
CMD ["uvicorn", "start:app", "--host", "0.0.0.0", "--port", "7770"]