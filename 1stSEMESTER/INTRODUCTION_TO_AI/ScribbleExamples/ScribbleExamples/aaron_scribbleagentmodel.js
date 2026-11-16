// AARON-inspired cooperative symbolic AI, not Cohen's original system or a trained model.
// Shared model: placed forms, occupied cells, motif counts, and colour usage.
let scribble
let model
let composer
let shaper
let colourist

class ComposerAgent {
  perceive(world) {
    return {
      complete: world.forms.length >= world.maxForms,
      available: world.cells.filter(cell => !cell.occupied),
      forms: world.forms
    }
  }

  decide(perception) {
    if (perception.complete || perception.available.length === 0) {
      return { type: 'stop' }
    }

    const ranked = perception.available.map(cell => {
      const neighbors = perception.forms.filter(form =>
        Math.hypot(form.cell.x - cell.x, form.cell.y - cell.y) < 150
      ).length
      const sameSide = perception.forms.filter(form =>
        (form.cell.x < width / 2) === (cell.x < width / 2)
      ).length
      return { cell, score: neighbors * 2 + sameSide + random(0, 2) }
    })
    ranked.sort((a, b) => a.score - b.score)
    return {
      type: 'place',
      cell: ranked[0].cell,
      angle: random(-Math.PI / 5, Math.PI / 5)
    }
  }

  act(placement, form, world) {
    if (placement.type === 'stop') {
      noLoop()
      return
    }
    placement.cell.occupied = true
    world.forms.push(form)
  }
}

class ShaperAgent {
  constructor() {
    this.motifs = ['plant', 'figure', 'rock', 'flower', 'bird', 'tree', 'vase']
  }

  perceive(placement, world) {
    return {
      cell: placement.cell,
      angle: placement.angle,
      counts: Object.fromEntries(this.motifs.map(motif => [
        motif, world.forms.filter(form => form.motif === motif).length
      ]))
    }
  }

  decide(perception) {
    const { cell, counts } = perception
    const candidates = this.motifs.map(motif => {
      let score = counts[motif] + random(0, 2)
      if (motif === 'plant' && (cell.column === 0 || cell.column === 5)) score -= 2
      if (motif === 'figure' && cell.column > 0 && cell.column < 5) score -= 1
      if (motif === 'rock' && cell.row < 2) score += 5
      return { motif, score }
    })
    candidates.sort((a, b) => a.score - b.score)
    const motif = candidates[0].motif
    const parts = []
    const lines = []

    if (motif === 'plant') {
      lines.push([0, 40, 0, -42])
      for (let level = 0; level < 4; level++) {
        const y = 22 - level * 17
        const reach = random(24, 35)
        for (const side of [-1, 1]) {
          parts.push({
            xs: [0, side * reach * 0.45, side * reach, side * reach * 0.55],
            ys: [y, y - 20, y - 16, y + 2]
          })
        }
      }
    } else if (motif === 'figure') {
      const lean = random(-5, 5)
      parts.push({ ellipse: [lean, -34, 23, 26] })
      parts.push({ xs: [-14, 12, 21, -22], ys: [-18, -18, 23, 23] })
      lines.push(
        [lean - 4, -21, -14, -18], [lean + 4, -21, 12, -18],
        [-14, -16, -32, 12], [12, -16, 31, 12],
        [-10, 23, -14, 46], [10, 23, 15, 46],
        [-14, 46, -24, 46], [15, 46, 25, 46]
      )
    } else if (motif === 'rock') {
      parts.push({ xs: [-36, -22, 10, 35, 29, -28], ys: [17, -9, -17, 7, 33, 35] })
      lines.push([-22, -9, 0, 11], [0, 11, 29, 33])
    } else if (motif === 'flower') {
      const petals = Math.floor(random(5, 9))
      const radius = random(13, 18)
      lines.push([0, -10, 0, 44])
      parts.push({ xs: [0, -23, -15], ys: [24, 8, 29] })
      parts.push({ xs: [0, 23, 16], ys: [32, 16, 36] })
      for (let i = 0; i < petals; i++) {
        const angle = i * Math.PI * 2 / petals
        parts.push({ ellipse: [
          Math.cos(angle) * radius, -18 + Math.sin(angle) * radius, 17, 20
        ] })
      }
      parts.push({ ellipse: [0, -18, 15, 15] })
    } else if (motif === 'bird') {
      const beak = random(36, 43)
      parts.push({ xs: [-22, -43, -35], ys: [9, -8, 20] })
      parts.push({ ellipse: [-5, 6, 48, 30] })
      parts.push({ xs: [-22, 11, -4], ys: [0, 3, 17] })
      parts.push({ ellipse: [20, -12, 22, 23] })
      parts.push({ xs: [30, beak, 30], ys: [-15, -8, -5] })
      lines.push([22, -15, 24, -15], [-10, 21, -14, 37],
        [5, 21, 9, 37], [-14, 37, -5, 37], [9, 37, 18, 37])
    } else if (motif === 'tree') {
      const crown = random(42, 54)
      parts.push({ xs: [-8, 7, 11, -12], ys: [-8, -8, 45, 45] })
      parts.push({ ellipse: [-18, -15, crown, 38] })
      parts.push({ ellipse: [17, -16, crown, 38] })
      parts.push({ ellipse: [0, -32, 40, 35] })
      lines.push([0, 28, -2, -16], [-2, 4, -19, -10], [-2, 9, 18, -11])
    } else if (motif === 'vase') {
      const belly = random(25, 34)
      parts.push({
        xs: [-16, 16, 12, belly, 23, -23, -belly, -12],
        ys: [-35, -35, -15, 12, 39, 39, 12, -15]
      })
      lines.push([-16, -29, 16, -29], [-23, 18, 23, 18],
        [-21, 25, 21, 25], [-19, 32, 19, 32])
    }

    return {
      cell,
      motif,
      parts,
      lines,
      angle: perception.angle,
      size: (0.75 + cell.row * 0.08) * random(0.8, 1.25)
    }
  }

  act(form) {
    stroke('#383b32')
    strokeWeight(1.3)
    noFill()
    for (const part of form.parts) {
      if (part.ellipse) {
        scribble.scribbleEllipse(...part.ellipse)
      } else {
        for (let i = 0; i < part.xs.length; i++) {
          const next = (i + 1) % part.xs.length
          scribble.scribbleLine(part.xs[i], part.ys[i], part.xs[next], part.ys[next])
        }
      }
    }
    for (const line of form.lines) scribble.scribbleLine(...line)
  }
}

class ColouristAgent {
  constructor() {
    this.palette = [
      { ink: '#b96048', family: 'warm' },
      { ink: '#bc9140', family: 'warm' },
      { ink: '#55754e', family: 'cool' },
      { ink: '#487b80', family: 'cool' },
      { ink: '#7c6484', family: 'cool' }
    ]
  }

  perceive(form, world) {
    return {
      motif: form.motif,
      usage: this.palette.map((colour, index) =>
        world.forms.filter(other => other.colourIndex === index).length
      ),
      nearbyColours: world.forms.filter(other =>
        Math.hypot(other.cell.x - form.cell.x, other.cell.y - form.cell.y) < 150
      ).map(other => other.colourIndex)
    }
  }

  decide(perception) {
    const ranked = this.palette.map((colour, index) => {
      let score = perception.usage[index] + random(0, 1.5)
      if (perception.nearbyColours.includes(index)) score += 3
      if (['plant', 'tree'].includes(perception.motif) && colour.family === 'warm') score += 2
      if (['figure', 'flower', 'vase'].includes(perception.motif) && colour.family === 'cool') score += 1
      return { index, score }
    })
    ranked.sort((a, b) => a.score - b.score)
    return { index: ranked[0].index, gap: random(3, 5), angle: random(25, 65) }
  }

  act(style, form) {
    stroke(this.palette[style.index].ink)
    strokeWeight(1)
    for (const part of form.parts) {
      let xs = part.xs
      let ys = part.ys
      if (part.ellipse) {
        // Scribble fills polygons; sample an ellipse for its hatching boundary.
        const [x, y, w, h] = part.ellipse
        xs = []
        ys = []
        for (let i = 0; i < 20; i++) {
          const angle = i * Math.PI * 2 / 20
          xs.push(x + Math.cos(angle) * w / 2)
          ys.push(y + Math.sin(angle) * h / 2)
        }
      }
      scribble.scribbleFilling(xs, ys, style.gap, style.angle)
    }
    form.colourIndex = style.index
  }
}

function setup() {
  const canvas = createCanvas(800, 600)
  canvas.attribute('aria-label', 'AARON-inspired composition by composer, shaper, and colourist agents')
  frameRate(4)
  scribble = new Scribble()
  scribble.bowing = 0.3
  scribble.roughness = 1.1
  scribble.maxOffset = 1.5
  composer = new ComposerAgent()
  shaper = new ShaperAgent()
  colourist = new ColouristAgent()
  resetComposition()
}

function resetComposition() {
  background('#f5efdf')
  model = { forms: [], cells: [], maxForms: 20 }
  for (let row = 0; row < 4; row++) {
    for (let column = 0; column < 6; column++) {
      model.cells.push({
        column,
        row,
        // Keep a margin for the largest rotated form, including scribble offsets.
        x: constrain(80 + column * 128 + random(-46, 46), 82, width - 82),
        y: constrain(80 + row * 140 + random(-42, 42), 82, height - 82),
        occupied: false
      })
    }
  }
  loop()
}

function draw() {
  const placement = composer.decide(composer.perceive(model))
  if (placement.type === 'stop') {
    composer.act(placement, null, model)
    return
  }

  const form = shaper.decide(shaper.perceive(placement, model))
  const style = colourist.decide(colourist.perceive(form, model))
  push()
  translate(form.cell.x, form.cell.y)
  rotate(form.angle)
  scale(form.size)
  colourist.act(style, form)
  shaper.act(form)
  pop()
  composer.act(placement, form, model)
}

function keyPressed() {
  if (key === 'r' || key === 'R') {
    resetComposition()
  } else if (key === ' ') {
    if (isLooping()) {
      noLoop()
    } else {
      loop()
    }
    return false
  } else if (key === 's' || key === 'S') {
    saveCanvas('aaron-multiagent', 'png')
  }
}
