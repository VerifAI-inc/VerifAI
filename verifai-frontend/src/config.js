let API_BASE_URL = "";

if (process.env.REACT_APP_API_BASE_URL) {
  API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
} else if (window.location.hostname === "localhost") {
  API_BASE_URL = "http://localhost:8000";
} else {
  // Update this with your backend URL
  API_BASE_URL = "https://verifai-4g9a.onrender.com"; // or .fly.dev
}

export default API_BASE_URL;


// const backendHost = window.location.hostname;
// const backendPort = "8000";

// const API_BASE_URL = `http://${backendHost}:${backendPort}/`;

// export default API_BASE_URL;
