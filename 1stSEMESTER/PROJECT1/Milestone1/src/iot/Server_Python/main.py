from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory "database"
items = {
    1: {"id": 1, "name": "Router", "qty": 2},
    2: {"id": 2, "name": "Switch", "qty": 5},
}
next_id = 3


@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(err):
    return jsonify(error=err.name, message=err.description), err.code


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/items")
def list_items():
    return jsonify(list(items.values()))


@app.get("/api/items/<int:item_id>")
def get_item(item_id):
    item = items.get(item_id) or abort(404, "Item not found")
    return jsonify(item)


@app.post("/api/items")
def create_item():
    global next_id
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        abort(400, "JSON body with 'name' is required")
    item = {"id": next_id, "name": data["name"], "qty": data.get("qty", 0)}
    items[next_id] = item
    next_id += 1
    return jsonify(item), 201


@app.put("/api/items/<int:item_id>")
def update_item(item_id):
    item = items.get(item_id) or abort(404, "Item not found")
    data = request.get_json(silent=True)
    if not data:
        abort(400, "JSON body required")
    item.update({k: data[k] for k in ("name", "qty") if k in data})
    return jsonify(item)


@app.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    if item_id not in items:
        abort(404, "Item not found")
    del items[item_id]
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)