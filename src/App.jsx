import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const DUSTBIN_COLORS = {
  Brown: "#8D5524",
  Blue: "#1976D2",
  Green: "#388E3C",
  Red: "#D32F2F",
  Black: "#212121",
  Yellow: "#FFD600",
};

const App = () => {
  const webcamRef = useRef(null);
  const [imgSrc, setImgSrc] = useState(null);
  const [results, setResults] = useState([]);
  const [mode, setMode] = useState("webcam");
  const [loading, setLoading] = useState(false);

  // Capture from webcam and analyze
  const capture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImgSrc(imageSrc);
    await analyzeImage(imageSrc);
  };

  // Analyze image (webcam or upload)
  const analyzeImage = async (imageSrc) => {
    setLoading(true);
    setResults([]);
    try {
      const blob = await (await fetch(imageSrc)).blob();
      const formData = new FormData();
      formData.append("file", blob, "capture.jpg");
      const res = await axios.post("http://localhost:8000/predict", formData);
      setResults(res.data.predictions);
    } catch (err) {
      alert("Error analyzing image.");
    }
    setLoading(false);
  };

  // Handle file upload
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImgSrc(URL.createObjectURL(file));
    setLoading(true);
    setResults([]);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await axios.post("http://localhost:8000/predict", formData);
      setResults(res.data.predictions);
    } catch (err) {
      alert("Error analyzing image.");
    }
    setLoading(false);
  };

  // UI
  return (
    <div className="container">
      <h1>♻️ Smart Waste Classifier</h1>
      <div className="mode-toggle">
        <button
          className={mode === "webcam" ? "active" : ""}
          onClick={() => {
            setMode("webcam");
            setImgSrc(null);
            setResults([]);
          }}
        >
          Webcam
        </button>
        <button
          className={mode === "upload" ? "active" : ""}
          onClick={() => {
            setMode("upload");
            setImgSrc(null);
            setResults([]);
          }}
        >
          Upload Image
        </button>
      </div>

      <div className="input-section">
        {mode === "webcam" ? (
          <div>
            {!imgSrc ? (
              <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                width={400}
                videoConstraints={{ facingMode: "environment" }}
                style={{ borderRadius: "12px" }}
              />
            ) : (
              <img
                src={imgSrc}
                alt="capture"
                width={400}
                style={{ borderRadius: "12px", boxShadow: "0 2px 8px #0002" }}
              />
            )}
            <div style={{ marginTop: "1rem" }}>
              {!imgSrc ? (
                <button onClick={capture} disabled={loading}>
                  {loading ? "Analyzing..." : "Capture & Analyze"}
                </button>
              ) : (
                <button
                  onClick={() => {
                    setImgSrc(null);
                    setResults([]);
                  }}
                  disabled={loading}
                >
                  Retake
                </button>
              )}
            </div>
          </div>
        ) : (
          <div>
            <input
              type="file"
              accept="image/*"
              onChange={handleUpload}
              disabled={loading}
            />
            {imgSrc && (
              <img
                src={imgSrc}
                alt="upload"
                width={400}
                style={{ borderRadius: "12px", marginTop: "1rem", boxShadow: "0 2px 8px #0002" }}
              />
            )}
          </div>
        )}
      </div>

      <div className="results">
        {loading && <div className="loading">Analyzing...</div>}
        {!loading && results.length > 0 && (
          <div>
            <h2>Detected Waste</h2>
            <ul>
              {results.map((r, i) => (
                <li key={i} className="result-card">
                  <span className="waste-type">{r.label}</span>
                  <span className="confidence">
                    ({(r.confidence * 100).toFixed(1)}%)
                  </span>
                  <div className="dustbin-row">
                    <span
                      className="dustbin-color"
                      style={{
                        background: DUSTBIN_COLORS[r.dustbin_color] || "#888",
                      }}
                    />
                    <span>
                      Dispose in:{" "}
                      <b style={{ color: DUSTBIN_COLORS[r.dustbin_color] || "#333" }}>
                        {r.dustbin_color}
                      </b>{" "}
                      dustbin
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Stylish UI */}
      <style>{`
        body { background: #eef3f6; }
        .container {
          font-family: 'Segoe UI', sans-serif;
          max-width: 600px;
          margin: 2rem auto;
          padding: 2rem;
          background: #f4f6f8;
          border-radius: 20px;
          box-shadow: 0 4px 24px #0001;
        }
        h1 {
          text-align: center;
          color: #2e7d32;
          font-weight: 700;
          margin-bottom: 1.5rem;
        }
        .mode-toggle {
          display: flex;
          justify-content: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }
        .mode-toggle button {
          padding: 0.5rem 1.5rem;
          border-radius: 8px;
          border: none;
          background: #388e3c;
          color: #fff;
          font-size: 1rem;
          cursor: pointer;
          transition: background 0.2s;
        }
        .mode-toggle button.active,
        .mode-toggle button:hover {
          background: #2e7d32;
        }
        .input-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-bottom: 2rem;
        }
        button {
          padding: 0.6rem 1.6rem;
          border-radius: 8px;
          border: none;
          background: #1976d2;
          color: #fff;
          font-size: 1rem;
          cursor: pointer;
          margin-top: 0.5rem;
          transition: background 0.2s;
        }
        button:disabled {
          background: #aaa;
          cursor: not-allowed;
        }
        button:hover:not(:disabled) {
          background: #1565c0;
        }
        .results {
          margin-top: 2rem;
        }
        .results h2 {
          color: #1976d2;
          margin-bottom: 1rem;
          text-align: center;
        }
        ul {
          list-style: none;
          padding: 0;
        }
        .result-card {
          background: #fff;
          margin: 0.5rem 0;
          padding: 1rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px #0001;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
        }
        .waste-type {
          font-size: 1.2rem;
          font-weight: 600;
          color: #333;
        }
        .confidence {
          font-size: 0.95rem;
          color: #666;
          margin-left: 0.5rem;
        }
        .dustbin-row {
          display: flex;
          align-items: center;
          margin-top: 0.5rem;
        }
        .dustbin-color {
          display: inline-block;
          width: 22px;
          height: 22px;
          border-radius: 50%;
          margin-right: 0.7rem;
          border: 2px solid #eee;
          box-shadow: 0 1px 3px #0001;
        }
        .loading {
          text-align: center;
          color: #1976d2;
          font-size: 1.1rem;
          margin-top: 1.5rem;
        }
      `}</style>
    </div>
  );
};

export default App;
