extends Node2D

@export var line_renderer: Line2D
@export var start: Vector2 = Vector2(0, 0)
@export var end: Vector2 = Vector2(200, 200)

@export var start_collision: Area2D
@export var end_collision: Area2D

func set_color(color: Color):
	line_renderer.default_color = color
	start_collision.modulate = color
	end_collision.modulate = color

# Called when the node enters the scene tree for the first time.
func _ready():
	# randomize the hue of the line
	var color = Color.from_hsv(randf(), 1, 1)
	set_color(color)


func initialize(start_pos: Vector2, end_pos: Vector2):
	self.start = start_pos
	self.end = end_pos

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if left_selected:
		var mouse_pos = get_viewport().get_mouse_position()
		start = mouse_pos
	elif right_selected:
		var mouse_pos = get_viewport().get_mouse_position()
		end = mouse_pos

	line_renderer.points = [start, end]
	start_collision.position = start
	end_collision.position = end


var left_selected = false
var right_selected = false

func _on_area_2d_input_event(viewport, event, shape_idx):
	if Input.is_action_just_pressed("Click"):
		left_selected = true
	
	if Input.is_action_just_released("Click"):
		left_selected = false



func _on_area_2d_2_input_event(viewport, event, shape_idx):
	if Input.is_action_just_pressed("Click"):
		right_selected = true
	
	if Input.is_action_just_released("Click"):
		right_selected = false

