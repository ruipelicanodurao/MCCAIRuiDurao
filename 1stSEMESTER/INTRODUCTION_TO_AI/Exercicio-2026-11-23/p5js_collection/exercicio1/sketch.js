const palette = {
	background: "#0b1020",
	panel: "#131b2f",
	panelBorder: "#27344d",
	text: "#e8eefc",
	muted: "#8d9bb5",
	cyan: "#53d8fb",
	purple: "#a78bfa",
	green: "#57e39b",
	orange: "#ffb454",
	red: "#ff6b7a",
	blue: "#648cff",
};

const algorithms = {
	sort: { title: "Bubble Sort", description: "Ordenação por comparação", color: palette.cyan },
	bfs: { title: "Busca em largura (BFS)", description: "Percorre o grafo nível a nível", color: palette.blue },
	dfs: { title: "Busca em profundidade (DFS)", description: "Explora um caminho até ao fim", color: palette.purple },
	ucs: { title: "Custo uniforme (UCS)", description: "Escolhe sempre o caminho de menor custo", color: palette.orange },
};
const speedOptions = [
	{ label: "0.5x", sortDelay: 14, searchDelay: 72 },
	{ label: "1x", sortDelay: 7, searchDelay: 36 },
	{ label: "2x", sortDelay: 4, searchDelay: 18 },
	{ label: "4x", sortDelay: 2, searchDelay: 9 },
];

const initialValues = 24;
const graphPositions = [
	{ x: 0.10, y: 0.48, links: [1, 2] },
	{ x: 0.30, y: 0.18, links: [0, 3, 4] },
	{ x: 0.30, y: 0.78, links: [0, 4] },
	{ x: 0.56, y: 0.18, links: [1, 5] },
	{ x: 0.56, y: 0.78, links: [1, 2, 5] },
	{ x: 0.82, y: 0.48, links: [3, 4] },
];
const graphExamples = [
	[[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [3, 5], [4, 5]],
	[[0, 1], [0, 3], [1, 2], [1, 4], [2, 5], [3, 4], [4, 5]],
	[[0, 2], [0, 3], [1, 2], [1, 4], [2, 3], [3, 5], [4, 5]],
	[[0, 1], [1, 2], [1, 3], [2, 4], [3, 4], [3, 5], [4, 5]],
];

let selectedAlgorithm = null;
let values = [];
let lastSortExample = "";
let sortRunning = false;
let sortDone = false;
let sortI = 0;
let sortJ = 0;
let comparisons = 0;
let swaps = 0;
let sortExplanation = "Carrega em Iniciar para começar a comparar valores adjacentes.";
let graph = graphPositions.map((node) => ({ x: node.x, y: node.y, links: [] }));
let edgeCosts = {};
let lastGraphExample = -1;
let exampleNumber = 0;
let search = null;
let lastStep = 0;
let controls = {};
let speedIndices = { sort: 1, bfs: 1, dfs: 1, ucs: 1 };

function setup() {
	createCanvas(windowWidth, max(windowHeight, 1060));
	textFont("Arial");
}

function draw() {
	drawBackdrop();
	controls = {};
	if (selectedAlgorithm === null) {
		drawMenu();
		return;
	}

	const panelTop = drawHeader();
	const panel = { x: 24, y: panelTop, w: width - 48, h: height - panelTop - 24 };
	if (selectedAlgorithm === "sort") {
		drawSortPanel(panel);
	} else {
		drawSearchPanel(panel);
	}
	updateAlgorithm();
}

function drawBackdrop() {
	const bands = 24;
	for (let i = 0; i < bands; i++) {
		noStroke();
		fill(lerpColor(color("#080b17"), color("#111b31"), i / bands));
		rect(0, (height / bands) * i, width, height / bands + 1);
	}
	noFill();
	stroke("#1c2a43");
	strokeWeight(1);
	for (let i = 0; i < 7; i++) {
		const x = width * (0.12 + i * 0.14);
		const y = 130 + (i % 3) * 70;
		circle(x, y, 4);
	}
}

function drawMenu() {
	noStroke();
	fill(palette.cyan);
	textAlign(LEFT, BASELINE);
	textStyle(BOLD);
	textSize(11);
	text("LABORATÓRIO INTERATIVO  /  INTELIGÊNCIA ARTIFICIAL", 30, 34);
	fill(palette.text);
	textFont("Georgia");
	textSize(34);
	text("Explora os algoritmos", 30, 78);
	textFont("Arial");
	fill(palette.muted);
	textStyle(NORMAL);
	textSize(14);
	text("Escolhe uma visualização. Cada nova execução cria um exemplo diferente.", 30, 106);

	const margin = 28;
	const gap = 16;
	const columns = width >= 1000 ? 4 : width >= 560 ? 2 : 1;
	const cardWidth = (width - margin * 2 - gap * (columns - 1)) / columns;
	const cardHeight = width < 560 ? 158 : 190;
	const cardGapY = 16;
	const top = 150;
	const choices = [
		{ id: "sort", number: "01", name: "Bubble Sort", detail: "Ordena valores comparando elementos adjacentes.", note: "Ordenação", color: palette.cyan },
		{ id: "bfs", number: "02", name: "BFS • largura", detail: "Visita os nós por níveis, usando uma fila.", note: "Busca em largura", color: palette.blue },
		{ id: "dfs", number: "03", name: "DFS • profundidade", detail: "Segue um ramo do grafo antes de voltar atrás.", note: "Busca em profundidade", color: palette.purple },
		{ id: "ucs", number: "04", name: "UCS • custo uniforme", detail: "Expande o nó com menor custo acumulado.", note: "Caminho de menor custo", color: palette.orange },
	];

	choices.forEach((choice, index) => {
		const col = index % columns;
		const row = floor(index / columns);
		const x = margin + col * (cardWidth + gap);
		const y = top + row * (cardHeight + cardGapY);
		controls[`menu_${choice.id}`] = { x, y, w: cardWidth, h: cardHeight };
		const hovered = mouseX >= x && mouseX <= x + cardWidth && mouseY >= y && mouseY <= y + cardHeight;
		noStroke();
		fill(hovered ? "#1b2942" : palette.panel);
		rect(x, y, cardWidth, cardHeight, 18);
		noFill();
		stroke(hovered ? choice.color : palette.panelBorder);
		strokeWeight(hovered ? 2 : 1);
		rect(x, y, cardWidth, cardHeight, 18);
		noStroke();
		fill(choice.color);
		rect(x + 16, y + 16, 3, cardHeight - 32, 2);

		fill(choice.color);
		textAlign(LEFT, BASELINE);
		textStyle(BOLD);
		textSize(11);
		text(choice.number, x + 20, y + 30);
		fill(palette.text);
		textFont("Georgia");
		textSize(width < 560 ? 20 : 22);
		text(choice.name, x + 20, y + 65, cardWidth - 40, 30);
		textFont("Arial");
		fill(palette.muted);
		textStyle(NORMAL);
		textSize(13);
		text(choice.detail, x + 20, y + 96, cardWidth - 40, 42);
		fill(choice.color);
		textStyle(BOLD);
		textSize(11);
		text(choice.note.toUpperCase(), x + 20, y + cardHeight - 20);
	});

	noCursorIfHoveringMenu();
}

function noCursorIfHoveringMenu() {
	const hovering = Object.values(controls).some((item) =>
		mouseX >= item.x && mouseX <= item.x + item.w && mouseY >= item.y && mouseY <= item.y + item.h
	);
	cursor(hovering ? HAND : ARROW);
}

function drawHeader() {
	const info = algorithms[selectedAlgorithm];
	cursor(ARROW);
	noStroke();
	fill(info.color);
	textAlign(LEFT, BASELINE);
	textStyle(BOLD);
	textSize(12);
	text("VISUALIZAÇÃO DE ALGORITMOS", 28, 30);
	fill(palette.text);
	textFont("Georgia");
	textSize(width < 520 ? 20 : 26);
	text(info.title, 28, 62);
	textFont("Arial");
	fill(palette.muted);
	textStyle(NORMAL);
	textSize(13);
	text(`Exemplo ${exampleNumber}  •  ${info.description}`, 28, 86);

	const compact = width < 520;
	drawButton("back", compact ? 28 : width - 118, compact ? 102 : 26, 90, 34, "← Menu", palette.muted, false);
	return compact ? 150 : 112;
}

function drawSortPanel(panel) {
	drawPanel(panel);
	drawPanelHeading(panel, "Ordenação por comparação");
	const compact = panel.w < 520;
	const buttonY = compact ? panel.y + 92 : panel.y + 24;
	const buttonX = compact ? panel.x + 24 : panel.x + panel.w - 302;
	const toggleWidth = compact ? 68 : 82;
	const speedWidth = compact ? 88 : 112;
	const resetWidth = compact ? 68 : 68;
	const gap = compact ? 6 : 8;
	drawButton("toggle", buttonX, buttonY, toggleWidth, 34,
		sortRunning ? "Pausar" : sortDone ? "Repetir" : "Iniciar", palette.cyan, true);
	const speedX = buttonX + toggleWidth + gap;
	drawButton("speed", speedX, buttonY, speedWidth, 34,
		`Vel.: ${speedOptions[speedIndices.sort].label}`, palette.cyan, false);
	drawButton("reset", speedX + speedWidth + gap, buttonY, resetWidth, 34, "Baralhar", palette.muted, false);

	const labelY = panel.y + (compact ? 145 : 92);
	drawMetric(panel.x + 24, labelY, "COMPARAÇÕES", comparisons, palette.cyan);
	drawMetric(panel.x + 175, labelY, "TROCAS", swaps, palette.orange);
	const chart = {
		x: panel.x + 24,
		y: panel.y + (compact ? 202 : 155),
		w: panel.w - 48,
		h: panel.h - (compact ? 370 : 325),
	};
	const slotWidth = chart.w / values.length;
	const barWidth = max(3, slotWidth * 0.68);
	const maxBarHeight = chart.h - 28;
	stroke(palette.panelBorder);
	strokeWeight(1);
	line(chart.x, chart.y + chart.h, chart.x + chart.w, chart.y + chart.h);

	for (let i = 0; i < values.length; i++) {
		const barHeight = (values[i] / values.length) * maxBarHeight;
		const x = chart.x + i * slotWidth + (slotWidth - barWidth) / 2;
		const y = chart.y + chart.h - barHeight;
		let barColor = palette.blue;
		if (sortDone || i >= values.length - sortI) barColor = palette.green;
		if (sortRunning && (i === sortJ || i === sortJ + 1)) barColor = palette.orange;
		noStroke();
		fill(barColor);
		rect(x, y, barWidth, barHeight, 4, 4, 0, 0);
		if (slotWidth >= 22) {
			fill(palette.text);
			textAlign(CENTER, BOTTOM);
			textSize(10);
			text(values[i], x + barWidth / 2, y - 4);
		}
	}

	drawExplanation(panel.x + 24, panel.y + panel.h - 130, panel.w - 48, 82,
		sortExplanation, palette.cyan);
	fill(palette.muted);
	textAlign(LEFT, BASELINE);
	textSize(12);
	text(sortDone ? "Ordenação concluída" : sortRunning ? "A comparar os elementos destacados" : "Pronto para ordenar",
		panel.x + 24, panel.y + panel.h - 24);
}

function drawSearchPanel(panel) {
	drawPanel(panel);
	drawPanelHeading(panel, selectedAlgorithm === "ucs" ? "Grafo ponderado • objetivo: nó F" : "Grafo não direcionado • início: nó A");
	const compact = panel.w < 520;
	const buttonY = compact ? panel.y + 92 : panel.y + 24;
	const buttonX = compact ? panel.x + 24 : panel.x + panel.w - 302;
	const toggleWidth = compact ? 68 : 82;
	const speedWidth = compact ? 88 : 112;
	const resetWidth = 68;
	const gap = compact ? 6 : 8;
	drawButton("toggle", buttonX, buttonY, toggleWidth, 34,
		search.running ? "Pausar" : search.done ? "Repetir" : "Iniciar", algorithms[selectedAlgorithm].color, true);
	const speedX = buttonX + toggleWidth + gap;
	drawButton("speed", speedX, buttonY, speedWidth, 34,
		`Vel.: ${speedOptions[speedIndices[selectedAlgorithm]].label}`, algorithms[selectedAlgorithm].color, false);
	drawButton("reset", speedX + speedWidth + gap, buttonY, resetWidth, 34, "Reiniciar", palette.muted, false);

	const graphArea = {
		x: panel.x + 70,
		y: panel.y + (compact ? 158 : 116),
		w: panel.w - 140,
		h: max(140, panel.h - (compact ? 430 : 390)),
	};
	const nodePositions = graph.map((node) => ({
		x: graphArea.x + node.x * graphArea.w,
		y: graphArea.y + node.y * graphArea.h,
	}));
	drawGraphEdges(nodePositions);
	drawGraphNodes(nodePositions);

	const infoY = panel.y + panel.h - 176;
	drawExplanation(panel.x + 24, infoY - 104, panel.w - 48, 86,
		search.explanation, algorithms[selectedAlgorithm].color);
	drawFrontier(panel.x + 24, infoY + 27, panel.w - 48);
	fill(palette.muted);
	textAlign(LEFT, BASELINE);
	textStyle(BOLD);
	textSize(10);
	text("ORDEM DE VISITA", panel.x + 24, infoY + 74);
	fill(palette.text);
	textStyle(NORMAL);
	textSize(13);
	const order = search.order.map(nodeName).join(" → ") || "—";
	text(order, panel.x + 24, infoY + 95, panel.w - 48, 22);

	if (selectedAlgorithm === "ucs") {
		const path = search.path.length ? search.path.map(nodeName).join(" → ") : "—";
		fill(palette.muted);
		textStyle(BOLD);
		textSize(10);
		text("CAMINHO DE MENOR CUSTO", panel.x + 24, infoY + 122);
		fill(palette.orange);
		textStyle(NORMAL);
		textSize(13);
		const totalCost = search.distances[5] === Infinity ? "—" : search.distances[5];
		text(`${path}   •   custo: ${totalCost}`, panel.x + 210, infoY + 122, panel.w - 234, 20);
	}

	fill(palette.muted);
	textStyle(NORMAL);
	textSize(12);
	const status = search.done
		? selectedAlgorithm === "ucs" ? "Destino alcançado com custo mínimo" : "Busca concluída"
		: search.running ? `A explorar o nó ${nodeName(search.current)}` : "Pronto para iniciar";
	text(status, panel.x + 24, panel.y + panel.h - 24);
}

function drawGraphEdges(nodePositions) {
	stroke(palette.panelBorder);
	strokeWeight(3);
	for (let i = 0; i < graph.length; i++) {
		for (const neighbor of graph[i].links) {
			if (neighbor > i) {
				const start = nodePositions[i];
				const end = nodePositions[neighbor];
				const onBestPath = selectedAlgorithm === "ucs"
					&& search.path.includes(i) && search.path.includes(neighbor)
					&& abs(search.path.indexOf(i) - search.path.indexOf(neighbor)) === 1;
				stroke(onBestPath ? palette.green : palette.panelBorder);
				strokeWeight(onBestPath ? 5 : 3);
				line(start.x, start.y, end.x, end.y);
				if (selectedAlgorithm === "ucs") {
					const cost = edgeCost(i, neighbor);
					noStroke();
					fill(palette.background);
					circle((start.x + end.x) / 2, (start.y + end.y) / 2, 24);
					fill(palette.orange);
					textAlign(CENTER, CENTER);
					textStyle(BOLD);
					textSize(11);
					text(cost, (start.x + end.x) / 2, (start.y + end.y) / 2);
				}
			}
		}
	}
}

function drawGraphNodes(nodePositions) {
	const frontier = frontierNodes();
	for (let i = 0; i < graph.length; i++) {
		const node = nodePositions[i];
		let nodeColor = palette.panel;
		if (search.explored.has(i)) nodeColor = palette.green;
		if (frontier.has(i)) nodeColor = palette.orange;
		if (search.current === i && search.running) nodeColor = palette.purple;
		stroke(search.explored.has(i) ? palette.green : palette.panelBorder);
		strokeWeight(2);
		fill(nodeColor);
		circle(node.x, node.y, 44);
		noStroke();
		fill(search.explored.has(i) || frontier.has(i) || (search.current === i && search.running) ? palette.background : palette.text);
		textAlign(CENTER, CENTER);
		textStyle(BOLD);
		textSize(15);
		text(nodeName(i), node.x, node.y);

		if (selectedAlgorithm === "ucs" && search.distances[i] !== Infinity) {
			fill(palette.orange);
			textStyle(BOLD);
			textSize(11);
			text(`g=${search.distances[i]}`, node.x, node.y + 34);
		}
	}
}

function drawFrontier(x, y, availableWidth) {
	const title = selectedAlgorithm === "bfs" ? "FILA (PRÓXIMOS NÓS)"
		: selectedAlgorithm === "dfs" ? "PILHA (PRÓXIMOS NÓS)" : "FRONTEIRA (NÓ: CUSTO)";
	fill(palette.muted);
	textAlign(LEFT, BASELINE);
	textStyle(BOLD);
	textSize(10);
	text(title, x, y);
	let items;
	if (selectedAlgorithm === "ucs") {
		items = search.frontier.slice().sort((a, b) => a.cost - b.cost)
			.map((item) => `${nodeName(item.node)}:${item.cost}`);
	} else {
		items = search.frontier.map(nodeName);
	}
	fill(palette.orange);
	textStyle(NORMAL);
	textSize(13);
	text(items.length ? items.join("  ·  ") : "vazia", x, y + 20, availableWidth, 20);
}

function drawPanel(panel) {
	noStroke();
	fill(palette.panel);
	rect(panel.x, panel.y, panel.w, panel.h, 18);
	noFill();
	stroke(palette.panelBorder);
	strokeWeight(1);
	rect(panel.x, panel.y, panel.w, panel.h, 18);
	noStroke();
	fill(algorithms[selectedAlgorithm].color);
	rect(panel.x + 20, panel.y, 72, 3, 0, 0, 3, 3);
}

function drawExplanation(x, y, w, h, message, accent) {
	noStroke();
	fill("#0e1728");
	rect(x, y, w, h, 12);
	fill(accent);
	rect(x, y + 10, 3, h - 20, 2);
	fill(accent);
	textAlign(LEFT, BASELINE);
	textStyle(BOLD);
	textSize(9);
	text("PASSO ATUAL", x + 14, y + 18);
	fill(palette.text);
	textStyle(NORMAL);
	textSize(12);
	text(message, x + 14, y + 39, w - 28, h - 42);
}

function drawPanelHeading(panel, subtitle) {
	noStroke();
	fill(palette.text);
	textAlign(LEFT, BASELINE);
	textStyle(BOLD);
	textSize(17);
	text(algorithms[selectedAlgorithm].title, panel.x + 24, panel.y + 34);
	fill(palette.muted);
	textStyle(NORMAL);
	textSize(12);
	text(subtitle, panel.x + 24, panel.y + 57);
}

function drawMetric(x, y, label, value, color) {
	fill(palette.muted);
	textAlign(LEFT, BASELINE);
	textStyle(BOLD);
	textSize(10);
	text(label, x, y);
	fill(color);
	textSize(17);
	text(String(value), x, y + 23);
	textStyle(NORMAL);
}

function drawButton(name, x, y, w, h, label, color, filled) {
	controls[name] = { x, y, w, h };
	noStroke();
	fill(filled ? color : palette.panel);
	rect(x, y, w, h, 9);
	if (!filled) {
		noFill();
		stroke(color);
		strokeWeight(1);
		rect(x, y, w, h, 9);
	}
	noStroke();
	fill(filled ? palette.background : palette.text);
	textAlign(CENTER, CENTER);
	textStyle(BOLD);
	textSize(11);
	text(label, x + w / 2, y + h / 2 + 1);
	textStyle(NORMAL);
}

function updateAlgorithm() {
	const speed = speedOptions[speedIndices[selectedAlgorithm]];
	if (selectedAlgorithm === "sort" && sortRunning && frameCount - lastStep >= speed.sortDelay) {
		lastStep = frameCount;
		stepSort();
	} else if (selectedAlgorithm !== "sort" && search && search.running && frameCount - lastStep >= speed.searchDelay) {
		lastStep = frameCount;
		stepSearch();
	}
}

function stepSort() {
	if (sortI >= values.length - 1) {
		sortRunning = false;
		sortDone = true;
		sortExplanation = "Todos os elementos estão ordenados.";
		return;
	}
	if (sortJ < values.length - sortI - 1) {
		comparisons++;
		const left = values[sortJ];
		const right = values[sortJ + 1];
		if (values[sortJ] > values[sortJ + 1]) {
			[values[sortJ], values[sortJ + 1]] = [values[sortJ + 1], values[sortJ]];
			swaps++;
			sortExplanation = `${left} é maior do que ${right}; troco os dois valores adjacentes.`;
		} else {
			sortExplanation = `${left} é menor do que ${right}; mantenho esta ordem e avanço.`;
		}
		sortJ++;
	} else {
		sortI++;
		sortJ = 0;
		sortExplanation = `Passagem ${sortI} concluída; o maior valor restante ficou na sua posição final.`;
		if (sortI >= values.length - 1) {
			sortRunning = false;
			sortDone = true;
			sortExplanation = "Todos os elementos estão ordenados.";
		}
	}
}

function createSearchState(type) {
	return {
		type,
		frontier: type === "ucs" ? [{ node: 0, cost: 0 }] : [0],
		discovered: new Set([0]),
		explored: new Set(),
		order: [],
		current: -1,
		running: false,
		done: false,
		distances: Array(graph.length).fill(Infinity).map((value, index) => index === 0 ? 0 : value),
		parents: Array(graph.length).fill(-1),
		path: [],
		explanation: type === "ucs"
			? "A fronteira começa com A a custo 0. Será escolhido sempre o menor custo acumulado."
			: type === "dfs"
				? "A pilha começa com A. O último nó adicionado será explorado primeiro."
				: "A fila começa com A. Os nós serão explorados pela ordem em que entram.",
	};
}

function stepSearch() {
	if (!search.frontier.length) {
		search.running = false;
		search.done = true;
		return;
	}

	if (selectedAlgorithm === "ucs") {
		search.frontier.sort((a, b) => a.cost - b.cost);
		const candidate = search.frontier.shift();
		if (search.explored.has(candidate.node) || candidate.cost !== search.distances[candidate.node]) {
			search.explanation = `${nodeName(candidate.node)} tinha um custo antigo na fronteira; ignoro esta entrada.`;
			return;
		}
		search.current = candidate.node;
		search.explored.add(candidate.node);
		search.order.push(candidate.node);
		if (candidate.node === graph.length - 1) {
			search.path = buildPath(candidate.node);
			search.running = false;
			search.done = true;
			search.explanation = `Cheguei a F com custo ${candidate.cost}. O caminho apresentado tem custo mínimo.`;
			return;
		}
		const updated = [];
		for (const neighbor of graph[candidate.node].links) {
			if (search.explored.has(neighbor)) continue;
			const newCost = search.distances[candidate.node] + edgeCost(candidate.node, neighbor);
			if (newCost < search.distances[neighbor]) {
				search.distances[neighbor] = newCost;
				search.parents[neighbor] = candidate.node;
				search.frontier.push({ node: neighbor, cost: newCost });
				updated.push(`${nodeName(neighbor)}=${newCost}`);
			}
		}
		search.explanation = updated.length
			? `Escolho ${nodeName(candidate.node)} (custo ${candidate.cost}) e atualizo: ${updated.join(", ")}.`
			: `Escolho ${nodeName(candidate.node)} (custo ${candidate.cost}); não há custos melhores nos vizinhos.`;
		return;
	}

	const current = selectedAlgorithm === "bfs" ? search.frontier.shift() : search.frontier.pop();
	search.current = current;
	search.explored.add(current);
	search.order.push(current);
	const neighbors = selectedAlgorithm === "dfs"
		? graph[current].links.slice().reverse()
		: graph[current].links;
	const added = [];
	for (const neighbor of neighbors) {
		if (!search.discovered.has(neighbor)) {
			search.discovered.add(neighbor);
			search.frontier.push(neighbor);
			added.push(nodeName(neighbor));
		}
	}
	if (selectedAlgorithm === "dfs") {
		search.explanation = `Retiro ${nodeName(current)} da pilha${added.length ? `; adiciono ${added.join(", ")}.` : "; não há vizinhos novos."}`;
	} else {
		search.explanation = `Retiro ${nodeName(current)} da fila${added.length ? `; junto ${added.join(", ")} ao fim da fila.` : "; não há vizinhos novos."}`;
	}
	if (!search.frontier.length) {
		search.running = false;
		search.done = true;
		search.explanation += " A busca terminou.";
	}
}

function startSelectedAlgorithm() {
	if (selectedAlgorithm === "sort") {
		if (sortDone) startNewExample("sort");
		sortRunning = !sortRunning;
	} else {
		if (search.done) startNewExample(selectedAlgorithm);
		search.running = !search.running;
	}
	lastStep = frameCount;
}

function startNewExample(type) {
	exampleNumber++;
	if (type === "sort") {
		resetSort();
		return;
	}

	let exampleIndex = floor(random(graphExamples.length));
	if (exampleIndex === lastGraphExample) {
		exampleIndex = (exampleIndex + 1 + floor(random(graphExamples.length - 1))) % graphExamples.length;
	}
	lastGraphExample = exampleIndex;
	graph = graphPositions.map((node) => ({ x: node.x, y: node.y, links: [] }));
	edgeCosts = {};
	for (const [a, b] of graphExamples[exampleIndex]) {
		graph[a].links.push(b);
		graph[b].links.push(a);
		edgeCosts[`${a}-${b}`] = floor(random(1, 10));
	}
	search = createSearchState(type);
}

function resetSort() {
	values = Array.from({ length: initialValues }, (_, index) => index + 1);
	for (let i = values.length - 1; i > 0; i--) {
		const j = floor(random(i + 1));
		[values[i], values[j]] = [values[j], values[i]];
	}
	if (values.join(",") === lastSortExample) values.push(values.shift());
	lastSortExample = values.join(",");
	sortRunning = false;
	sortDone = false;
	sortI = 0;
	sortJ = 0;
	comparisons = 0;
	swaps = 0;
	sortExplanation = "Carrega em Iniciar para começar a comparar valores adjacentes.";
}

function nodeName(node) {
	return String.fromCharCode(65 + node);
}

function edgeCost(a, b) {
	return edgeCosts[`${min(a, b)}-${max(a, b)}`];
}

function buildPath(node) {
	const path = [];
	for (let current = node; current !== -1; current = search.parents[current]) {
		path.unshift(current);
	}
	return path;
}

function frontierNodes() {
	return new Set(search.frontier.map((item) => selectedAlgorithm === "ucs" ? item.node : item));
}

function mousePressed() {
	for (const [name, button] of Object.entries(controls)) {
		if (mouseX < button.x || mouseX > button.x + button.w || mouseY < button.y || mouseY > button.y + button.h) continue;

		if (name.startsWith("menu_")) {
			selectedAlgorithm = name.slice(5);
			startNewExample(selectedAlgorithm);
		} else if (name === "back") {
			selectedAlgorithm = null;
			sortRunning = false;
			if (search) search.running = false;
		} else if (name === "toggle") {
			startSelectedAlgorithm();
		} else if (name === "reset") {
			startNewExample(selectedAlgorithm);
		} else if (name === "speed") {
			speedIndices[selectedAlgorithm] = (speedIndices[selectedAlgorithm] + 1) % speedOptions.length;
		}
		return false;
	}
	return false;
}

function keyPressed() {
	if (key === "Escape") {
		selectedAlgorithm = null;
		sortRunning = false;
		if (search) search.running = false;
	} else if (key === " " && selectedAlgorithm !== null) {
		startSelectedAlgorithm();
	} else if ((key === "r" || key === "R") && selectedAlgorithm !== null) {
		startNewExample(selectedAlgorithm);
	}
}

function windowResized() {
	resizeCanvas(windowWidth, max(windowHeight, 1060));
}
