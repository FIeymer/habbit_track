# Use the base image with Python
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app_folder

# Copy dependencies
COPY app_folder/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app_folder/ /app_folder/
COPY /server_folder/models.py .
COPY /server_folder/database.py .

# Run the bot
CMD ["python", "-c", "from bot_api import bot; bot.infinity_polling()"]

