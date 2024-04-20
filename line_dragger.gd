extends Node

@export var start: Vector2 = Vector2(0, 0)
@export var end: Vector2 = Vector2(200, 200)

@onready var line_renderer = $Line2D
@onready var start_collision = $S
@onready var end_collision = $E

var start_selected = false
var end_selected = false

func set_color(color: Color):
	line_renderer.default_color = color
	start_collision.modulate = color
	end_collision.modulate = color

func get_color() -> Color:
	return line_renderer.default_color

# Called when the node enters the scene tree for the first time.
func _ready():
	# randomize the hue of the line
	set_color(Color.from_hsv(randf(), 1, 1))

# Called from the line manager to set the start and end positions
func initialize(start_pos: Vector2, end_pos: Vector2):
	self.start = start_pos
	self.end = end_pos

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	# Always let go when the mouse is relaesed
	# This is needed when the mouse releases while moving quickly
	if not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		start_selected = false
		end_selected = false
	
	var mouse_pos = get_viewport().get_mouse_position()

	if start_selected:
		start = mouse_pos
	elif end_selected:
		end = mouse_pos

	line_renderer.points = [start, end]

	start_collision.position = start
	end_collision.position = end

# Bound to the input event of the start node
func _on_area_2d_input_event(viewport, event, shape_idx):
	if Input.is_action_just_pressed("Delete"):
		get_viewport().set_input_as_handled()
		# Destroy the object
		queue_free()

	if Input.is_action_just_pressed("Click"):
		start_selected = true
		# Set the input as as handeled so it doesn't trigger anything else
		get_viewport().set_input_as_handled()
	
	if Input.is_action_just_released("Click"):
		start_selected = false
		get_viewport().set_input_as_handled()

# Bound to the input event of the end node
func _on_area_2d_2_input_event(viewport, event, shape_idx):
	if Input.is_action_just_pressed("Delete"):
		get_viewport().set_input_as_handled()
		queue_free()

	if Input.is_action_just_pressed("Click"):
		end_selected = true
		get_viewport().set_input_as_handled()
	
	if Input.is_action_just_released("Click"):
		end_selected = false
		get_viewport().set_input_as_handled()
