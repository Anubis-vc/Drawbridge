const streamButton = document.getElementById("toggle-stream-btn");
const streamView = document.getElementById("stream-view");

const VIDEO_API_BASE = "http://127.0.0.1:8000/video";
const STREAM_ENDPOINT = `${VIDEO_API_BASE}/stream`;
let isStreaming = false;

const setUiForStreaming = (running) => {
  isStreaming = running;
  streamButton.textContent = running ? "Stop Stream" : "Start Stream";

  if (running) {
    // force a new MJPEG connection on restart with ?t=....
    streamView.src = `${STREAM_ENDPOINT}?t=${Date.now()}`;
  } else {
    streamView.removeAttribute("src");
  }
};

const brieflyDisableButton = () => {
  streamButton.disabled = true;
  setTimeout(() => {
    streamButton.disabled = false;
  }, 1000);
};

const refreshStatus = async () => {
  try {
    const response = await fetch(`${VIDEO_API_BASE}/status`);
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    const video_response = await response.json();
    const video_status = video_response.video_status;
    const running = "running" === video_status.toLowerCase();
    setUiForStreaming(running);
  } catch (error) {
    console.error("Failed to get stream status:", error);
    setUiForStreaming(false);
  }
};

streamButton.addEventListener("click", async () => {
  brieflyDisableButton();
  const nextAction = isStreaming ? "stop" : "start";
  try {
    const response = await fetch(`${VIDEO_API_BASE}/${nextAction}`);
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    await refreshStatus();
  } catch (error) {
    console.error(`Failed to ${nextAction} stream:`, error);
    setUiForStreaming(false);
    streamButton.textContent = "Error";
  }
});

refreshStatus();
