extends Node3D

const Actor = preload("res://scripts/actor.gd")
const Combat = preload("res://scripts/combat.gd")
const Hud = preload("res://scripts/hud.gd")
var player: CharacterBody3D
var camera: Camera3D
var hud: Control
var actors: Array[CharacterBody3D] = []
var npcs: Array[CharacterBody3D] = []
var navigation := AStarGrid2D.new()
var paused := false
var muted := false
var fury := 100.0
var basic_fury_generation := 12.0
var potions := 4
var quest := 0
var kills := 0
var time := 0.0
var hover: CharacterBody3D
var selected_npc: CharacterBody3D
var dialog := ""
var notice_text := ""
var notification_clock := 7.0
var move_marker: MeshInstance3D
var marker_clock := 0.0
var fires: Array[Node3D] = []
var motes: Array[MeshInstance3D] = []
var numbers: Array[Dictionary] = []
var flash_effects: Array[Dictionary] = []
var camera_focus := Vector3.ZERO
var camera_size := 25.0
var area := "罗格营地"
var ambience: AudioStreamPlayer
var capture_path := ""
var capture_clock := 0.0
var smoke := false
var sound_cache: Dictionary = {}
var combat: Node
var camera_shake := 0.0
var portrait_mode := false
var portrait_angle := .30
var monster_total := 48
var mouse_drag_walk := false
var mouse_repath_timer := 0.0

func _ready() -> void:
	randomize()
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color("28363a")
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color("8eabb1")
	e.ambient_light_energy = .46
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	e.ssao_enabled=true
	e.ssao_radius=.65
	e.ssao_intensity=1.1
	e.glow_enabled=true
	e.glow_intensity=.40
	e.fog_enabled = true
	e.fog_light_color = Color("647979")
	e.fog_light_energy = .35
	e.fog_density = .0018
	env.environment = e
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -35, 0)
	sun.light_color = Color("bac9c5")
	sun.light_energy = .9
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 90
	add_child(sun)
	var scene = load("res://assets/models/rogue_encampment.glb").instantiate()
	add_child(scene)
	# A distant terrain skirt prevents the playable moor ending at a visible plane edge.
	var horizon := MeshInstance3D.new()
	var horizon_plane := PlaneMesh.new()
	horizon_plane.size=Vector2(220,220)
	horizon.mesh=horizon_plane
	horizon.position.y=-.08
	var horizon_material := StandardMaterial3D.new()
	horizon_material.albedo_color=Color("384536")
	horizon_material.roughness=1.0
	horizon.material_override=horizon_material
	add_child(horizon)
	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var floor_box := BoxShape3D.new()
	floor_box.size = Vector3(88, .2, 120)
	floor_shape.shape = floor_box
	floor_body.position = Vector3(0, -.13, -24)
	floor_body.add_child(floor_shape)
	add_child(floor_body)
	build_navigation()
	player = spawn("barbarian", "player", "野蛮人", "来自北方的旅人", Vector3(1,0,6))
	var reference = JSON.parse_string(FileAccess.get_file_as_string("res://data/skill_reference.json"))
	player.hp=280
	player.max_hp=280
	player.damage = 32.0 * float(reference.skills.lunging_strike.damage_coefficient)
	basic_fury_generation = float(reference.skills.lunging_strike.fury_generation)
	spawn("akara", "npc", "阿卡拉", "目盲之眼 · 女祭司", Vector3(-6.0,0,-2.0))
	spawn("kashya", "npc", "卡夏", "罗格卫队 · 指挥官", Vector3(8,0,-8))
	spawn("charsi", "npc", "恰西", "营地铁匠", Vector3(6.5,0,4))
	spawn("warriv", "npc", "瓦瑞夫", "向东行进的商队", Vector3(-5.5,0,10))
	spawn("warriv", "npc", "基德", "商人", Vector3(-13.5,0,10.0))
	for i in range(2):
		var a = spawn("kashya", "ally", "罗格斥候", "营地守卫", Vector3(-2.4+i*4.8,0,-19.5))
		a.hp = 240
		a.max_hp = 240
		a.damage = 5
	var packs := [Vector3(0,0,-25),Vector3(-12,0,-33),Vector3(11,0,-36),Vector3(-4,0,-44),Vector3(17,0,-49),Vector3(-18,0,-53),Vector3(3,0,-59),Vector3(0,0,-68)]
	for pack in range(packs.size()):
		for i in range(6):
			var angle := i*TAU/6
			var point: Vector3=packs[pack]+Vector3(cos(angle)*2.8,0,sin(angle)*2.8)
			var cell := free_cell(point)
			point=Vector3(cell.x*.5,0,cell.y*.5)
			var a=spawn("fallen","enemy","沉沦魔","鲜血荒地",point)
			a.hp=54.0+pack*3
			a.max_hp=a.hp
			a.damage=7.0
			if i==0 and pack in [3,5,7]:
				a.elite=true
				a.display_name=["裂骨者","荒地屠夫","洞窟守卫"][int((pack-3)/2)]
				a.hp=220
				a.max_hp=220
				a.damage=16
				a.figure.scale*=1.38
				a.speed=2.0
	combat=Combat.new()
	combat.world=self
	add_child(combat)
	# Lights, smoke, sparks and flames remain live engine objects.
	add_fire(Vector3(-1,.38,2),1.0)
	add_fire(Vector3(8.45,1.55,7.8),.75)
	for p in [Vector3(-3.65,2.8,-17),Vector3(3.65,2.8,-17),Vector3(-6,1.5,-4),Vector3(-10,1.7,10)]:
		add_fire(p,.3)
	var waypoint := OmniLight3D.new()
	waypoint.position = Vector3(6,1,-1)
	waypoint.light_color = Color("79bdc5")
	waypoint.light_energy = .9
	waypoint.omni_range = 3.5
	add_child(waypoint)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = camera_size
	camera.far = 180
	add_child(camera)
	camera_focus = Vector3(0,0,2)
	position_camera()
	camera.current = true
	move_marker = ring_mesh(.45,Color("b69a57"))
	move_marker.visible = false
	add_child(move_marker)
	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Hud.new()
	hud.world = self
	layer.add_child(hud)
	hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	load_audio()
	toast("罗格营地 · 最后的庇护所")
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			capture_path = arg.trim_prefix("--capture=")
			capture_clock = 3.0
		if arg == "--smoke-test": smoke = true
		if arg == "--view=hero":
			portrait_mode=true
			player.figure.rotation.y=PI
		if arg == "--view=combat":
			player.position=Vector3(0,0,-25)
			camera_focus=player.position
			camera_size=17
			call_deferred("capture_combat")
		if arg == "--view=moor":
			player.position = Vector3(0,0,-23)
			camera_focus = player.position
		if arg == "--view=akara":
			player.position = Vector3(-4,0,-1)
			camera_focus = Vector3(-5,0,-4)
			call_deferred("talk", npcs[0])
	if smoke: call_deferred("run_smoke_test")

func build_navigation() -> void:
	navigation.region = Rect2i(-76,-156,152,212)
	navigation.cell_size = Vector2(.5,.5)
	navigation.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	navigation.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	navigation.default_estimate_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	navigation.update()
	var data = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	for item in data.obstacles:
		var x: float = item[0]
		var z: float = item[1]
		var w: float = item[2]
		var d: float = item[3]
		var body := StaticBody3D.new()
		var collision := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(w,2.8,d)
		collision.shape = box
		body.position = Vector3(x,1.4,z)
		body.add_child(collision)
		add_child(body)
		for ix in range(int(floor((x-w/2-.38)*2)),int(ceil((x+w/2+.38)*2))+1):
			for iz in range(int(floor((z-d/2-.38)*2)),int(ceil((z+d/2+.38)*2))+1):
				var id := Vector2i(ix,iz)
				if navigation.is_in_boundsv(id): navigation.set_point_solid(id)
	# The continuous defensive wall is blocked even between individual wood posts.
	for ix in range(-42,43):
		for iz in range(-39,43):
			var x := ix * .5
			var z := iz * .5
			var radius := sqrt(pow(x/20,2)+pow((z-1)/19,2))
			if radius > .95 and radius < 1.05 and not (z < -15 and absf(x) < 3.0):
				navigation.set_point_solid(Vector2i(ix,iz))

func free_cell(p: Vector3) -> Vector2i:
	var id := Vector2i(clampi(roundi(p.x*2),-75,74),clampi(roundi(p.z*2),-155,54))
	if not navigation.is_point_solid(id): return id
	for radius in range(1,9):
		for x in range(-radius,radius+1):
			for z in range(-radius,radius+1):
				var n := id+Vector2i(x,z)
				if navigation.is_in_boundsv(n) and not navigation.is_point_solid(n): return n
	return id

func make_path(a: Vector3, b: Vector3) -> PackedVector3Array:
	var result := PackedVector3Array()
	var start := free_cell(a)
	var end := free_cell(b)
	if navigation.is_point_solid(start) or navigation.is_point_solid(end): return result
	var points := navigation.get_point_path(start,end,true)
	for p in points: result.append(Vector3(p.x,0,p.y))
	return result

func spawn(kind: String, team: String, name_text: String, role: String, p: Vector3) -> CharacterBody3D:
	var a = Actor.new()
	a.world=self
	a.kind=kind
	a.team=team
	a.display_name=name_text
	a.role_name=role
	a.position=p
	add_child(a)
	actors.append(a)
	if team=="npc": npcs.append(a)
	if team=="npc": a.face(Vector3(0,0,4))
	if kind=="charsi": a.face(Vector3(7,0,5.5))
	return a

func closest_opponent(who: CharacterBody3D) -> CharacterBody3D:
	var result: CharacterBody3D
	var dist := 9.0 if who.team=="enemy" else 7.0
	for other in actors:
		if other.dead or other.team == "npc":continue
		if who.team == "enemy" and other.team == "enemy":continue
		if who.team == "ally" and other.team != "enemy":continue
		if who.team == "ally" and who.home_position.distance_to(other.position)>6.5:continue
		if other.position.z > -16:continue
		var d := who.position.distance_to(other.position)
		if who.team == "enemy" and other.team == "ally" and d>4.5:continue
		if d<dist:
			dist=d
			result=other
	return result

func position_camera() -> void:
	if portrait_mode:
		var focus: Vector3=player.position+Vector3.UP*1.15
		camera.position=focus+Vector3(sin(portrait_angle)*5,.7,cos(portrait_angle)*5)
		camera.look_at(focus)
		camera.size=3.3
		return
	camera.position = camera_focus + Vector3(19,26,23)
	if camera_shake>0:camera.position+=Vector3(randf_range(-.10,.10),randf_range(-.05,.05),0)*camera_shake*5
	camera.look_at(camera_focus)
	camera.size = camera_size

func _process(delta: float) -> void:
	if not paused:
		time += delta
		camera_shake=maxf(0,camera_shake-delta)
		camera_focus = camera_focus.lerp(player.position + Vector3(0,0,-1.6),1.0-exp(-delta*3.0))
		position_camera()
		notification_clock = maxf(0,notification_clock-delta)
		marker_clock -= delta
		move_marker.visible = marker_clock > 0
		if marker_clock > 0:
			move_marker.scale = Vector3.ONE * (1+.12*sin(marker_clock*12))
		for fire in fires:
			var light: OmniLight3D = fire.get_node("WarmLight")
			light.light_energy = (1.4 + sin(time*9+fire.position.x)*.12+sin(time*17)*.06) * fire.get_meta("power")
			for child in fire.get_children():
				if child is MeshInstance3D:
					child.scale.y = 1+sin(time*7+child.position.x*18)*.12
					child.look_at(camera.global_position)
					child.material_override.set_shader_parameter("clock",time)
		for i in range(motes.size()):
			var m := motes[i]
			var t := fmod(time*.6+i*.271,2.8)
			m.position = Vector3(-1+sin(time+i)*(.1+t*.12),.7+t,2+cos(time*.8+i)*(.1+t*.12))
		for n in numbers:n.ttl -= delta
		numbers = numbers.filter(func(n):return n.ttl>0)
		for f in flash_effects:
			f.ttl -= delta
			f.mesh.scale += Vector3.ONE*delta*3
			if f.ttl<=0: f.mesh.queue_free()
		flash_effects = flash_effects.filter(func(f):return f.ttl>0)
		var new_area := "鲜血荒地" if player.position.z < -18 else "罗格营地"
		if new_area != area:
			area=new_area
			toast(area + (" · 邪恶正在逼近" if area=="鲜血荒地" else " · 安全区域"))
		if player.position.z < -69 and quest==1:
			quest=2
			toast("你找到了邪恶洞窟。深处的黑暗仍在等待。")
		if mouse_drag_walk and not player.dead and not portrait_mode and not combat.channeling and combat.leap_clock<=0:
			if not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
				mouse_drag_walk = false
			else:
				mouse_repath_timer -= delta
				if mouse_repath_timer <= 0.0:
					mouse_repath_timer = 0.08
					var pt := mouse_ground()
					if not (is_instance_valid(hover) and (hover.team=="enemy" or hover.team=="npc")) and pt.distance_to(player.position) > 0.6:
						player.target = null
						player.walk_to(pt)
	update_hover()
	hud.queue_redraw()
	if capture_clock>0:
		capture_clock-=delta
		if capture_clock<=0:
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(capture_path)
			print("Captured: "+capture_path)
			print("Render: fps="+str(Engine.get_frames_per_second())+", draw_calls="+str(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)))
			get_tree().quit()

func update_hover() -> void:
	hover = null
	var mouse := get_viewport().get_mouse_position()
	var closest := 48.0
	for a in actors:
		if a==player or a.dead or camera.is_position_behind(a.position):continue
		var screen := camera.unproject_position(a.position+Vector3.UP*1.2)
		var d := screen.distance_to(mouse)
		if d<closest:
			closest=d
			hover=a
	Input.set_default_cursor_shape(Input.CURSOR_POINTING_HAND if hover else Input.CURSOR_ARROW)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode==KEY_F7:
			get_tree().change_scene_to_file("res://scenes/hero_review.tscn")
			return
		if event.keycode==KEY_ESCAPE:
			if not dialog.is_empty():close_dialog()
			else: paused = not paused
			combat.cancel()
		if event.keycode==KEY_M:
			muted=not muted
			AudioServer.set_bus_mute(0,muted)
		if event.keycode==KEY_F11:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if DisplayServer.window_get_mode()==DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
		if event.keycode==KEY_Q and not paused and not player.dead:
			if player.hp<player.max_hp and potions>0:
				potions-=1
				player.hp=minf(player.max_hp,player.hp+105)
				toast("药剂恢复了生命")
		if event.keycode==KEY_C and not player.dead:
			portrait_mode=not portrait_mode
			player.stop()
			player.target=null
			combat.cancel()
			if portrait_mode:player.figure.rotation.y=PI
		if event.keycode in [KEY_1,KEY_2,KEY_3,KEY_4]:
			combat.cast(int(event.keycode-KEY_1)+2,mouse_ground())
		if event.keycode==KEY_R and player.dead:get_tree().reload_current_scene()
	if event is InputEventMouseMotion and portrait_mode and Input.is_mouse_button_pressed(MOUSE_BUTTON_MIDDLE):
		portrait_angle-=event.relative.x*.009
	if event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_RIGHT and not event.pressed:
		combat.cancel()
		player.stop()
		return
	if event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT and not event.pressed:
		mouse_drag_walk = false
	if not event is InputEventMouseButton or not event.pressed:return
	if event.button_index==MOUSE_BUTTON_WHEEL_UP:
		camera_size=clampf(camera_size-1.2,9,34)
		return
	if event.button_index==MOUSE_BUTTON_WHEEL_DOWN:
		camera_size=clampf(camera_size+1.2,9,34)
		return
	if paused or not dialog.is_empty() or player.dead or portrait_mode or combat.leap_clock>0:return
	if event.button_index==MOUSE_BUTTON_RIGHT:
		combat.cast(1,mouse_ground())
		return
	if event.button_index==MOUSE_BUTTON_LEFT:
		combat.cancel()
		if is_instance_valid(hover):
			if hover.team=="npc" or hover.team=="enemy":
				player.target=hover
				player.walk_to(hover.position)
				play_sound("click",player.position)
				return
		mouse_drag_walk = true
		mouse_repath_timer = 0.08
		var origin := camera.project_ray_origin(event.position)
		var direction := camera.project_ray_normal(event.position)
		var point = Plane(Vector3.UP,0).intersects_ray(origin,direction)
		if point!=null:
			player.target=null
			player.walk_to(point)
			if player.path.size()>0:
				move_marker.position=player.path[-1]+Vector3.UP*.06
				marker_clock=1.4
			play_sound("click",player.position)

func talk(person: CharacterBody3D) -> void:
	combat.cancel()
	player.stop()
	selected_npc=person
	player.face(person.position)
	person.face(player.position)
	match person.display_name:
		"阿卡拉":
			dialog="我们曾在修道院守望群山，如今只剩这片营地。黑暗追随着一个向东而去的旅人，也夺走了我们的家园。\n斥候在鲜血荒地发现了一处藏满邪物的洞窟。如果你愿意帮助我们，就从那里开始。" if quest==0 else "穿过北面的木门，沿荒地中的小径前行，你会找到邪恶洞窟。清除里面所有的邪物，让姐妹们能够在夜里安睡。"
		"卡夏":dialog="我们的姐妹还在木门外作战。曾经并肩守卫修道院的人，如今有些已经向黑暗低头。\n如果你想赢得罗格的信任，就让我们看看你的武器能做些什么。"
		"恰西":dialog="你是从北方来的？我听过你们部族的传说。看这柄战斧，它比营地里大多数人的行囊还重。\n我把最好的工具留在了修道院。不过炉火还在，铁砧也还在——我们仍能重新开始。"
		"瓦瑞夫":dialog="我本来要带商队向东，直到修道院的道路被恶魔封锁。一个沉默的旅人曾与我们同行，他离开后，灾祸接踵而至。\n在道路恢复安全之前，这里就是我们的家。去见见阿卡拉，她一直在等一个能够带来希望的人。"
		"基德":dialog="在这种时候，一件可靠的武器比一袋金币更有价值。当然，要是你坚持带着金币，我也非常乐意帮你减轻行囊。\n商队暂时停在这里。先活着回来，我们总有机会谈生意。"
	play_sound("click",player.position)

func close_dialog() -> void:
	if is_instance_valid(selected_npc) and selected_npc.kind=="charsi":selected_npc.face(Vector3(7,0,5.5))
	dialog=""
	selected_npc=null

func accept_quest() -> void:
	quest=1
	close_dialog()
	toast("任务已接受 · 邪恶洞窟")
	play_sound("quest",player.position)

func toast(message: String) -> void:
	notice_text=message
	notification_clock=5.5

func on_death(actor: CharacterBody3D) -> void:
	if actor.team=="enemy":
		kills+=1
		if actor.target==player and potions<4 and kills%3==0:potions+=1
		play_sound("impact",actor.position,.7)
	elif actor==player:
		toast("你的旅程尚未结束。按 R 返回营地。")

func damage_number(actor: CharacterBody3D, value: float) -> void:
	numbers.append({"point":actor.position+Vector3.UP*2.2,"value":str(int(ceil(value))),"ttl":.9,"enemy":actor.team=="enemy"})

func ring_mesh(radius: float, color: Color) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var t := TorusMesh.new()
	t.inner_radius=radius-.026
	t.outer_radius=radius+.026
	t.rings=32
	t.ring_segments=6
	m.mesh=t
	var mat := StandardMaterial3D.new()
	mat.albedo_color=color
	mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	m.material_override=mat
	return m

func hit_effect(p: Vector3, is_enemy: bool) -> void:
	var m := ring_mesh(.26,Color("ecbc75") if is_enemy else Color("ab3d31"))
	add_child(m)
	m.position=p
	m.rotation_degrees.x=70
	flash_effects.append({"mesh":m,"ttl":.16})
	play_sound("impact",p,randf_range(.85,1.15))

func add_fire(p: Vector3, size: float) -> void:
	var node := Node3D.new()
	node.position=p
	node.set_meta("power",size)
	add_child(node)
	var light := OmniLight3D.new()
	light.name="WarmLight"
	light.position.y=.6
	light.light_color=Color("ffa65e")
	light.light_energy=1.5*size
	light.omni_range=8.5*sqrt(size)
	node.add_child(light)
	for i in range(7):
		var flame := MeshInstance3D.new()
		var shape := QuadMesh.new()
		shape.size=Vector2(randf_range(.65,.9),randf_range(1.15,1.75))*size
		flame.mesh=shape
		var mat := ShaderMaterial.new()
		mat.shader=load("res://shaders/flame.gdshader")
		mat.set_shader_parameter("phase",float(i)*1.7)
		flame.material_override=mat
		flame.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		flame.position=Vector3(randf_range(-.28,.28)*size,shape.size.y*.40,randf_range(-.20,.20)*size)
		node.add_child(flame)
	fires.append(node)
	if size>.9:
		for i in range(18):
			var spark := MeshInstance3D.new()
			var sphere := SphereMesh.new()
			sphere.radius=.014
			sphere.height=.028
			sphere.radial_segments=4
			sphere.rings=3
			spark.mesh=sphere
			var m := StandardMaterial3D.new()
			m.albedo_color=Color("ffcb7d")
			m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
			spark.material_override=m
			add_child(spark)
			motes.append(spark)

func load_audio() -> void:
	# The headless interaction test has no audio output; visual runs exercise audio.
	if DisplayServer.get_name()=="headless":return
	for id in ["wind","click","impact","swing","quest","shout","slam","leap"]:
		var path: String = "res://assets/audio/"+id+".wav"
		if ResourceLoader.exists(path):sound_cache[id]=load(path)
	if sound_cache.has("wind"):
		ambience=AudioStreamPlayer.new()
		ambience.stream=sound_cache.wind
		ambience.volume_db=-16
		add_child(ambience)
		ambience.finished.connect(func():ambience.play())
		ambience.play()

func _exit_tree() -> void:
	for node in get_children():
		if node is AudioStreamPlayer or node is AudioStreamPlayer3D:
			node.stop()
			node.stream=null
	sound_cache.clear()

func play_sound(id: String, p: Vector3, pitch: float = 1.0) -> void:
	if not sound_cache.has(id):return
	var audio := AudioStreamPlayer3D.new()
	audio.stream=sound_cache[id]
	audio.position=p+Vector3.UP
	audio.pitch_scale=pitch
	audio.unit_size=18
	audio.max_distance=70
	audio.volume_db=-9
	add_child(audio)
	audio.finished.connect(audio.queue_free)
	audio.play()

func run_smoke_test() -> void:
	await get_tree().process_frame
	assert(npcs.size()==5,"Five opening NPCs")
	assert(actors.size()==56,"Player, five NPCs, two rogues and 48 monsters")
	assert(player.skeleton!=null and player.skeleton.get_bone_count()>=100,"Anatomical skeleton imported")
	assert(player.animation_names.size()==10,"Ten Blender clips imported")
	for label in player.animation_names:
		var clip: Animation = player.animation_player.get_animation(player.animation_names[label])
		assert(absf(clip.length-player.clip_duration(label, clip.length))<.035,"Animation timing matches gameplay: "+label)
	for i in range(16):
		assert(player.skeleton.find_bone("tasset.%02d" % i)>=0,"Articulated skirt panel imported")
	assert(combat.active_unlocked.all(func(v):return v),"All six skills unlocked at spawn")
	assert(fury==100 and combat.cooldowns.all(func(v):return v==0),"Full initial Fury and no cooldowns")
	var p := make_path(Vector3(1,0,6),Vector3(0,0,-23))
	assert(p.size()>10,"Camp to moor path exists")
	for point in p:assert(not navigation.is_point_solid(free_cell(point)),"Path avoids blocked cells")
	# Exercise the actual mouse input path and movement in the live scene.
	var origin := player.position
	var event := InputEventMouseButton.new()
	event.button_index=MOUSE_BUTTON_LEFT
	event.pressed=true
	event.position=camera.unproject_position(Vector3(3,0,5))
	hover=null
	_unhandled_input(event)
	await get_tree().create_timer(1.0).timeout
	assert(player.position.distance_to(origin)>.3,"Mouse movement executes")
	player.target=npcs[0]
	player.walk_to(npcs[0].position)
	for i in range(100):
		await get_tree().create_timer(.1).timeout
		if not dialog.is_empty():break
	assert(not dialog.is_empty(),"NPC dialogue")
	accept_quest()
	assert(quest==1 and dialog.is_empty(),"Quest acceptance")
	player.stop()
	var stationary := player.position
	var key := InputEventKey.new()
	key.keycode=KEY_W
	key.pressed=true
	_unhandled_input(key)
	await get_tree().create_timer(.2).timeout
	assert(player.position.distance_to(stationary)<.03,"WASD is not mapped to movement")
	# Isolate combat subjects while exercising the real scene and physics callbacks.
	for a in actors:
		if a.team=="enemy" or a.team=="ally":a.set_physics_process(false)
	player.position=Vector3(0,0,-43)
	player.target=null
	player.stop()
	var dummy=spawn("fallen","enemy","技能验证目标","",player.position+Vector3(0,0,-3.2))
	dummy.hp=1000
	dummy.max_hp=1000
	dummy.damage=0
	dummy.speed=0
	fury=0
	hover=dummy
	event.position=camera.unproject_position(dummy.position)
	_unhandled_input(event)
	await get_tree().create_timer(1.0).timeout
	assert(dummy.hp<1000 and fury>=12,"Lunging Strike hits and generates Fury")
	player.target=null
	player.stop()
	fury=100
	var ally=actors.filter(func(a):return a.team=="ally")[0]
	ally.position=player.position+Vector3(1,0,0)
	key.keycode=KEY_1
	_unhandled_input(key)
	assert(player.rally_buff>3.9 and fury==65,"Rallying Cry costs 35 Fury and grants 4 seconds")
	assert(is_equal_approx(ally.rally_bonus,.10) and is_equal_approx(ally.rally_buff,2),"Nearby ally gets half rally effect")
	await get_tree().create_timer(.75).timeout
	key.keycode=KEY_2
	_unhandled_input(key)
	assert(player.war_buff>3.9 and combat.cooldowns[3]>24.9,"War Cry buff and cooldown")
	assert(is_equal_approx(ally.war_bonus,.0375),"War Cry affects ally")
	assert(not combat.cast(3,player.position),"Cooldown blocks repeated cast")
	await get_tree().create_timer(.85).timeout
	var landing: Vector3=player.position+Vector3(0,0,-7)
	dummy.position=landing+Vector3(1,0,0)
	var before: float=dummy.hp
	assert(combat.cast(4,landing),"Leap accepts open ground")
	var takeoff_position := player.position
	await get_tree().create_timer(.10).timeout
	assert(player.position.distance_to(takeoff_position)<.04,"Leap anticipation remains grounded")
	await get_tree().create_timer(.25).timeout
	assert(player.position.y>1,"Leap follows airborne arc")
	await get_tree().create_timer(.55).timeout
	assert(player.position.distance_to(landing)<.8,"Leap lands at requested point")
	assert(dummy.hp<before and dummy.slow_clock>2,"Leap deals damage and slows nearby enemies")
	assert(fury==80,"Leap generates 15 Fury")
	assert(combat.leap_clock>0,"Landing recovery finishes before another skill")
	assert(not combat.cast(1,player.position),"Landing recovery cannot be interrupted by whirlwind")
	await get_tree().create_timer(.22).timeout
	combat.cooldowns[4]=0
	assert(not combat.cast(4,player.position),"Invalid near leap costs no cooldown")
	assert(combat.cooldowns[4]==0,"Invalid leap does not spend cooldown")
	var dummy2=spawn("fallen","enemy","范围目标","",player.position+Vector3(-1,0,0))
	dummy2.hp=1000
	dummy2.max_hp=1000
	dummy2.damage=0
	dummy2.speed=0
	before=dummy.hp
	var fury_before := fury
	event.button_index=MOUSE_BUTTON_RIGHT
	event.pressed=true
	_unhandled_input(event)
	combat.channel_repath=1.0
	await get_tree().create_timer(.55).timeout
	assert(combat.channeling and dummy.hp<before and dummy2.hp<1000,"Whirlwind hits multiple enemies")
	assert(fury<fury_before and fury>fury_before-10 and fury<fury_before-6,"Whirlwind spends Fury by elapsed time")
	event.pressed=false
	_unhandled_input(event)
	assert(not combat.channeling,"Releasing right mouse ends channel")
	key.keycode=KEY_4
	_unhandled_input(key)
	assert(player.berserk_buff>9.9 and player.unstoppable_buff>9.9,"Wrath grants 10 second Berserking and Unstoppable")
	assert(combat.cooldowns[5]>89.9,"Wrath keeps its 90 second cooldown")
	assert(dummy.push_velocity.length()>0,"Wrath knocks back nearby enemies")
	paused=true
	var clock := time
	var cd: float=combat.cooldowns[5]
	await get_tree().create_timer(.2).timeout
	assert(time==clock and combat.cooldowns[5]==cd,"Pause freezes world and cooldown clocks")
	paused=false
	await get_tree().create_timer(1.0).timeout
	fury=100
	assert(combat.cast(1,player.position),"Whirlwind can start again")
	player.receive_damage(10000,dummy)
	await get_tree().create_timer(.1).timeout
	assert(player.dead and not combat.channeling and combat.leap_clock==0,"Death cancels skills")
	print("ASHEN OATH SMOKE PASS: skeletal hero, 48 monsters, mouse navigation, NPC dialogue, quest, no WASD, all six skills, Fury, AOE, ally buffs, leap, cooldown, pause and death.")
	for node in get_children():
		if node is AudioStreamPlayer or node is AudioStreamPlayer3D:
			node.stop()
			node.stream=null
	sound_cache.clear()
	await get_tree().process_frame
	get_tree().quit()

func mouse_ground() -> Vector3:
	var screen := get_viewport().get_mouse_position()
	var origin := camera.project_ray_origin(screen)
	var direction := camera.project_ray_normal(screen)
	var point=Plane(Vector3.UP,0).intersects_ray(origin,direction)
	return point if point!=null else player.position

func capture_combat() -> void:
	await get_tree().create_timer(.5).timeout
	combat.cast(5,player.position)
	await get_tree().create_timer(1).timeout
	combat.cast(1,player.position)

func line_of_sight(a: Vector3,b: Vector3) -> bool:
	var ray := PhysicsRayQueryParameters3D.create(a+Vector3.UP,b+Vector3.UP,1)
	return get_world_3d().direct_space_state.intersect_ray(ray).is_empty()

func _notification(what: int) -> void:
	if what==NOTIFICATION_APPLICATION_FOCUS_OUT and is_instance_valid(combat):
		combat.cancel()
		player.stop()
