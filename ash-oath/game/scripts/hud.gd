extends Control

var world: Node3D
var serif: SystemFont
var sans: SystemFont
var gold := Color("c3aa70")
var ivory := Color("dfd5bb")
var dim := Color("9f9c8a")
var ink := Color(.025,.034,.035,.94)

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	serif = SystemFont.new()
	serif.font_names = PackedStringArray(["Songti SC","Noto Serif CJK SC","Georgia"])
	sans = SystemFont.new()
	sans.font_names = PackedStringArray(["PingFang SC","Noto Sans CJK SC","Arial"])

func text(p: Vector2, value: String, size_px: int = 18, c: Color = Color("dfd5bb"), center: bool = false, font: Font = null) -> void:
	if font == null: font=serif
	if center:p.x-=font.get_string_size(value,HORIZONTAL_ALIGNMENT_LEFT,-1,size_px).x*.5
	draw_string(font,p+Vector2(1,2),value,HORIZONTAL_ALIGNMENT_LEFT,-1,size_px,Color(0,0,0,.7))
	draw_string(font,p,value,HORIZONTAL_ALIGNMENT_LEFT,-1,size_px,c)

func panel(r: Rect2, c: Color = Color(.025,.034,.035,.94)) -> void:
	draw_rect(r,c)
	draw_rect(r,Color(.48,.41,.27,.65),false,1)
	for p in [r.position,r.position+Vector2(r.size.x,0),r.end,r.position+Vector2(0,r.size.y)]:
		var dx := 1.0 if p.x==r.position.x else -1.0
		var dy := 1.0 if p.y==r.position.y else -1.0
		draw_line(p,p+Vector2(14*dx,0),gold,2)
		draw_line(p,p+Vector2(0,14*dy),gold,2)

func diamond(p: Vector2,r: float,c: Color) -> void:
	draw_colored_polygon(PackedVector2Array([p+Vector2(0,-r),p+Vector2(r,0),p+Vector2(0,r),p+Vector2(-r,0)]),c)

func wrap_lines(value: String, width: float, px: int) -> PackedStringArray:
	var lines := PackedStringArray()
	for para in value.split("\n"):
		var line := ""
		for ch in para:
			if serif.get_string_size(line+ch,HORIZONTAL_ALIGNMENT_LEFT,-1,px).x>width:
				lines.append(line)
				line=""
			line+=ch
		lines.append(line)
	return lines

func _draw() -> void:
	if not is_instance_valid(world.player):return
	var w := size.x
	var h := size.y
	# Quiet cinematic edge shade; the play field remains the dominant surface.
	for i in range(38):
		var a := .011*(1-float(i)/38)
		draw_rect(Rect2(i*3,0,w-i*6,h),Color(0,0,0,a),false,6)
	for i in range(16):
		draw_rect(Rect2(0,i*5,w,5),Color(.01,.02,.025,.40*(1.0-i/16.0)))
	text(Vector2(43,49),"A S H E N   O A T H",20,gold)
	text(Vector2(43,83),"灰 烬 誓 约",27,ivory)
	draw_line(Vector2(44,101),Vector2(207,101),Color(.65,.52,.32,.55))
	text(Vector2(44,125),"野蛮人  /  第一幕",13,dim,false,sans)
	text(Vector2(w/2,39),"第 一 幕 · 目 盲 之 眼",14,gold,true)
	text(Vector2(w/2,75),world.area,29,ivory,true)
	draw_line(Vector2(w/2-140,93),Vector2(w/2-12,93),Color(.64,.54,.37,.65))
	draw_line(Vector2(w/2+12,93),Vector2(w/2+140,93),Color(.64,.54,.37,.65))
	diamond(Vector2(w/2,93),4,gold)
	if world.portrait_mode:
		panel(Rect2(w-348,h*.3,290,245))
		text(Vector2(w-320,h*.3+45),"北境的誓约者",27,gold)
		text(Vector2(w-320,h*.3+85),"野蛮人 · 双持武器",16,ivory)
		text(Vector2(w-320,h*.3+122),"战斧 / 单手剑 / 背负巨剑",14,dim)
		text(Vector2(w-320,h*.3+160),"六项战技已装备",16,ivory)
		text(Vector2(w-320,h*.3+200),"按住鼠标中键拖动 · 环绕观察",13,dim)
		text(Vector2(w/2,h-45),"C  返回旅途",18,gold,true)
		return
	draw_map(Vector2(w-132,135))
	var qx := w-306
	draw_rect(Rect2(qx-18,265,300,170 if world.kills==0 else 190),Color(.02,.028,.027,.62))
	text(Vector2(qx,286),"任 务 日 志",13,gold)
	draw_line(Vector2(qx,298),Vector2(w-38,298),Color(.60,.50,.32,.4))
	var title := "远道而来的旅人" if world.quest==0 else "邪恶洞窟"
	text(Vector2(qx,330),title,23,ivory)
	diamond(Vector2(qx+4,357),3,gold)
	var objective := "与女祭司阿卡拉交谈" if world.quest==0 else "穿过北门，寻找邪恶洞窟" if world.quest==1 else "邪恶洞窟已发现"
	text(Vector2(qx+18,363),objective,16,ivory,false,sans)
	text(Vector2(qx+18,391),"营地内可与五位旅人交谈" if world.quest==0 else "鲜血荒地 · 北方小径" if world.quest==1 else "洞窟深处将在后续章节开放",13,dim,false,sans)
	if world.kills>0:text(Vector2(qx+18,419),"荒地击杀  ·  "+str(world.kills)+" / "+str(world.monster_total),13,dim,false,sans)
	# NPC names belong to their characters in the world, rather than a roster UI.
	for actor in world.actors:
		if actor==world.player or actor.dead or world.camera.is_position_behind(actor.position):continue
		var p: Vector2 = world.camera.unproject_position(actor.position+Vector3.UP*2.53)
		if p.x<22 or p.x>w-22 or p.y<110 or p.y>h-170:continue
		if p.x>w-330 and p.y<440:continue
		if actor.team=="npc":
			text(p,actor.display_name,16,gold if actor==world.hover else ivory,true)
			if actor==world.hover:text(p+Vector2(0,-24),"点击交谈",12,gold,true,sans)
			if actor.display_name=="阿卡拉" and world.quest==0:
				diamond(p+Vector2(0,-39),9,Color("d3b772"))
				text(p+Vector2(0,-34),"!",15,ink,true,sans)
		elif actor==world.hover or actor.hp<actor.max_hp:
			if actor==world.hover:text(p,actor.display_name,14,Color("d7b7a1") if actor.team=="enemy" else ivory,true)
			draw_rect(Rect2(p+Vector2(-25,8),Vector2(50,4)),Color(.04,.025,.02,.9))
			draw_rect(Rect2(p+Vector2(-25,8),Vector2(50*actor.hp/actor.max_hp,4)),Color("943e30") if actor.team=="enemy" else Color("849886"))
	for n in world.numbers:
		var p: Vector2 = world.camera.unproject_position(n.point)
		p.y-=(.9-n.ttl)*35
		text(p,n.value,22,Color(1,.80,.46,n.ttl/.9) if n.enemy else Color(.96,.31,.21,n.ttl/.9),true,sans)
	if world.notification_clock>0 and world.dialog.is_empty():
		var a := minf(1,world.notification_clock)
		text(Vector2(w/2,158),world.notice_text,20,Color(.9,.82,.64,a),true)
	# Forged action bar.
	var cx := w/2
	var by := h-93
	panel(Rect2(cx-353,by-51,706,115),Color(.025,.03,.029,.93))
	draw_line(Vector2(cx-335,by-46),Vector2(cx+335,by-46),Color(.47,.37,.23,.45))
	for i in range(6):
		var bx := cx-241+i*81
		var r := Rect2(bx,by-34,67,68)
		var active: bool=(i==1 and world.combat.channeling) or (i==2 and world.player.rally_buff>0) or (i==3 and world.player.war_buff>0) or (i==5 and world.player.berserk_buff>0)
		var cd: float=world.combat.cooldowns[i]
		panel(r,Color(.20,.15,.08,1) if active else Color(.07,.085,.08,1))
		draw_skill_icon(i,Vector2(bx+33,by),gold if cd<=0 else dim)
		if cd>0:
			var fraction: float=cd/float(world.combat.skill(i).cooldown_seconds)
			draw_rect(Rect2(bx,by-34,67,68*fraction),Color(0,0,0,.72))
			text(Vector2(bx+33,by+7),str(ceili(cd)),23,ivory,true,sans)
		if active:draw_rect(r,Color("e6c77e"),false,2)
		text(Vector2(bx+33,by-40),["鼠标左键","按住右键","1","2","3","4"][i],11,gold,true,sans)
		text(Vector2(bx+33,by+52),world.combat.NAMES[i],11,ivory,true,sans)
		if r.has_point(get_local_mouse_position()):draw_skill_tooltip(i,Vector2(cx-255,by-278))
	var buffs := []
	if world.player.rally_buff>0:buffs.append("集结  "+str(ceili(world.player.rally_buff))+"s")
	if world.player.war_buff>0:buffs.append("战吼  "+str(ceili(world.player.war_buff))+"s")
	if world.player.berserk_buff>0:buffs.append("狂暴 · 不可阻挡  "+str(ceili(world.player.berserk_buff))+"s")
	if buffs.size()>0:text(Vector2(cx,by-78),"    /    ".join(buffs),15,gold,true,sans)
	draw_orb(Vector2(cx-415,by+1),55,world.player.hp/world.player.max_hp,Color("842d26"),str(int(world.player.hp))+" / "+str(int(world.player.max_hp)),"生命")
	draw_orb(Vector2(cx+415,by+1),55,world.fury/100.0,Color("b36d25"),str(int(world.fury))+" / 100","怒气")
	text(Vector2(cx, h-16),"左键移动 / 突刺   ·   右键旋风斩   ·   1—4 技能   ·   C 人物近景",13,dim,true,sans)
	text(Vector2(34,h-30),"Q  药剂 "+str(world.potions)+" / 4     Esc  暂停",13,ivory,false,sans)
	text(Vector2(w-32,h-30),"",13,dim)
	text(Vector2(w-236,h-30),"M  "+("声音关闭" if world.muted else "环境音开启")+"    F11  全屏",12,dim,false,sans)
	if not world.dialog.is_empty():draw_dialog(cx,by)
	if world.paused or world.player.dead:
		draw_rect(Rect2(0,0,w,h),Color(.01,.02,.025,.66))
		panel(Rect2(cx-220,h/2-100,440,210))
		text(Vector2(cx,h/2-42),"旅途暂停" if world.paused else "你倒在了荒野",30,gold,true)
		text(Vector2(cx,h/2),"炉火仍为你燃烧。",18,ivory,true)
		panel(Rect2(cx-100,h/2+27,200,46),Color(.16,.13,.085,.95))
		text(Vector2(cx,h/2+57),"继续旅程" if world.paused else "返回营地",18,gold,true)

func draw_orb(p: Vector2, radius: float, value: float, c: Color, label: String, caption: String) -> void:
	draw_circle(p,radius+9,Color("141a19"))
	draw_arc(p,radius+8,0,TAU,72,Color("756140"),3,true)
	draw_arc(p,radius+3,0,TAU,72,Color("b39c65"),1,true)
	draw_circle(p,radius,Color("221a18"))
	for i in range(24):
		var t := float(i)/24
		var shade := c.lightened(t*.18).darkened((1-value)*.74)
		draw_circle(p+Vector2(-t*7,-t*8),radius*(1-t*.85),shade)
	draw_arc(p,radius-2,-PI/2,-PI/2+TAU*clampf(value,.001,1),72,c.lightened(.42),2,true)
	draw_arc(p+Vector2(-7,-8),radius*.70,3.45,4.15,16,Color(.94,.88,.74,.35),3,true)
	diamond(p+Vector2(0,-radius-9),4,gold)
	text(p+Vector2(0,6),label,15,Color("f3e2ca"),true,sans)
	text(p+Vector2(0,radius+28),caption,13,gold,true)

func draw_map(p: Vector2) -> void:
	draw_circle(p,87,Color(.025,.044,.040,.88))
	draw_arc(p,87,0,TAU,96,Color("998258"),1.5,true)
	draw_arc(p,81,0,TAU,96,Color(.48,.43,.29,.35),1,true)
	var origin := Vector2(world.player.position.x,world.player.position.z)*2.35
	var sc := 2.35
	for a in range(80):
		var ang := a*TAU/80
		var q := Vector2(cos(ang)*20,(1+sin(ang)*19))*sc-origin
		if q.length()>78:continue
		if q.y<-35 and absf(q.x)<9:continue
		draw_circle(p+q,1.15,Color("716c51"))
	draw_line(p+Vector2(0,-72),p+Vector2(0,72),Color(.39,.36,.25,.4),2)
	draw_line(p+Vector2(-37,7),p+Vector2(37,7),Color(.39,.36,.25,.5),3)
	for a in world.actors:
		if a.dead:continue
		var q := Vector2(a.position.x,a.position.z)*sc-origin
		if q.length()>77:continue
		if a==world.player:diamond(p+q,4,ivory)
		elif a.team=="npc":diamond(p+q,2.6,gold)
		elif a.team=="enemy":draw_circle(p+q,2,Color("a1503d"))
		else:draw_circle(p+q,2,Color("8daba0"))
	text(p+Vector2(0,-93),"N",12,gold,true,sans)
	text(p+Vector2(0,115),"鲜血荒地  ↑",13,dim,true,sans)

func draw_dialog(cx: float, by: float) -> void:
	var r := Rect2(cx-405,by-333,810,244)
	panel(r,Color(.025,.034,.033,.98))
	var npc = world.selected_npc
	text(r.position+Vector2(28,41),npc.display_name,27,gold)
	text(r.position+Vector2(140,40),npc.role_name,13,dim,false,sans)
	draw_line(r.position+Vector2(27,57),r.position+Vector2(783,57),Color(.53,.43,.27,.48))
	var lines := wrap_lines(world.dialog,750,18)
	for i in range(lines.size()):text(r.position+Vector2(28,86+i*27),lines[i],18,ivory)
	var button := Rect2(r.end-Vector2(199,52),Vector2(173,34))
	panel(button,Color(.17,.14,.087,1))
	text(button.position+Vector2(86,23),"接受委托" if npc.display_name=="阿卡拉" and world.quest==0 else "愿你平安",16,gold,true)
	text(r.position+Vector2(28,225),"Esc  结束交谈",12,dim,false,sans)

func _input(event: InputEvent) -> void:
	if not event is InputEventMouseButton or not event.pressed or event.button_index!=MOUSE_BUTTON_LEFT:return
	var p: Vector2 = event.position
	var cx := size.x/2
	var by := size.y-93
	if world.paused or world.player.dead:
		if Rect2(cx-100,size.y/2+27,200,46).has_point(p):
			if world.player.dead: get_tree().reload_current_scene()
			else:world.paused=false
		get_viewport().set_input_as_handled()
	elif not world.dialog.is_empty():
		var r := Rect2(cx-405,by-333,810,244)
		if Rect2(r.end-Vector2(199,52),Vector2(173,34)).has_point(p):
			if world.selected_npc.display_name=="阿卡拉" and world.quest==0:world.accept_quest()
			else:world.close_dialog()
		get_viewport().set_input_as_handled()
	elif p.y>size.y-164 or p.x>size.x-310 and p.y<440:
		get_viewport().set_input_as_handled()

func draw_skill_icon(i: int, p: Vector2, c: Color) -> void:
	match i:
		0:
			draw_line(p+Vector2(-15,21),p+Vector2(14,-20),c,3,true)
			draw_colored_polygon(PackedVector2Array([p+Vector2(5,-14),p+Vector2(23,-22),p+Vector2(26,-7),p+Vector2(11,1)]),c)
		1:
			for j in range(3):
				var a := j*TAU/3
				draw_arc(p,21-j*3,a,a+PI*1.4,25,c,2,true)
			diamond(p,4,c)
		2,3:
			var flip := -1.0 if i==2 else 1.0
			var pts := PackedVector2Array([p+Vector2(-18,12),p+Vector2(-3,4),p+Vector2(6,-14),p+Vector2(14,-20),p+Vector2(12,-3),p+Vector2(2,11),p+Vector2(-12,19)])
			draw_polyline(pts,c,2,true)
			for j in range(3):draw_arc(p+Vector2(11,-14),8+j*6,-.7,.5,12,c,1.5,true)
			if flip>0:draw_line(p+Vector2(-18,-18),p+Vector2(-10,-10),c,2,true)
		4:
			draw_arc(p+Vector2(-5,8),21,PI,TAU,24,c,2,true)
			draw_colored_polygon(PackedVector2Array([p+Vector2(9,-8),p+Vector2(21,8),p+Vector2(21,-6)]),c)
			for j in range(3):draw_line(p+Vector2(-21+j*17,17),p+Vector2(-17+j*17,23),c,2,true)
		5:
			draw_circle(p+Vector2(0,-8),8,c,false,2,true)
			draw_polyline(PackedVector2Array([p+Vector2(-23,-21),p+Vector2(-13,-6),p+Vector2(-7,-12)]),c,3,true)
			draw_polyline(PackedVector2Array([p+Vector2(23,-21),p+Vector2(13,-6),p+Vector2(7,-12)]),c,3,true)
			draw_polyline(PackedVector2Array([p+Vector2(-17,19),p+Vector2(-10,3),p+Vector2(0,8),p+Vector2(10,3),p+Vector2(17,19)]),c,3,true)

func draw_skill_tooltip(i: int, p: Vector2) -> void:
	var descriptions := [
		"向目标逼近并攻击。命中造成 90% 武器伤害，产生 12 点怒气。",
		"按住右键旋转攻击周围敌人，并朝鼠标指向移动。每秒消耗 15 点怒气，单次命中造成 72% 武器伤害。松开右键结束。",
		"消耗 35 点怒气。移动速度提高 20%，持续 4 秒。附近罗格卫队获得一半效果。",
		"伤害提高 7.5%，持续 4 秒。附近罗格卫队获得一半效果。冷却 25 秒。",
		"跃向鼠标位置，落地造成 55% 武器伤害，使敌人减速 70%，持续 3 秒。产生 15 点怒气，冷却 17 秒。",
		"击退附近敌人，获得狂暴与不可阻挡，持续 10 秒。狂暴提高 25% 伤害、15% 移动速度。冷却 90 秒。"]
	panel(Rect2(p,Vector2(510,205)))
	text(p+Vector2(23,36),world.combat.NAMES[i],23,gold)
	var lines := wrap_lines(descriptions[i],462,16)
	for j in range(lines.size()):text(p+Vector2(23,72+j*26),lines[j],16,ivory)
	text(p+Vector2(23,183),"已装备  ·  基础技能",12,dim,false,sans)
