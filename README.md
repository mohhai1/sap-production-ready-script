# Folder Monitoring Script

## Objective

This script monitors a specific folder for events such as folder creation, renaming, and deletion. It prints messages to the screen when these events occur and ensures that the folder is continuously monitored, even if it is renamed or deleted. The script is designed to be portable, executable in a Linux/Unix environment, and operates without requiring network connectivity.

## Features

- Monitors folder events (`created`, `renamed`, `deleted`).
- Handles folder creation, renaming, and deletion with appropriate log messages.
- Portable and executable on vanilla Linux/Unix systems with no network connectivity.
- Configurable periodicity for monitoring folder events.

## How the Script Meets the Requirements

### Minimal Requirements
1. **For Each Event (Creation, Renaming, Deletion)**:
   - The script prints a message to the screen whenever a folder is created, renamed, or deleted.
   
2. **Portability**:
   - The script is designed to run on any Linux/Unix environment without dependencies on network connectivity or external services.
   - It uses Python's built-in libraries (such as `os`, `time`, and `logging`) and `watchdog` for file system event monitoring, making it highly portable across different environments.

### Important Evaluation Criteria

1. **Portability**:
   - The script relies only on standard Python libraries and the `watchdog` library for file system monitoring, which can be easily installed on most systems.
   - No network connectivity is required for the script to operate.

2. **User Friendliness**:
   - Clear and detailed logging messages provide the user with the status of the monitored folder (created, renamed, or deleted).
   - The script allows customization of the folder path and monitoring periodicity using environment variables.
   
3. **Maintainability**:
   - The script is modular and functions are organized logically, making it easy to maintain and update.
   - Clear logging and event-handling mechanisms help in tracking and debugging issues.

4. **Readability**:
   - The code is well-commented and follows consistent naming conventions for variables and functions.
   - Logging messages are clear, with color-coded output for different log levels (INFO, WARNING, CRITICAL).

5. **Scalability**:
   - The script is designed to handle any folder specified via an environment variable, making it easy to scale for additional folders.
   - Future improvements can include making the script more dynamic and adaptable to multiple folders or directories.

6. **Usability**:
   - The script can be customized easily for different folders by adjusting the environment variable (`MONITORED_FOLDER`).
   - Users can change the monitoring frequency by setting the `PERIODICITY` environment variable.
   - Error handling and logging provide useful feedback for the user.

## How to Run the Script

1. **Install Dependencies**:
   The script depends on the `watchdog` library for file system event monitoring. You can install it using pip:

   ```bash
   pip install watchdog termcolor
   ```

2. **Set Environment Variables**:
   - `MONITORED_FOLDER`: The folder to monitor. By default, it is set to `./watched_folder`.
   - `PERIODICITY`: The time interval (in seconds) between each monitoring check. Default is `5` seconds.

   Example:

   ```bash
   export MONITORED_FOLDER=/path/to/folder
   export PERIODICITY=10
   ```

3. **Run the Script**:
   ```bash
   python monitor_folder.py
   ```

   The script will monitor the specified folder for events (creation, renaming, deletion) and log appropriate messages to the terminal.

4. **Running the Script in the Background**:
   To run the script in the background on a Linux/Unix system, you can use `nohup` or `screen` to keep it running even if the terminal is closed:

   - **Using `nohup`**:
     ```bash
     nohup python monitor_folder.py &
     ```

     This command will run the script in the background and redirect all output to the `nohup.out` file. The script will continue running even after you log out.

   - **Using `screen`**:
     1. Start a new screen session:
        ```bash
        screen -S folder-monitor
        ```
     2. Run the script:
        ```bash
        python monitor_folder.py
        ```
     3. Detach from the screen session by pressing `Ctrl+A` followed by `D`.
     4. To reattach to the session:
        ```bash
        screen -r folder-monitor
        ```

5. **Stopping the Script**:
   You can stop the script by pressing `Ctrl+C` in the terminal where the script is running or by killing the background process if it was started with `nohup` or `screen`.

## Future Improvements

In the future, we plan to enhance the script with additional features and deployment capabilities:

### 1. **Docker Integration**:
   - **Docker Image**: Package the script into a Docker image for easier deployment and scalability.
     - A sample `Dockerfile` to package the script:

     ```Dockerfile
     FROM python:3.9-slim

     WORKDIR /app
     COPY . /app

     RUN pip install -r requirements.txt

     CMD ["python", "monitor_folder.py"]
     ```

   - **Docker Compose**: Use `docker-compose.yml` to manage multi-container deployments if needed.

     ```yaml
     version: '3'
     services:
       folder-monitor:
         build: .
         environment:
           MONITORED_FOLDER: /path/to/folder
           PERIODICITY: 5
         volumes:
           - /path/to/folder:/path/to/folder
     ```

### 2. **Kubernetes Deployment**:
   - **Deployment**: The script can be run as a Kubernetes `Deployment` resource with an attached `hostPath` volume pointing to the directory to monitor.
   - **Affinity**: Use Kubernetes affinity settings to ensure the monitoring happens on specific nodes.
     Example of a `Deployment` resource:

     ```yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: folder-monitor
     spec:
       replicas: 1
       selector:
         matchLabels:
           app: folder-monitor
       template:
         metadata:
           labels:
             app: folder-monitor
         spec:
           containers:
             - name: folder-monitor
               image: your-docker-image
               env:
                 - name: MONITORED_FOLDER
                   value: "/path/to/folder"
                 - name: PERIODICITY
                   value: "5"
               volumeMounts:
                 - name: folder-volume
                   mountPath: /path/to/folder
           volumes:
             - name: folder-volume
               hostPath:
                 path: /path/to/folder
     ```

### 3. **Monitoring and Alerts**:
   - **Service & Prometheus Monitoring**: Expose metrics to Prometheus via a `/metrics` endpoint in the script. Create a `Service` and `ServiceMonitor` in Kubernetes for Prometheus scraping.
   
     Example of exposing metrics:

     ```python
     from prometheus_client import start_http_server, Gauge

     folder_status_gauge = Gauge('folder_status', 'Status of the monitored folder')

     def monitor_folder_metrics():
         while True:
             folder_status_gauge.set(1 if os.path.exists(folder_path) else 0)
             time.sleep(5)
     
     start_http_server(8000)  # Expose metrics on port 8000
     monitor_folder_metrics()
     ```

   - **Alerts**: Set up Prometheus alerting rules based on the folder monitoring status (e.g., alert when the folder is deleted or renamed).
   - **Alertmanager and Grafana**: Use Prometheus Alertmanager to send notifications, and visualize these alerts in Grafana dashboards.

     Example Prometheus alert:

     ```yaml
     groups:
     - name: folder-monitor-alerts
       rules:
       - alert: FolderRenamedOrDeleted
         expr: folder_status == 0
         for: 5m
         annotations:
           summary: "The folder has been renamed or deleted"
     ```

### 4. **Automation & Testing**:
   - Automate the testing of the script to validate that it correctly handles all folder events.
   - Implement CI/CD pipelines for deployment and testing.

## Conclusion

This folder monitoring script provides a portable, scalable, and maintainable solution to monitor folder events. It is designed to work in production environments and can be extended with additional features such as Docker integration, Kubernetes deployment, and Prometheus monitoring. Future improvements will focus on automation, alerting, and scaling the solution.
