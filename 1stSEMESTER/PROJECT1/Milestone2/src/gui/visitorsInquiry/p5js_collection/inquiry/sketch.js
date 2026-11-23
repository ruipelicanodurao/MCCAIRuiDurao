let video;
let hands = [];
let modelStatus = "A carregar o modelo de mãos…";

const MIN_ANGLE = 145;
const MIN_FINGERS = 3;

const FINGERS = [
    [5, 6, 7, 8],     // Indicador
    [9, 10, 11, 12],  // Médio
    [13, 14, 15, 16], // Anelar
    [17, 18, 19, 20]  // Mindinho
];

function setup() {
    createCanvas(windowWidth, windowHeight);
    pixelDensity(1);

    video = createCapture(VIDEO, () => {
        startHandPose();
    });
    video.hide();
}

async function startHandPose() {
    try {
        const handPose = await ml5.handPose();
        if (handPose.ready) await handPose.ready;

        modelStatus = "A iniciar a deteção de mãos…";

        await handPose.detectStart(video, (results) => {
            hands = results ?? [];
            modelStatus = "";
        });
    } catch (error) {
        modelStatus = `Erro no HandPose: ${error.message}`;
        console.error(error);
    }
}

function draw() {
    background(0);

    const camera = video?.elt;
    if (!camera?.videoWidth || camera.readyState < 2) {
        drawStatus("À espera da imagem da webcam…");
        return;
    }

    // Mostrar a webcam em espelho.
    push();
    translate(width, 0);
    scale(-1, 1);
    image(video, 0, 0, width, height);
    pop();

    noStroke();
    fill(255, 0, 0, 80);
    rect(0, 0, width / 2, height);
    fill(0, 255, 0, 80);
    rect(width / 2, 0, width / 2, height);

    fill(255, 255, 0);
    for (const hand of hands) {
        for (const point of hand.keypoints ?? []) {
            const { x, y } = canvasPosition(point);
            circle(x, y, 8);
        }
    }

    if (modelStatus) {
        drawStatus(modelStatus);
    } else if (hands.length === 0) {
        drawStatus("Mão não detetada. Mostra a palma à câmara.");
    } else {
        const openHand = hands.find(
            (hand) => hand.keypoints?.[0] && isHandOpen(hand)
        );

        if (openHand) {
            const wrist = canvasPosition(openHand.keypoints[0]);
            const side = wrist.x < width / 2 ? "zona vermelha" : "zona verde";
            drawStatus(`Mão aberta — ${side}`);
        } else {
            drawStatus("Mão detetada, mas não está aberta.");
        }
    }
}

function canvasPosition(point) {
    // Aplicar aos pontos o mesmo espelho usado no vídeo.
    return {
        x: width - (point.x / video.elt.videoWidth) * width,
        y: (point.y / video.elt.videoHeight) * height
    };
}

function isHandOpen(hand) {
    const points = hand.keypoints3D?.length >= 21
        ? hand.keypoints3D
        : hand.keypoints;

    if (!points || points.length < 21) return false;

    const wrist = points[0];
    let extended = 0;

    for (const finger of FINGERS) {
        const [base, pip, dip, tip] = finger.map((i) => points[i]);

        if (
            jointAngle(base, pip, dip) >= MIN_ANGLE &&
            jointAngle(pip, dip, tip) >= MIN_ANGLE &&
            distance(wrist, tip) > distance(wrist, pip)
        ) {
            extended++;
        }
    }

    return extended >= MIN_FINGERS;
}

function jointAngle(a, b, c) {
    const ux = a.x - b.x;
    const uy = a.y - b.y;
    const uz = (a.z ?? 0) - (b.z ?? 0);

    const vx = c.x - b.x;
    const vy = c.y - b.y;
    const vz = (c.z ?? 0) - (b.z ?? 0);

    const lengths = Math.hypot(ux, uy, uz) * Math.hypot(vx, vy, vz);
    if (!lengths) return 0;

    const cosine = (ux * vx + uy * vy + uz * vz) / lengths;
    return Math.acos(Math.max(-1, Math.min(1, cosine))) * 180 / Math.PI;
}

function distance(a, b) {
    return Math.hypot(
        a.x - b.x,
        a.y - b.y,
        (a.z ?? 0) - (b.z ?? 0)
    );
}

function drawStatus(message) {
    const boxWidth = Math.min(width - 24, 540);

    push();

    noStroke();
    fill(0, 0, 0, 190);
    rect(12, 12, boxWidth, 60, 10);

    fill(255);
    textSize(16);
    textAlign(LEFT, TOP);
    text(message, 24, 24, boxWidth - 24);

    pop();
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}