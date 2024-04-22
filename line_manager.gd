extends Node

@export var line_scene: PackedScene
@export var event_indicator_scene: PackedScene
@export var segment_indicator_scene: PackedScene

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
	update_intersection_indicators()
	update_event_indicators()
	update_segment_indicator()
	
var intersection_indicators: Array[Sprite2D] = []
func update_intersection_indicators():
	# Get rid of old indicators
	for i in intersection_indicators:
		i.queue_free();
	
	intersection_indicators = []
	
	# Add new indicators
	for i in ben_ott.FindSegmentIntersections(lines):
		var intersection = segment_indicator_scene.instantiate()
		intersection.position = i
		intersection.z_index = 10
		intersection.scale *= 0.5
		intersection.modulate = Color(1, 1, 1)
		intersection_indicators.append(intersection)
		add_child(intersection)
	
# Vertical ticks on the slider
var event_indicators: Array[Node2D] = []
func update_event_indicators():
	# Get rid of old indicators
	for e in event_indicators:
		e.queue_free();
	
	event_indicators = []
	
	# Add new indicators
	for e in ben_ott.GetEvents():
		var event = event_indicator_scene.instantiate()
		event.z_index = 10
		event.position = Vector2(e, slider.get_node("HSlider").global_position.y)
		event_indicators.append(event)
		add_child(event)

# Circles showing the ordering of segments
var segment_indicators: Array[Sprite2D] = []
func update_segment_indicator():
	# Get rid of old indicators
	for s in segment_indicators:
		s.queue_free();
	
	segment_indicators = []
	
	var offset = Vector2(20, 20)
	var delta = Vector2(0, 35)

	var i = 0;

	# Add new indicators
	for s in ben_ott.GetSegmentsAtTime(slider.slider_position):
		var segment: Sprite2D = segment_indicator_scene.instantiate()
		segment.position = offset + delta * i
		segment.modulate = s.get_color()
		segment.z_index = 10
		segment_indicators.append(segment)
		add_child(segment)

		i += 1
	

# Wired up to the `Add line` button
func add_random_line():
	var size = DisplayServer.window_get_size()
	var margin = 50

	var max_y = size.y - margin;
	var max_x = size.x - margin;
	
	var x1 = randf_range(margin, max_x);
	var y1 = randf_range(margin, max_y);
	var x2 = randf_range(margin, max_x);
	var y2 = randf_range(margin, max_y);
	
	add_line(Vector2(x1, y1), Vector2(x2, y2))

# Remove lines when they are destroyed
func _on_child_exiting_tree(node):
	# Check if the deleted node is in the array, and remove it if it is
	for i in range(0, lines.size()):
		if lines[i] == node:
			lines.remove_at(i)
			return
