# Use Python 3.9
FROM python:3.9

# Set working directory to /code
WORKDIR /code

# 1. Copy the "app" folder from your computer to "/code/app" in the container
COPY app /code/app

# 2. Set the working directory INSIDE the app folder
WORKDIR /code/app

# 3. Now "requirements.txt" is right here in the current folder
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Create a user (Required by Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

EXPOSE 7860

# Command to run the app
CMD ["python", "app.py"]