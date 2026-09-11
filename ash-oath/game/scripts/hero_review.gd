extends Node3D
## Inspect the actual exported game asset, its grips, and all animation phases.

const CLIPS := ["Idle", "Run", "Attack", "Whirlwind", "Rally", "WarCry", "Leap", "Berserk", "Hit", "Death"]
const TITLES := ["待机 · 呼吸", "跑动 · 步态", "突刺 · 挥斧", "旋风斩", "集结呐喊", "战吼", "腾空斩", "狂战士之怒", "受击", "倒地"]
var models: Array[Node3D] = []
var players: Array[AnimationPlayer] = []
var names: Array[Dictionary] = []
var profile: Dictionary
var clip_index := 0
var clock := 0.0
var total_clock := 0.0
var freeze := false
var slow := false
var showreel := false
var snapshot := ""
var snapshot_phase := .48
var capture_ready := false
var title: Label
var progress: ProgressBar

func _ready() -> void:
	profile=JSON.parse_string(FileAccess.get_file_as_string("res://data/barbarian_animation.json"))
	var environment := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode=Environment.BG_COLOR
	e.background_color=Color("141b20")
	e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color=Color("abbecb")
	e.ambient_light_energy=.5
	e.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	e.ssao_enabled=true
	e.ssao_radius=.20
	e.ssao_intensity=1.3
	environment.environment=e
	add_child(environment)
	for spec in [[Vector3(-2,5,4),Color("ffe0bb"),1.2], [Vector3(3,4,-3),Color("afcfe8"),1.6]]:
		var light := DirectionalLight3D.new()
		add_child(light)
		light.position=spec[0]
		light.look_at(Vector3(0,1,0))
		light.light_color=spec[1]
		light.light_energy=spec[2]
		light.shadow_enabled=true
		light.directional_shadow_max_distance=30
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size=Vector2(200,200)
	floor_mesh.mesh=plane
	var mat := StandardMaterial3D.new()
	mat.albedo_color=Color(.022,.028,.032)
	mat.roughness=.88
	floor_mesh.material_override=mat
	add_child(floor_mesh)
	var scene: PackedScene=load("res://assets/models/barbarian.glb")
	for i in range(3):
		var holder := Node3D.new()
		add_child(holder)
		holder.position.x=(i-1)*2.4
		var model := scene.instantiate()
		holder.add_child(model)
		model.rotation.y=[0.0, -.72, PI][i]
		models.append(model)
		var player: AnimationPlayer=model.find_child("AnimationPlayer",true,false)
		player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		players.append(player)
		var mapping := {}
		for animation in player.get_animation_list():
			for label in CLIPS:
				if animation.ends_with(label):mapping[label]=animation
		names.append(mapping)
	var camera := Camera3D.new()
	add_child(camera)
	camera.projection=Camera3D.PROJECTION_ORTHOGONAL
	camera.size=5.15
	camera.position=Vector3(0,3.0,10)
	camera.look_at(Vector3(0,1.17,0))
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var root := Control.new()
	canvas.add_child(root)
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	title=Label.new()
	title.position=Vector2(55,46)
	title.add_theme_font_size_override("font_size",30)
	title.add_theme_color_override("font_color",Color("e4cb92"))
	root.add_child(title)
	var subtitle := Label.new()
	subtitle.text="ASHEN OATH    /    野蛮人动作检查"
	subtitle.position=Vector2(57,22)
	subtitle.add_theme_font_size_override("font_size",14)
	subtitle.modulate=Color("9ca8a8")
	root.add_child(subtitle)
	var footer := Label.new()
	footer.text="← → 切换动作     空格 暂停     S 慢放     Esc 返回营地"
	footer.position=Vector2(55,940)
	footer.add_theme_font_size_override("font_size",18)
	footer.modulate=Color("aeb8b7")
	root.add_child(footer)
	progress=ProgressBar.new()
	progress.position=Vector2(55,910)
	progress.size=Vector2(1490,3)
	progress.show_percentage=false
	var background := StyleBoxFlat.new()
	background.bg_color=Color("344148")
	var fill := StyleBoxFlat.new()
	fill.bg_color=Color("b8a371")
	progress.add_theme_stylebox_override("background",background)
	progress.add_theme_stylebox_override("fill",fill)
	root.add_child(progress)
	for arg in OS.get_cmdline_user_args():
		if arg=="--showreel":showreel=true
		elif arg.begins_with("--review-capture="):snapshot=arg.trim_prefix("--review-capture=")
		elif arg.begins_with("--clip="):clip_index=maxi(0,CLIPS.find(arg.trim_prefix("--clip=")))
		elif arg.begins_with("--phase="):snapshot_phase=arg.trim_prefix("--phase=").to_float()
	select_clip(clip_index)
	if not snapshot.is_empty():
		freeze=true
		clock=float(profile.clips[CLIPS[clip_index]].duration)*snapshot_phase
		pose_at(clock)
		capture_ready=true

func select_clip(index: int) -> void:
	clip_index=posmod(index,CLIPS.size())
	clock=0.0
	title.text="%02d / %02d    %s" % [clip_index+1,CLIPS.size(),TITLES[clip_index]]
	for i in range(players.size()):
		# Inspection samples exact poses with seek(); a timed blend would never
		# advance when sampling with advance(0), leaving the previous clip visible.
		players[i].play(names[i][CLIPS[clip_index]],0.0)
		players[i].seek(0,true)

func pose_at(seconds: float) -> void:
	var label: String=CLIPS[clip_index]
	var duration: float=profile.clips[label].duration
	var cycle := duration if label in ["Idle","Run","Whirlwind"] else duration+.40
	var phase := minf(seconds,duration) if label=="Death" else fmod(seconds,cycle)
	for i in range(players.size()):
		players[i].seek(minf(phase,duration),true)
		players[i].advance(0)
		models[i].position.y=0
		models[i].rotation.y=[0.0,-.72,PI][i]
		if label=="Whirlwind":models[i].rotation.y+=seconds*15.5
		elif label=="Leap":
			var t := clampf((phase-float(profile.leap_takeoff_seconds))/(float(profile.leap_land_seconds)-float(profile.leap_takeoff_seconds)),0,1)
			# Compact stage flight uses the exact launch/impact timing from combat.
			models[i].position.y=4*t*(1-t)*.55
	progress.value=clampf(phase/duration,0,1)*100

func _process(delta: float) -> void:
	if not freeze:
		clock+=delta*(.25 if slow else 1.0)
		total_clock+=delta
		if showreel:
			var index := mini(int(total_clock/3.0),CLIPS.size()-1)
			if index!=clip_index:select_clip(index)
			if total_clock>=CLIPS.size()*3.0:get_tree().quit()
		pose_at(clock)
	if capture_ready:
		capture_ready=false
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(snapshot)
		print("REVIEW CAPTURE: "+snapshot)
		get_tree().quit()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_RIGHT:select_clip(clip_index+1)
			KEY_LEFT:select_clip(clip_index-1)
			KEY_SPACE:freeze=not freeze
			KEY_S:slow=not slow
			KEY_ESCAPE:get_tree().change_scene_to_file("res://scenes/encampment.tscn")
