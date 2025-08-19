FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY src/ ./src/

# Optional debug: list files
RUN echo "Files in /var/task:" && ls -R /var/task

ENTRYPOINT ["python3", "-m", "awslambdaric"]
# Set the Lambda function handler
CMD ["main.lambda_handler"]
