// AARON-inspired symbolic AI, not Harold Cohen's original AARON system.
// Reactive rules map current spatial perceptions to drawing actions, without planning.
let scribble
let environment
let agent

class ReactiveDrawingAgent {
  perceive(world) {
    const occupied = world.cells.filter(cell => cell.occupied)
    const leftCount = occupied.filter(cell => cell.x < width / 2).length

    return {
      complete: occupied.length >= world.maxForms,
      columns: world.columns,
      leftCount,
      rightCount: occupied.length - leftCount,
      available: world.cells.filter(cell => !cell.occupied).map(cell => ({
        cell,
        neighbors: occupied.filter(other =>
          Math.abs(other.column - cell.column) <= 1 &&
          Math.abs(other.row - cell.row) <= 1
        ).length
      }))
    }
  }

  decide(perception) {
    if (perception.complete || perception.available.length === 0) {
      return { type: 'stop' }
    }

    // Prefer open space and counterbalance the currently more populated half.
    const ranked = perception.available.map(({ cell, neighbors }) => {
      const sideCount = cell.x < width / 2
        ? perception.leftCount
        : perception.rightCount
      return { cell, score: neighbors * 2 + sideCount + random(0, 3) }
    })
    ranked.sort((a, b) => a.score - b.score)
    const cell = ranked[0].cell
    const edge = cell.column === 0 || cell.column === perception.columns - 1
    let motif = 'plant'

    if (!edge && cell.row >= 1 && random() < 0.45) {
      motif = 'figure'
    } else if (cell.row >= 3 && random() < 0.5) {
      motif = 'rock'
    }

    return { type: 'draw', motif, cell }
  }

  act(action) {
    if (action.type === 'stop') {
      noLoop()
      return
    }

    const cell = action.cell
    push()
    translate(cell.x, cell.y)
    scale(0.7 + cell.row * 0.075)
    strokeWeight(1.2)
    noFill()

    if (action.motif === 'plant') {
      this.drawPlant()
    } else if (action.motif === 'figure') {
      this.drawFigure()
    } else {
      this.drawRock()
    }

    pop()
    cell.occupied = true
  }

  drawPlant() {
    stroke('#345343')
    const stemTop = random(-39, -28)
    scribble.scribbleCurve(0, 32, 0, stemTop, -9, 8, 8, -15)

    for (let level = 0; level < 4; level++) {
      const y = 16 - level * 13
      const reach = random(18, 30)
      for (const side of [-1, 1]) {
        const xs = [0, side * reach * 0.5, side * reach, side * reach * 0.55]
        const ys = [y, y - 16, y - 14, y + 1]
        stroke(random(['#59754b', '#928644', '#46766a']))
        scribble.scribbleFilling(xs, ys, 4, side * 35)
        stroke('#345343')
        for (let i = 0; i < xs.length; i++) {
          const next = (i + 1) % xs.length
          scribble.scribbleLine(xs[i], ys[i], xs[next], ys[next])
        }
      }
    }
  }

  drawFigure() {
    const lean = random(-6, 6)
    const xs = [-12, 10, 19, -20]
    const ys = [-16, -16, 20, 20]
    stroke(random(['#bd6549', '#c09442', '#617c91']))
    scribble.scribbleFilling(xs, ys, 3.5, random(25, 65))
    stroke('#38382f')
    scribble.scribbleEllipse(lean, -29, 19, 23)
    scribble.scribbleLine(lean - 4, -18, -12, -16)
    scribble.scribbleLine(lean + 4, -18, 10, -16)
    for (let i = 0; i < xs.length; i++) {
      const next = (i + 1) % xs.length
      scribble.scribbleLine(xs[i], ys[i], xs[next], ys[next])
    }
    scribble.scribbleCurve(-12, -14, -26, 15, -28, -5, -30, 5)
    scribble.scribbleCurve(10, -14, 25, 12, 25, -7, 29, 6)
    scribble.scribbleLine(-9, 20, -12, 40)
    scribble.scribbleLine(9, 20, 14, 40)
    scribble.scribbleLine(-12, 40, -21, 40)
    scribble.scribbleLine(14, 40, 23, 40)
  }

  drawRock() {
    const xs = [-30, -19, 8, 29, 24, -23]
    const ys = [20, 0, -6, 11, 29, 31]
    stroke('#a48d72')
    scribble.scribbleFilling(xs, ys, 4, 25)
    stroke('#5c5547')
    for (let i = 0; i < xs.length; i++) {
      const next = (i + 1) % xs.length
      scribble.scribbleLine(xs[i], ys[i], xs[next], ys[next])
    }
    scribble.scribbleLine(-19, 0, 0, 15)
    scribble.scribbleLine(0, 15, 24, 29)
  }
}

function setup() {
  const canvas = createCanvas(800, 600)
  canvas.attribute('aria-label', 'AARON-inspired drawing of plants, figures, and rocks')
  frameRate(6)
  scribble = new Scribble()
  scribble.bowing = 0.3
  scribble.roughness = 1.1
  scribble.maxOffset = 1.5
  agent = new ReactiveDrawingAgent()
  resetComposition()
}

function resetComposition() {
  background('#f5efdf')
  environment = { columns: 8, rows: 5, maxForms: 26, cells: [] }
  for (let row = 0; row < environment.rows; row++) {
    for (let column = 0; column < environment.columns; column++) {
      environment.cells.push({
        column,
        row,
        x: 64 + column * 96 + random(-7, 7),
        y: 80 + row * 108 + random(-5, 5),
        occupied: false
      })
    }
  }
  loop()
}

function draw() {
  const perception = agent.perceive(environment)
  const action = agent.decide(perception)
  agent.act(action)
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
    saveCanvas('aaron-reactive', 'png')
  }
}
