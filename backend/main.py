import asyncio
import subprocess
import webbrowser
import os
from rocket_data_analysis.data_analysis import read_and_write_data, websocket_handler
import websockets

####### TODO: #######
# 1. Add error handling and logging for better debugging and monitoring
# 2. Add option to connect to webSockect through button in the dashboard
# 3. Add option to start and stop data generation and transmition from the dashboard
# 4. Do not start the program immediately, wait for the user to click the button in the dashboard (add a button in the dashboard to start the program)


# this function is used to start the HTTP server and open the dashboard in a web browser
# it is called in the main function
def start_http_server():
    dashboard_dir = os.path.abspath("dashboard/public")
    subprocess.Popen(["python", "-m", "http.server", "8080"], cwd=dashboard_dir)
    webbrowser.open("http://localhost:8080/dashboard.html")

# WebSocket handler
async def main():
    start_http_server() # Start the HTTP server and open the dashboard in a web browser
    print("[System] Starting WebSocket server on ws://localhost:8765")      # log message
    server = await websockets.serve(websocket_handler, "localhost", 8765)   # Start the WebSocket server

    print("[System] WebSocket server started")  # log message
    # run the funntion while the server is running
    
    await asyncio.gather(
        read_and_write_data(),
        server.wait_closed()
    )

# Main function to start the WebSocket server and data generation
# TODO: Add error handling and logging for better debugging and monitoring
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:       # Handle keyboard interrupt (Ctrl+C) to stop the server gracefully
        print("Interrupted. Shutting down...")  