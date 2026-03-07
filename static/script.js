const video = document.getElementById("video");
const canvas = document.getElementById("drawCanvas");
const ctx = canvas.getContext("2d");

const saveBtn = document.getElementById("saveBtn");
const clearBtn = document.getElementById("clearBtn");
const gallery = document.getElementById("gallery");
const statusText = document.getElementById("statusText");

const homePage = document.getElementById("homePage");
const drawSection = document.getElementById("drawSection");
const gallerySection = document.getElementById("gallerySection");

const showDrawBtn = document.getElementById("showDrawBtn");
const showGalleryBtn = document.getElementById("showGalleryBtn");

const backHomeBtn = document.getElementById("backHomeBtn");
const backHomeBtn2 = document.getElementById("backHomeBtn2");

let prevX = null;
let prevY = null;

let cameraStarted = false;
let cameraInstance = null;

function showHome() {
  homePage.classList.remove("hidden");
  drawSection.classList.add("hidden");
  gallerySection.classList.add("hidden");
}

async function showDraw() {
  homePage.classList.add("hidden");
  drawSection.classList.remove("hidden");
  gallerySection.classList.add("hidden");

  // wait a moment so the section is visible before sizing canvas
  setTimeout(async () => {
    if (!cameraStarted) {
      await startCamera();
    } else {
      resizeCanvas();
    }
  }, 100);
}

async function showGallery() {
  homePage.classList.add("hidden");
  drawSection.classList.add("hidden");
  gallerySection.classList.remove("hidden");
  await loadGallery();
}

showDrawBtn.onclick = showDraw;
showGalleryBtn.onclick = showGallery;
backHomeBtn.onclick = showHome;
backHomeBtn2.onclick = showHome;

function resizeCanvas() {
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
}

clearBtn.onclick = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  prevX = null;
  prevY = null;
};

async function saveDrawing() {
  const off = document.createElement("canvas");
  off.width = canvas.width;
  off.height = canvas.height;

  const offctx = off.getContext("2d");
  offctx.fillStyle = "black";
  offctx.fillRect(0, 0, off.width, off.height);
  offctx.drawImage(canvas, 0, 0);

  const image = off.toDataURL("image/png");

  const res = await fetch("/save-image", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ image })
  });

  const data = await res.json();

  if (data.success) {
    statusText.textContent = "Saved image";
  } else {
    statusText.textContent = "Save failed";
  }
}

saveBtn.onclick = saveDrawing;

document.addEventListener("keydown", (e) => {
  if (e.key === "s" || e.key === "S") {
    saveDrawing();
  }
  if (e.key === "c" || e.key === "C") {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    prevX = null;
    prevY = null;
  }
});

async function loadGallery() {
  const res = await fetch("/gallery-images");
  const data = await res.json();

  gallery.innerHTML = "";

  data.images.forEach((src) => {
    const img = document.createElement("img");
    img.src = src + "?t=" + Date.now();
    gallery.appendChild(img);
  });
}

const hands = new Hands({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
});

hands.setOptions({
  maxNumHands: 1,
  modelComplexity: 1,
  minDetectionConfidence: 0.7,
  minTrackingConfidence: 0.7
});

hands.onResults((results) => {
  if (!canvas.width || !canvas.height) {
    resizeCanvas();
  }

  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    const hand = results.multiHandLandmarks[0];

    const tip = hand[8];
    const joint = hand[6];

    // mirrored x to match mirrored camera
    const x = (1 - tip.x) * canvas.width;
    const y = tip.y * canvas.height;

    const fingerUp = tip.y < joint.y;

    if (fingerUp) {
      if (prevX === null || prevY === null) {
        prevX = x;
        prevY = y;
      }

      ctx.beginPath();
      ctx.moveTo(prevX, prevY);
      ctx.lineTo(x, y);
      ctx.strokeStyle = "white";
      ctx.lineWidth = 5;
      ctx.lineCap = "round";
      ctx.stroke();

      prevX = x;
      prevY = y;

      statusText.textContent = "Drawing...";
    } else {
      prevX = null;
      prevY = null;
      statusText.textContent = "Hand detected - not drawing";
    }
  } else {
    prevX = null;
    prevY = null;
    statusText.textContent = "No hand detected";
  }
});

async function startCamera() {
  if (cameraStarted) return;

  const stream = await navigator.mediaDevices.getUserMedia({
    video: true,
    audio: false
  });

  video.srcObject = stream;

  video.onloadedmetadata = async () => {
    resizeCanvas();

    cameraInstance = new Camera(video, {
      onFrame: async () => {
        await hands.send({ image: video });
      },
      width: 640,
      height: 480
    });

    cameraInstance.start();
    cameraStarted = true;
    statusText.textContent = "Camera started";
  };
}