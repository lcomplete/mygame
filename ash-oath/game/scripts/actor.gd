extends CharacterBody3D

var world: Node3D
var kind := "barbarian"
var display_name := "野蛮人"
var role_name := ""
var team := "player"
var hp := 120.0
var max_hp := 120.0
var speed := 4.5
var target: Node3D
var path := PackedVector3Array()
var path_index := 0
var figure: Node3D
var shoulders: Array[Node3D] = []
var hips: Array[Node3D] = []
var torso: Node3D
var age := 0.0
var attack_clock := 0.0
var attack_did_hit := false
var attack_total := 0.72
var hurt_clock := 0.0
var dead := false
var repath := 0.0
var base_y := 0.0
var damage := 17.0
var warning_ring: MeshInstance3D
var home_position := Vector3.ZERO
var animation_player: AnimationPlayer
var skeleton: Skeleton3D
var animation_names: Dictionary = {}
var current_animation := ""
var rally_buff := 0.0
var rally_bonus := 0.0
var war_buff := 0.0
var war_bonus := 0.0
var berserk_buff := 0.0
var unstoppable_buff := 0.0
var slow_clock := 0.0
var slow_fraction := 0.0
var push_velocity := Vector3.ZERO
var elite := false
var lunge_clock := 0.0

func _ready() -> void:
	home_position=position
	collision_layer = 2
	collision_mask = 3
	var hit := CollisionShape3D.new()
	var shape := CapsuleShape3D.new()
	shape.radius = 0.32
	shape.height = 1.8
	hit.shape = shape
	hit.position.y = 0.95
	add_child(hit)
	figure=Node3D.new()
	add_child(figure)
	var model=load("res://assets/models/"+kind+".glb").instantiate()
	figure.add_child(model)
	if kind=="barbarian":model.rotation.y=PI
	animation_player=figure.find_child("AnimationPlayer",true,false)
	skeleton=find_skeleton(figure)
	if animation_player:
		for animation in animation_player.get_animation_list():
			for label in ["Idle","Run","Attack","Whirlwind","Shout","Berserk","Leap","Death"]:
				if animation.ends_with(label):
					animation_names[label]=animation
					if label in ["Idle","Run","Whirlwind"]:animation_player.get_animation(animation).loop_mode=Animation.LOOP_LINEAR
		animation_player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		play_animation("Idle")
	if kind == "fallen":
		figure.scale = Vector3.ONE * 0.82
	elif kind != "barbarian":
		figure.scale = Vector3.ONE * 0.94
	for tag in ["L", "R"]:
		shoulders.append(figure.find_child("Shoulder_" + tag, true, false))
		hips.append(figure.find_child("Hip_" + tag, true, false))
	torso = figure.find_child("Torso", true, false)
	if torso: base_y = torso.position.y
	age = randf() * 8.0
	max_hp = hp
	if team == "enemy":
		speed = 2.5
		attack_total = 1.15
		warning_ring = world.ring_mesh(.85,Color("c9804c"))
		warning_ring.position.y = .05
		warning_ring.visible = false
		add_child(warning_ring)
	if team == "npc": speed = 0.0

func walk_to(point: Vector3) -> void:
	path = world.make_path(global_position, point)
	path_index = 0

func stop() -> void:
	path.clear()
	velocity = Vector3.ZERO

func face(point: Vector3, delta: float = 1.0) -> void:
	var d := point - global_position
	if d.length_squared() > 0.02:
		figure.rotation.y = lerp_angle(figure.rotation.y, atan2(-d.x, -d.z), minf(delta * 14.0, 1.0))

func start_attack(victim: Node3D) -> void:
	if dead or attack_clock > 0.0: return
	if team=="player" and (world.combat.channeling or world.combat.cast_clock>0 or world.combat.leap_clock>0):return
	if not world.line_of_sight(global_position,victim.global_position):return
	target = victim
	if team=="player":lunge_clock=.18
	stop()
	face(target.global_position)
	attack_clock = attack_total
	attack_did_hit = false
	play_animation("Attack",true)
	if team == "player": world.play_sound("swing", global_position, 0.92 + randf() * .17)

func receive_damage(amount: float, source: Node3D) -> void:
	if dead: return
	if team=="player" and world.combat.leap_clock>0:return
	hp = maxf(0.0, hp - amount)
	hurt_clock = 0.19
	world.damage_number(self, amount)
	world.hit_effect(global_position + Vector3.UP, team == "enemy")
	if team == "enemy" and is_instance_valid(source): target = source
	if hp <= 0.0:
		dead = true
		collision_layer=0
		collision_mask=1
		play_animation("Death",true)
		stop()
		attack_clock = 0.0
		world.on_death(self)

func _physics_process(delta: float) -> void:
	if world.paused: return
	age += delta
	if animation_player:animation_player.advance(delta)
	for buff in ["rally_buff","war_buff","berserk_buff","unstoppable_buff","slow_clock"]:set(buff,maxf(0,float(get(buff))-delta))
	if team=="enemy" and position.distance_squared_to(world.player.position)>1100 and position.z< -28:
		return
	if dead:
		if warning_ring:warning_ring.visible=false
		if not animation_player:
			figure.rotation.z = lerpf(figure.rotation.z, -1.48, delta * 6.0)
			figure.position.y = lerpf(figure.position.y, .2, delta * 5.0)
		return
	if team=="player" and (world.combat.leap_clock>0 or world.combat.cast_clock>0):return
	hurt_clock = maxf(0.0, hurt_clock - delta)
	if warning_ring:warning_ring.visible=attack_clock>attack_total*.52
	repath -= delta
	if attack_clock > 0.0:
		attack_clock = maxf(0.0, attack_clock - delta)
		if attack_clock < attack_total * .52 and not attack_did_hit:
			attack_did_hit = true
			if is_instance_valid(target) and not target.dead and global_position.distance_to(target.global_position) < 2.65:
				target.receive_damage(damage*world.combat.damage_multiplier(self), self)
				if elite and target.unstoppable_buff<=0:
					target.slow_clock=1.2
					target.slow_fraction=.3
				if team == "player": world.fury = minf(100.0, world.fury + world.basic_fury_generation)
	if team=="enemy" and is_instance_valid(target) and (target.position.z> -16 or position.distance_to(home_position)>16):
		target=null
		walk_to(home_position)
	if (team == "enemy" or team == "ally") and repath <= 0.0:
		repath = .65
		if not is_instance_valid(target) or target.dead:
			target = world.closest_opponent(self)
		if is_instance_valid(target):
			if global_position.distance_to(target.global_position) > 1.75: walk_to(target.global_position)
	if is_instance_valid(target) and target.team != "npc" and not target.dead:
		var dist := global_position.distance_to(target.global_position)
		if dist < (3.65 if team=="player" else 1.85):
			start_attack(target)
		elif team == "player" and repath <= 0.0:
			repath = .3
			walk_to(target.global_position)
	var moving := false
	velocity = Vector3.ZERO
	if attack_clock <= 0.0 and path_index < path.size():
		var diff := path[path_index] - global_position
		diff.y = 0
		if diff.length() < .19:
			path_index += 1
		else:
			var actual_speed: float = speed*world.combat.move_multiplier(self)
			if slow_clock>0 and unstoppable_buff<=0:actual_speed*=1.0-slow_fraction
			if team == "player" and is_instance_valid(target) and target.team == "enemy" and diff.length() > .3:
				actual_speed *= 1.2
			var separation := Vector3.ZERO
			for other in world.actors:
				if other==self or other.dead:continue
				var away: Vector3 = global_position-other.global_position
				away.y=0
				var distance := away.length()
				if distance>.01 and distance<1.0:separation+=away/distance*(1.0-distance)*2.4
			velocity = (diff.normalized()+separation).normalized() * actual_speed
			if not (team=="player" and world.combat.channeling):face(global_position + diff, delta)
			moving = true
	if team=="player" and lunge_clock>0 and is_instance_valid(target) and not target.dead:
		lunge_clock=maxf(0,lunge_clock-delta)
		var toward: Vector3=target.position-position
		toward.y=0
		velocity=toward.normalized()*minf(14,maxf(0,toward.length()-1.3)/delta)
	velocity+=push_velocity
	push_velocity=push_velocity.move_toward(Vector3.ZERO,delta*20)
	velocity.y = -3.0
	move_and_slide()
	if team == "player" and is_instance_valid(target) and target.team == "npc" and global_position.distance_to(target.global_position) < 2.6:
		stop()
		var person = target
		target = null
		world.talk(person)
	if animation_player:
		if team=="player" and world.combat.channeling:play_animation("Whirlwind")
		elif attack_clock<=0:play_animation("Run" if moving else "Idle")
		return
	# NPC articulated meshes retain their lightweight animation.
	var phase := age * (9.5 if team == "player" else 7.0)
	for i in range(2):
		var wave := sin(phase + i * PI) * (.48 if moving else .02)
		if hips[i]: hips[i].rotation.x = lerpf(hips[i].rotation.x, wave, delta * 14.0)
		if shoulders[i]:
			var angle := -wave * .85
			if attack_clock > 0.0:
				var t := 1.0 - attack_clock / attack_total
				angle = -sin(t * PI) * (2.3 if i == 1 else .7)
			elif kind == "charsi":
				angle = -maxf(0.0, sin(age * 2.2)) * 1.0 if i == 1 else .05
			shoulders[i].rotation.x = lerpf(shoulders[i].rotation.x, angle, delta * 20.0)
	if torso:
		torso.position.y = base_y + (absf(sin(phase)) * .055 if moving else sin(age * 2.0) * .013)
		torso.rotation.x = -.10 if hurt_clock > 0.0 else 0.0

func find_skeleton(node: Node) -> Skeleton3D:
	if node is Skeleton3D:return node
	for child in node.get_children():
		var found := find_skeleton(child)
		if found:return found
	return null

func play_animation(label: String, restart: bool=false) -> void:
	if not animation_player or not animation_names.has(label):return
	if current_animation==label and not restart:return
	current_animation=label
	animation_player.play(animation_names[label],.12)
