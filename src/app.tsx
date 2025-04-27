interface Detection {
  class: string;
  confidence: number;
  coordinates: number[];
  mask?: number[][];
}

function App() {
  const [detections, setDetections] = useState<Detection[]>([]);
  // ... rest of the React code remains type-safe
}
