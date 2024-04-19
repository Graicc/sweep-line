extends Node2D

@export var line_scene: PackedScene

@export var lines: Array[Node2D] = []

func add_line(start: Vector2, end: Vector2):
	var line = line_scene.instantiate() as Node2D
	# Call initialize on `line_dragger.gd`
	line.initialize(start, end)
	
	# Add as a child of ourselves
	add_child(line)
	lines.append(line)

# Called when the node enters the scene tree for the first time.
func _ready():
	add_line(Vector2(100, 100), Vector2(300, 100))
	# add_line(Vector2(20, 200), Vector2(200, 100))

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	# var pos = get_global_mouse_position()
	# lines[0].get_node("Line2D").points[1] = pos
	pass


func _on_button_pressed():
	var max_y = 600;
	var max_x = 800;
	var x1 = randf_range(0, max_x);
	var y1 = randf_range(0, max_y);
	var x2 = randf_range(0, max_x);
	var y2 = randf_range(0, max_y);
	add_line(Vector2(x1, y1), Vector2(x2, y2))
	
	pass # Replace with function body.
