extends Node2D

@export var line_scene: PackedScene

@export var lines: Array[Node2D] = []

func add_line(start: Vector2, end: Vector2):
	var line = line_scene.instantiate() as Node2D
	line.position = start

	var line_renderer = line.get_node("Line2D") as Line2D
	line_renderer.points = [Vector2(0, 0), end - start]
	
	
	add_child(line)
	lines.append(line)

# Called when the node enters the scene tree for the first time.
func _ready():
	add_line(Vector2(0, 0), Vector2(100, 100))
	# add_line(Vector2(20, 200), Vector2(200, 100))

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	# var pos = get_global_mouse_position()
	# lines[0].get_node("Line2D").points[1] = pos
	pass
