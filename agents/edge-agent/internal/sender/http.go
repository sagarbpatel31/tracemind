package sender

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Client sends telemetry data to the TraceMind API.
type Client struct {
	apiURL     string
	deviceID   string
	deviceName string
	httpClient *http.Client
}

// NewClient creates a new sender client.
func NewClient(apiURL, deviceID, deviceName string) *Client {
	return &Client{
		apiURL:     apiURL,
		deviceID:   deviceID,
		deviceName: deviceName,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// RegisterDevice registers this device with the TraceMind API.
func (c *Client) RegisterDevice() error {
	payload := map[string]string{
		"device_id":   c.deviceID,
		"device_name": c.deviceName,
	}
	return c.post("/api/v1/devices/register", payload)
}

// MetricsPayload is the body sent to the metrics ingest endpoint.
type MetricsPayload struct {
	DeviceID  string      `json:"device_id"`
	Timestamp time.Time   `json:"timestamp"`
	Metrics   interface{} `json:"metrics"`
}

// SendMetrics posts a metrics snapshot to the API.
func (c *Client) SendMetrics(metrics interface{}) error {
	payload := MetricsPayload{
		DeviceID:  c.deviceID,
		Timestamp: time.Now().UTC(),
		Metrics:   metrics,
	}
	return c.post("/api/v1/ingest/metrics", payload)
}

// LogEntry represents a single log line to ingest.
type LogEntry struct {
	DeviceID  string    `json:"device_id"`
	Timestamp time.Time `json:"timestamp"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
}

// SendLog posts a log entry to the API.
func (c *Client) SendLog(level, message string) error {
	entry := LogEntry{
		DeviceID:  c.deviceID,
		Timestamp: time.Now().UTC(),
		Level:     level,
		Message:   message,
	}
	return c.post("/api/v1/ingest/logs", entry)
}

// post marshals payload to JSON and POSTs it to the given path.
func (c *Client) post(path string, payload interface{}) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	url := c.apiURL + path
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("send request to %s: %w", path, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 300 {
		return fmt.Errorf("unexpected status %d from %s", resp.StatusCode, path)
	}
	return nil
}
