let API_BASE_URL = "";

if (window.location.hostname === "localhost") {
  API_BASE_URL = "http://localhost:8000/";
} else {
  API_BASE_URL = "https://verifai-backend.onrender.com/";
}

export default API_BASE_URL;


// const backendHost = window.location.hostname;
// const backendPort = "8000";

// const API_BASE_URL = `http://${backendHost}:${backendPort}/`;

// export default API_BASE_URL;
