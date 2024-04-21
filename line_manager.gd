extends Node

@export var line_scene: PackedScene
@export var event_indicator_scene: PackedScene

# The array of lines for doing sweep line intersection
var lines: Array[Node] = []

# $Slider is shorthand for get_node("Slider")
@onready var slider = $Slider

@onready var ben_ott = $BenOtt

func add_line(start: Vector2, end: Vector2):
	# Spawn the line in the world
	var line = line_scene.instantiate()
	# Call initialize on `line_dragger.gd`
	line.initialize(start, end)
	
	# Add as a child of ourselves
	add_child(line)
	lines.append(line)
	
# Called when the node enters the scene tree for the first time.
func _ready():
	# Start us off with a single line
	add_line(Vector2(100, 100), Vector2(300, 100))

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	print(ben_ott.FindSegmentIntersections(lines))
	update_event_indicators();
	pass
	
var event_indicators: Array[Node2D] = []
func update_event_indicators():
	# Get rid of old indicators
	for e in event_indicators:
		e.queue_free();
	
	event_indicators = []
	
	# Add new indicators
	for e in ben_ott.GetEvents():
		var event = event_indicator_scene.instantiate()
		event.position = Vector2(e, slider.get_node("HSlider").global_position.y)
		event_indicators.append(event)
		add_child(event)

# Wired up to the `Add line` button
func add_random_line():
	var max_y = 600;
	var max_x = 800;
	
	var x1 = randf_range(0, max_x);
	var y1 = randf_range(0, max_y);
	var x2 = randf_range(0, max_x);
	var y2 = randf_range(0, max_y);
	
	add_line(Vector2(x1, y1), Vector2(x2, y2))

# Remove lines when they are destroyed
func _on_child_exiting_tree(node):
	# Check if the deleted node is in the array, and remove it if it is
	for i in range(0, lines.size()):
		if lines[i] == node:
			lines.remove_at(i)
			return
