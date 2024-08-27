FROM public.ecr.aws/lambda/python:3.10

# Copy only the requirements file to the container
COPY ./requirements.txt .

# Install Python packages from requirements file
RUN pip install --no-cache-dir --upgrade -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy the entire app directory to the container
COPY ./API ${LAMBDA_TASK_ROOT}

# Specify the command to run when the container starts
CMD ["api.handler"]
