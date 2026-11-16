// A mouse-aware creative agent that leaves a colorful scribble every two seconds.
let scribble
let agent
let lastDrawTime

const DRAW_INTERVAL = 2000
const SHAPE_MARGIN = 40

class CreativeScribbleAgent {
  constructor() {
    this.memory = { centerWidth: 0.8, centerHeight: 0.8 }
    this.shapes = ['line', 'curve', 'rectangle', 'roundedRectangle', 'ellipse', 'polygon']
  }

  perceive() {
    const areaWidth = width * this.memory.centerWidth
    const areaHeight = height * this.memory.centerHeight
    const left = (width - areaWidth) / 2
    const top = (height - areaHeight) / 2

    return {
      mouseX,
      mouseY,
      left: left + SHAPE_MARGIN,
      right: width - left - SHAPE_MARGIN,
      top: top + SHAPE_MARGIN,
      bottom: height - top - SHAPE_MARGIN
    }
  }

  decide(perception) {
    return {
      shape: random(this.shapes),
      x: constrain(perception.mouseX, perception.left, perception.right),
      y: constrain(perception.mouseY, perception.top, perception.bottom),
      color: color(random(40, 230), random(40, 230), random(40, 230))
    }
  }

  act(action) {
    push()
    stroke(action.color)
    strokeWeight(2)
    noFill()

    if (action.shape === 'line') {
      scribble.scribbleLine(action.x - 32, action.y - 24, action.x + 32, action.y + 24)
    } else if (action.shape === 'curve') {
      scribble.scribbleCurve(
        action.x - 34, action.y + 20,
        action.x + 34, action.y - 20,
        action.x - 24, action.y - 30,
        action.x + 24, action.y + 30
      )
    } else if (action.shape === 'rectangle') {
      scribble.scribbleRect(action.x, action.y, 64, 54)
    } else if (action.shape === 'roundedRectangle') {
      scribble.scribbleRoundedRect(action.x, action.y, 64, 54, 12)
    } else if (action.shape === 'ellipse') {
      scribble.scribbleEllipse(action.x, action.y, 64, 54)
    } else {
      const xCoords = [
        action.x, action.x + 30, action.x + 20,
        action.x - 20, action.x - 30
      ]
      const yCoords = [
        action.y - 34, action.y - 10, action.y + 26,
        action.y + 26, action.y - 10
      ]
      scribble.scribbleFilling(xCoords, yCoords, 5, 30)
      for (let i = 0; i < xCoords.length; i++) {
        const next = (i + 1) % xCoords.length
        scribble.scribbleLine(xCoords[i], yCoords[i], xCoords[next], yCoords[next])
      }
    }

    pop()
  }
}

function setup() {
  createCanvas(800, 600)
  background(250)
  frameRate(30)

  scribble = new Scribble()
  scribble.bowing = 0.1
  scribble.roughness = 1.25
  scribble.maxOffset = 2
  scribble.numEllipseSteps = 2
  agent = new CreativeScribbleAgent()
  lastDrawTime = millis()
}

function draw() {
  if (millis() - lastDrawTime < DRAW_INTERVAL) {
    return
  }

  lastDrawTime = millis()
  const perception = agent.perceive()
  const action = agent.decide(perception)
  agent.act(action)
}
