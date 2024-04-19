extends Node

@onready var line_renderer = $Line2D
@onready var slider = $HSlider

var slider_position = 0.0

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	# Compute position of slider in world space
	var pos = slider.global_position + Vector2.RIGHT * slider.value * slider.size
	
	# Give it some offset from
	pos += Vector2(0, -10)
	
	# Update the dotted line
	line_renderer.points = [pos, pos + Vector2.UP * 1000]
	
	slider_position = pos.x
