extends Node

const IDS := ["lunging_strike", "whirlwind", "rallying_cry", "war_cry", "leap", "wrath_of_the_berserker"]
const NAMES := ["突刺", "旋风斩", "集结呐喊", "战吼", "腾空斩", "狂战士之怒"]
var world: Node3D
var data: Dictionary
var cooldowns := [0.0,0.0,0.0,0.0,0.0,0.0]
var channeling := false
var whirlwind_tick := 0.0
var channel_repath := 0.0
var cast_clock := 0.0
var cast_animation := "Rally"
var leap_clock := 0.0
var leap_from := Vector3.ZERO
var leap_to := Vector3.ZERO
var leap_duration := 1.0666667
var leap_takeoff := .18
var leap_land := .78
var leap_did_land := false
var spin_velocity := 0.0
var weapon_damage := 32.0
var effects: Array[Dictionary] = []
var spinning_blades: MeshInstance3D
var berserk_light: OmniLight3D
var active_unlocked := [true,true,true,true,true,true]

func _ready() -> void:
	data=JSON.parse_string(FileAccess.get_file_as_string("res://data/skill_reference.json")).skills
	var profile: Dictionary = world.player.animation_profile
	leap_duration = float(profile.get("leap_duration", leap_duration))
	leap_takeoff = float(profile.get("leap_takeoff_seconds", leap_takeoff))
	leap_land = float(profile.get("leap_land_seconds", leap_land))
	spinning_blades=arc_mesh(2.45,Color("e9d4a1"),true)
	world.add_child(spinning_blades)
	spinning_blades.visible=false
	berserk_light=OmniLight3D.new()
	berserk_light.light_color=Color("ec6d29")
	berserk_light.omni_range=4.5
	berserk_light.light_energy=1.6
	berserk_light.visible=false
	world.player.add_child(berserk_light)
	berserk_light.position.y=1.4

func skill(i: int) -> Dictionary:
	return data[IDS[i]]

func damage_multiplier(actor: Node3D) -> float:
	var multiplier := 1.0
	if actor.war_buff>0:multiplier*=1.0+actor.war_bonus
	if actor.berserk_buff>0:multiplier*=1.25
	return multiplier

func move_multiplier(actor: Node3D) -> float:
	return 1.0+(actor.rally_bonus if actor.rally_buff>0 else 0.0)+(.15 if actor.berserk_buff>0 else 0.0)

func cancel() -> void:
	channeling=false
	spin_velocity=0.0
	spinning_blades.visible=false

func cast(i: int, point: Vector3) -> bool:
	var p = world.player
	if world.paused or p.dead or not world.dialog.is_empty() or leap_clock>0 or cast_clock>0:return false
	if i<0 or i>=6 or not active_unlocked[i]:return false
	if cooldowns[i]>.01:
		world.toast(NAMES[i]+" · 冷却剩余 "+str(ceili(cooldowns[i]))+" 秒")
		return false
	if i==0:
		var enemy = world.hover
		if is_instance_valid(enemy) and enemy.team=="enemy" and not enemy.dead:
			cancel()
			p.target=enemy
			p.walk_to(enemy.position)
			return true
		return false
	var s := skill(i)
	var cost := float(s.get("fury_cost",0.0))
	if i==1:cost=float(s.fury_per_second)*float(s.tick_seconds)
	if world.fury<cost:
		world.toast("怒气不足 · 突刺与腾空斩可以产生怒气")
		return false
	if i==4:
		# Limit leap to a reachable connected point; never land inside props or cross the camp wall.
		var direction: Vector3 = point-p.position
		direction.y=0
		if direction.length()<.7:
			world.toast("腾空斩 · 请指向更远的地面")
			return false
		var desired: Vector3=p.position+direction.limit_length(10.0)
		var route: PackedVector3Array=world.make_path(p.position,desired)
		if route.is_empty():return false
		leap_to=route[-1]
		var travel := 0.0
		var prev: Vector3=p.position
		for q in route:
			travel+=prev.distance_to(q)
			prev=q
		if leap_to.distance_to(desired)>1.0 or travel>p.position.distance_to(leap_to)*1.6+2.0:
			world.toast("落点被阻挡 · 请指向开阔地面")
			return false
	cancel()
	p.stop()
	p.target=null
	p.attack_clock=0
	p.lunge_clock=0
	p.reaction_clock=0
	if i!=1:world.fury-=cost
	cooldowns[i]=float(s.get("cooldown_seconds",0.0))
	match i:
		1:
			channeling=true
			whirlwind_tick=float(s.tick_seconds)
			channel_repath=0
			p.play_animation("Whirlwind", true)
		2:
			p.rally_buff=float(s.duration_seconds)
			p.rally_bonus=float(s.movement_speed_bonus)
			for a in world.actors:
				if a.team=="ally" and not a.dead and a.position.distance_to(p.position)<8:
					a.rally_buff=p.rally_buff*.5
					a.rally_bonus=p.rally_bonus*.5
			shout("Rally",Color("88c4d1"),8.0)
		3:
			p.war_buff=float(s.duration_seconds)
			p.war_bonus=float(s.damage_bonus)
			for a in world.actors:
				if a.team=="ally" and not a.dead and a.position.distance_to(p.position)<8:
					a.war_buff=p.war_buff*.5
					a.war_bonus=p.war_bonus*.5
			shout("WarCry",Color("e09d52"),8.0)
		4:
			leap_from=p.position
			leap_clock=leap_duration
			leap_did_land=false
			p.face(leap_to)
			p.play_animation("Leap", true)
			pulse(p.position,Color("b29c73"),1.5,.4)
			world.play_sound("leap",p.position)
		5:
			p.berserk_buff=float(s.duration_seconds)
			p.unstoppable_buff=float(s.duration_seconds)
			p.slow_clock=0
			shout("Berserk",Color("f27432"),5.0)
			for a in enemies_in(p.position,4.0):
				var away: Vector3=(a.position-p.position).normalized()
				a.push_velocity=away*8
	world.toast(NAMES[i]+(" · 按住右键持续引导" if i==1 else ""))
	return true

func shout(animation: String, color: Color, radius: float) -> void:
	cast_clock=world.player.clip_duration(animation, .8)
	cast_animation=animation
	world.player.play_animation(animation, true)
	pulse(world.player.position,color,radius,.65)
	pulse(world.player.position+Vector3.UP*.15,color,radius*.75,.5)
	world.play_sound("shout",world.player.position,.72 if animation=="Berserk" else 1.0)

func enemies_in(point: Vector3, radius: float) -> Array:
	return world.actors.filter(func(a):return a.team=="enemy" and not a.dead and a.position.distance_to(point)<radius)

func area_damage(point: Vector3, radius: float, coefficient: float, slow: bool=false) -> int:
	var hit := 0
	for a in enemies_in(point,radius):
		a.receive_damage(weapon_damage*coefficient*damage_multiplier(world.player),world.player)
		if slow and not a.dead:
			a.slow_clock=float(skill(4).slow_duration_seconds)
			a.slow_fraction=float(skill(4).slow_fraction)
		hit+=1
	return hit

func _physics_process(delta: float) -> void:
	if world.paused:return
	var p=world.player
	for i in range(6):cooldowns[i]=maxf(0,cooldowns[i]-delta)
	cast_clock=maxf(0,cast_clock-delta)
	berserk_light.visible=p.berserk_buff>0 and not p.dead
	if p.dead:
		cancel()
		if leap_clock>0:p.position=leap_from
		leap_clock=0
		cast_clock=0
		return
	if leap_clock>0:
		leap_clock=maxf(0,leap_clock-delta)
		var elapsed := leap_duration-leap_clock
		var t := clampf((elapsed-leap_takeoff)/(leap_land-leap_takeoff), 0.0, 1.0)
		# Anticipation stays on the ground; the landing pose owns the recovery lock.
		p.position=leap_from.lerp(leap_to,t)+Vector3.UP*(4.0*t*(1.0-t)*3.0)
		if elapsed>=leap_land and not leap_did_land:
			leap_did_land=true
			p.position=leap_to
			world.fury=minf(100,world.fury+float(skill(4).fury_generation))
			area_damage(p.position,3.4,float(skill(4).damage_coefficient),true)
			pulse(p.position,Color("dec497"),3.4,.45)
			debris(p.position,22)
			world.camera_shake=.20
			world.play_sound("slam",p.position)
		return
	if not channeling:return
	if world.fury<=.01:
		cancel()
		p.stop()
		world.toast("怒气耗尽 · 用突刺继续积攒怒气")
		return
	world.fury=maxf(0,world.fury-float(skill(1).fury_per_second)*delta)
	whirlwind_tick-=delta
	channel_repath-=delta
	if whirlwind_tick<=0:
		whirlwind_tick+=float(skill(1).tick_seconds)
		area_damage(p.position,2.75,float(skill(1).damage_coefficient))
		world.play_sound("swing",p.position,.72)
	if channel_repath<=0:
		channel_repath=.15
		var point: Vector3=world.mouse_ground()
		if point.distance_to(p.position)>1:p.walk_to(point)
		else:p.stop()
	spin_velocity=move_toward(spin_velocity, 15.5, delta*100.0)
	p.figure.rotation.y=wrapf(p.figure.rotation.y+delta*spin_velocity, -PI, PI)
	spinning_blades.visible=true
	spinning_blades.position=p.position+Vector3.UP*.65
	spinning_blades.rotation.y+=delta*18

func _process(delta: float) -> void:
	if world.paused:return
	for e in effects:
		e.ttl-=delta
		var t: float = 1.0-e.ttl/e.duration
		if e.has("velocity"):
			e.mesh.position+=e.velocity*delta
			e.velocity.y-=12*delta
			e.mesh.rotate_x(delta*6)
		else:e.mesh.scale=Vector3.ONE*maxf(.03,t)*e.radius
		e.mesh.material_override.albedo_color.a=maxf(0,(1-t)*.85)
		if e.ttl<=0:e.mesh.queue_free()
	effects=effects.filter(func(e):return e.ttl>0)

func pulse(point: Vector3,color: Color,radius: float,duration: float) -> void:
	var m := arc_mesh(1.0,color,false)
	world.add_child(m)
	m.position=point+Vector3.UP*.08
	m.scale=Vector3.ONE*.05
	effects.append({"mesh":m,"ttl":duration,"duration":duration,"radius":radius})

func arc_mesh(radius: float,color: Color,slash: bool) -> MeshInstance3D:
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(96):
		if slash and i%48>31:continue
		var a := i*TAU/96
		var b := (i+1)*TAU/96
		var width := .22*(1.0-float(i%48)/48) if slash else .035
		var p1 := Vector3(cos(a)*radius,0,sin(a)*radius)
		var p2 := Vector3(cos(b)*radius,0,sin(b)*radius)
		var p3 := Vector3(cos(a)*(radius-width),0,sin(a)*(radius-width))
		var p4 := Vector3(cos(b)*(radius-width),0,sin(b)*(radius-width))
		for v in [p1,p3,p2,p2,p3,p4]:mesh.surface_add_vertex(v)
	mesh.surface_end()
	var m := MeshInstance3D.new()
	m.mesh=mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color=color
	mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode=BaseMaterial3D.CULL_DISABLED
	m.material_override=mat
	m.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return m

func debris(point: Vector3,count: int) -> void:
	var rock := PrismMesh.new()
	rock.size=Vector3(.09,.13,.10)
	for i in range(count):
		var a := randf()*TAU
		var m := MeshInstance3D.new()
		m.mesh=rock
		var mat := StandardMaterial3D.new()
		mat.albedo_color=Color("aa8860")
		mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
		m.material_override=mat
		m.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		world.add_child(m)
		m.position=point+Vector3(cos(a),.1,sin(a))*randf_range(.5,1.7)
		effects.append({"mesh":m,"ttl":.7,"duration":.7,"velocity":Vector3(cos(a)*4,randf_range(2,5),sin(a)*4)})
