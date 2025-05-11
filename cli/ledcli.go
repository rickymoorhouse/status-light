package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"time"
)

func isWebcamActive(ctx context.Context) bool {
	// Run the `log stream` command to monitor webcam activity
	// log stream --predicate '(eventMessage CONTAINS "AVCaptureSessionDidStartRunningNotification" || eventMessage CONTAINS "AVCaptureSessionDidStopRunningNotification")' --info
	cmd := exec.CommandContext(ctx, "log", "stream", "--predicate", `(eventMessage CONTAINS "AVCaptureSessionDidStartRunningNotification" || eventMessage CONTAINS "AVCaptureSessionDidStopRunningNotification" ||eventMessage CONTAINS "stopRunning")`, "--info")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Printf("Error creating stdout pipe: %v\n", err)
		return false
	}

	if err := cmd.Start(); err != nil {
		fmt.Printf("Error starting log stream: %v\n", err)
		return false
	}

	// Create a channel to signal webcam activity
	webcamActive := make(chan bool)

	// Process the log stream in a separate goroutine
	go func() {
		scanner := bufio.NewScanner(stdout)
		for scanner.Scan() {
			line := scanner.Text()
			if line != "" {
				if strings.Contains(line, "Filtering") {
					// Ignore filtering message
				} else if strings.Contains(line, "AVCaptureSessionDidStartRunningNotification") {
					//fmt.Println("Webcam is active")
					webcamActive <- true
				} else if strings.Contains(line, "topRunning") {
					fmt.Println(line)
					fmt.Println("Webcam is inactive")
					turnOffLight()
					webcamActive <- false
				} else {
					fmt.Println(line)
				}
			}
		}

		if err := scanner.Err(); err != nil {
			fmt.Printf("Error reading log stream: %v\n", err)
		}

		// Close the channel when the log stream ends
		close(webcamActive)
	}()

	// Listen for webcam activity updates
	for {
		select {
		case active, ok := <-webcamActive:
			if !ok {
				// Channel closed, exit the function
				return false
			}
			return active
		case <-ctx.Done():
			// Context canceled, stop the log stream
			cmd.Process.Kill()
			return false
		}
	}
}

func turnOffLight() {
	// Construct the API URL
	host := os.Getenv("LED_SERVER_HOST")
	apiURL := fmt.Sprintf("http://%s/leds", host)
	// Make the DELETE request
	req, err := http.NewRequest("DELETE", apiURL, nil)
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Error making DELETE request: %v\n", err)
		os.Exit(1)
	}
	defer resp.Body.Close()
	if resp.StatusCode == http.StatusOK {
		fmt.Println("DELETE request sent to turn off LEDs successfully")
	} else {
		fmt.Printf("Failed to turn off LEDs. Status code: %d\n", resp.StatusCode)
	}
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && s[:len(substr)] == substr
}

func main() {
	// Define command-line flags for RGB values
	red := flag.Int("r", 0, "Red value (0-255)")
	green := flag.Int("g", 0, "Green value (0-255)")
	blue := flag.Int("b", 0, "Blue value (0-255)")
	flag.Parse()

	// Get server details from environment variables
	host := os.Getenv("LED_SERVER_HOST")

	if host == "" {
		fmt.Println("Error: LED_SERVER_HOST environment variable must be set")
		os.Exit(1)
	}

	// Create a context to manage the log stream process
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	// Construct the API URL
	apiURL := fmt.Sprintf("http://%s/leds?r=%d&g=%d&b=%d", host, *red, *green, *blue)

	// Periodically check webcam status
	for {
		if isWebcamActive(ctx) {

			// Make the POST request
			resp, err := http.Post(apiURL, "application/json", nil)
			if err != nil {
				fmt.Printf("Error making POST request: %v\n", err)
				os.Exit(1)
			}
			defer resp.Body.Close()
			// Check the response
			if resp.StatusCode == http.StatusOK {
				fmt.Println("POST request set LED color successfully!")
			} else {
				fmt.Printf("Failed to set LED color. Status code: %d\n", resp.StatusCode)
			}

		} else {
			turnOffLight()
		}

		// Wait for 5 seconds before checking again
		time.Sleep(5 * time.Second)
	}
}
