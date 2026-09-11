"""Continuous 60 Hz clips with planted-foot IK and shared gameplay timing.

Executed after equipment construction by build_barbarian.py.
"""
def ease(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def curve(t, keys):
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return x+(y-x)*ease((t-a)/(b-a))
    return keys[-1][1]

def rot(name,axis,angle):
    rest_rotate(name,axis,angle)

def root_height(z):
    # Bone-local Z is not world up in the MakeHuman rig.
    pb=rig.pose.bones['root']
    pb.location=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,z))

def world_rotation(pb, q):
    rest=pb.bone.matrix_local
    if pb.parent:rest=pb.parent.matrix@pb.parent.bone.matrix_local.inverted()@rest
    pb.rotation_quaternion=rest.to_quaternion().inverted()@q

def solve_leg(side,target,roll=0):
    """Two effective segments span the rig's twist bones. Keep the knee forward."""
    bpy.context.view_layer.update()
    thigh=rig.pose.bones['upperleg01.'+side]
    shin=rig.pose.bones['lowerleg01.'+side]
    foot=rig.pose.bones['foot.'+side]
    hip=thigh.head.copy();knee=shin.head.copy();ankle=foot.head.copy()
    a=(knee-hip).length;b=(ankle-knee).length
    delta=target-hip;distance=min(delta.length,a+b-.001)
    direction=delta.normalized()
    pole=Vector((0,-1,0));pole=(pole-direction*pole.dot(direction)).normalized()
    along=(a*a+distance*distance-b*b)/(2*distance)
    desired_knee=hip+direction*along+pole*math.sqrt(max(0,a*a-along*along))
    q=(knee-hip).rotation_difference(desired_knee-hip)
    world_rotation(thigh,q@thigh.matrix.to_quaternion())
    bpy.context.view_layer.update()
    q=(foot.head-shin.head).rotation_difference(target-shin.head)
    world_rotation(shin,q@shin.matrix.to_quaternion())
    bpy.context.view_layer.update()
    world_rotation(foot,Quaternion((1,0,0),roll)@foot.bone.matrix_local.to_quaternion())

def close_hands():
    for side,sign in [('L',1),('R',-1)]:
        axis=finger_axes[side]
        for finger in range(2,6):
            for part,angle in [(1,1.05),(2,1.27),(3,.87)]:rot(f'finger{finger}-{part}.{side}',axis,-sign*angle)
        rot('finger1-1.'+side,(0,0,1),sign*.42)
        rot('finger1-2.'+side,axis,-sign*.65)
        rot('finger1-3.'+side,axis,-sign*.65)

def ready():
    for pb in rig.pose.bones:
        pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion();pb.location=(0,0,0)
    for side,sign in [('L',1),('R',-1)]:
        rot('upperarm01.'+side,(0,1,0),sign*.34)
        rot('upperarm01.'+side,(1,0,0),.08)
        rot('lowerarm01.'+side,(1,0,0),-.23)
    close_hands()

# One neutral wrist alignment. Every clip retains it, so equipment never drifts.
ready();bpy.context.view_layer.update();wrist_ready={}
for side,sign in [('L',1),('R',-1)]:
    pb=rig.pose.bones['wrist.'+side]
    rest=pb.bone.matrix_local.to_quaternion()
    current=pb.matrix.to_quaternion()@rest.inverted()@grip_frames[side][1]
    desired=Vector((sign*.10,-.13,1)).normalized()
    world_rotation(pb,current.rotation_difference(desired)@pb.matrix.to_quaternion())
    wrist_ready[side]=pb.rotation_quaternion.copy()

def pose(kind,t):
    ready()
    for side in ['L','R']:rig.pose.bones['wrist.'+side].rotation_quaternion=wrist_ready[side].copy()
    feet={side:rig.data.bones['foot.'+side].head_local.copy() for side in ['L','R']}
    rolls={'L':0,'R':0};height=-.045
    if kind=='Idle':
        breath=math.sin(t*math.tau)
        height+=.006*breath
        rot('spine02',(1,0,0),.014*breath)
        rot('spine01',(0,1,0),.006*math.sin(t*math.tau))
        rot('head',(1,0,0),-.008*breath)
        for side in ['L','R']:rot('lowerarm01.'+side,(1,0,0),-.008*breath)
    elif kind=='Run':
        phi=t*math.tau;height=-.17+.020*math.cos(phi*2)
        rot('spine04',(1,0,0),.10);rot('spine02',(1,0,0),.10)
        rot('spine02',(0,0,1),-.10*math.sin(phi));rot('head',(1,0,0),-.14)
        for side,sign,phase in [('L',1,0),('R',-1,.5)]:
            u=(t+phase)%1
            # Smooth periodic paths keep foot and knee velocity continuous at
            # toe-off and contact; extra hip clearance avoids an IK knee snap.
            feet[side].y-=.48*math.cos(u*math.tau)
            feet[side].z+=.23*max(0,-math.sin(u*math.tau))**2
            rolls[side]=-.10*math.cos(u*math.tau)+.10*max(0,-math.sin(u*math.tau))**2
            swing=math.sin(phi)*sign
            rot('upperarm01.'+side,(1,0,0),-.34*swing)
            rot('lowerarm01.'+side,(1,0,0),-.45-.09*swing)
    elif kind=='Attack':
        wind=curve(t,[(0,0),(.27,1),(.49,-.34),(.64,-.23),(1,0)])
        strike=curve(t,[(0,0),(.28,0),(.49,1),(.65,.8),(1,0)])
        rot('upperarm01.R',(1,0,0),-1.55*wind+.38*strike)
        rot('upperarm01.R',(0,0,1),-.23*wind)
        rot('lowerarm01.R',(1,0,0),-.30*wind)
        rot('upperarm01.L',(1,0,0),-.30*strike)
        rot('spine02',(0,0,1),.24*wind-.16*strike)
        rot('spine03',(1,0,0),-.08*wind+.15*strike)
        step=curve(t,[(0,0),(.28,.6),(.50,1),(.74,1),(1,0)])
        feet['L'].y-=.20*step;feet['R'].y+=.10*step;height-=.035*step
    elif kind=='Whirlwind':
        height=-.09+.013*math.cos(t*math.tau*2)
        rot('spine03',(1,0,0),.08)
        for side,sign in [('L',1),('R',-1)]:
            rot('upperarm01.'+side,(0,1,0),-sign*.97)
            rot('lowerarm01.'+side,(1,0,0),.12)
            rot('wrist.'+side,(0,1,0),sign*.34)
            feet[side].y+=math.sin(t*math.tau)*sign*.17
            feet[side].z+=max(0,math.cos(t*math.tau)*sign)*.055
    elif kind in ['Rally','WarCry','Berserk']:
        charge=curve(t,[(0,0),(.25,-.25),(.48,1),(.68,.92),(1,0)])
        strength={'Rally':.75,'WarCry':1.0,'Berserk':1.3}[kind]
        height-=.025*max(0,charge)
        rot('spine03',(1,0,0),-.14*charge)
        rot('head',(1,0,0),-.18*charge)
        # Jaw articulation makes the cry readable in portrait mode.
        if 'jaw' in rig.pose.bones:rot('jaw',(1,0,0),.18*max(0,charge))
        for side,sign in [('L',1),('R',-1)]:
            rot('upperarm01.'+side,(0,1,0),-sign*.40*charge*strength)
            rot('upperarm01.'+side,(1,0,0),-.62*charge*strength)
            rot('lowerarm01.'+side,(1,0,0),-.38*charge)
    elif kind=='Leap':
        # Clip seconds: anticipation .00-.18, flight .18-.78, recovery .78-1.06.
        crouch=curve(t,[(0,0),(.12,1),(.20,.12),(.52,.05),(.736,0),(.82,.8),(1,0)])
        airborne=curve(t,[(0,0),(.17,0),(.37,1),(.59,.88),(.736,0),(1,0)])
        height-=.15*crouch
        for side,sign in [('L',1),('R',-1)]:
            feet[side].z+=.27*airborne
            feet[side].y+=.12*airborne
            rolls[side]=.25*airborne
            rot('upperarm01.'+side,(1,0,0),-1.55*airborne+.25*crouch)
            rot('lowerarm01.'+side,(1,0,0),-.28*airborne)
        rot('spine03',(1,0,0),.20*crouch-.08*airborne)
    elif kind=='Hit':
        impact=curve(t,[(0,0),(.22,1),(.52,.65),(1,0)])
        rot('spine03',(1,0,0),-.11*impact);rot('head',(1,0,0),.12*impact)
        height-=.025*impact
    elif kind=='Death':
        collapse=curve(t,[(0,0),(.22,.14),(.72,1),(1,1)])
        rot('root',(1,0,0),-collapse*1.51)
        rot('spine02',(1,0,0),collapse*.17)
        height=-.045-.94*collapse
        for side in ['L','R']:rot('upperarm01.'+side,(1,0,0),-.50*collapse)
    root_height(height)
    if kind!='Death':
        for side in ['L','R']:solve_leg(side,feet[side],rolls[side])
    # Cloth follows the actual leg swing with a mild delayed secondary movement.
    bpy.context.view_layer.update()
    for i in range(16):
        a=i*math.tau/16;side='L' if math.cos(a)>0 else 'R'
        thigh=rig.pose.bones['upperleg01.'+side]
        movement=thigh.matrix.to_quaternion()@thigh.bone.matrix_local.to_quaternion().inverted()
        leg_forward=(movement@Vector((0,0,-1))).y
        outward=max(0,-leg_forward)*max(0,-math.sin(a))*.85+max(0,leg_forward)*max(0,math.sin(a))*.7
        if kind=='Whirlwind':outward+=.27
        if kind=='Leap':outward+=.18*math.sin(math.pi*t)**2
        if kind=='Run':outward+=.035*(1+math.sin(t*math.tau*2-i*.25))
        rot(f'tasset.{i:02}',(-math.sin(a),math.cos(a),0),-outward)

clips=[('Idle',2.4),('Run',.64),('Attack',.72),('Whirlwind',.60),
       ('Rally',.70),('WarCry',.78),('Berserk',.94),('Leap',1.06),('Death',1.2),('Hit',.34)]
rig.animation_data_create();bpy.context.scene.render.fps=60
loop_names={'Idle','Run','Whirlwind'};quality={}
for name,duration in clips:
    action=bpy.data.actions.new(name);rig.animation_data.action=action
    frames=round(duration*60);previous={};max_delta=0;first=None;last=None
    for frame in range(frames+1):
        pose(name,frame/frames)
        state={}
        for pb in rig.pose.bones:
            q=pb.rotation_quaternion
            if pb.name in previous:
                if q.dot(previous[pb.name])<0:q.negate()
                max_delta=max(max_delta,previous[pb.name].rotation_difference(q).angle)
            previous[pb.name]=q.copy();state[pb.name]=q.copy()
            pb.keyframe_insert('rotation_quaternion',frame=frame+1,group=pb.name)
            if pb.name=='root':pb.keyframe_insert('location',frame=frame+1,group=pb.name)
        if first is None:first=state
        last=state
    # Linear interpolation of densely sampled smooth poses prevents Bezier overshoot.
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points:key.interpolation='LINEAR'
    loop_error=max(first[n].rotation_difference(last[n]).angle for n in first) if name in loop_names else None
    assert max_delta<.65,(name,'Pose discontinuity',max_delta)
    if loop_error is not None:assert loop_error<.001,(name,'Loop discontinuity',loop_error)
    quality[name]={'duration':frames/60,'max_frame_rotation_radians':round(max_delta,5),'loop_seam_radians':loop_error}
    action.use_fake_user=True
    track=rig.animation_data.nla_tracks.new();track.name=name
    track.strips.new(name,1,action);track.mute=True
    print('CLIP',name,quality[name],flush=True)
rig.animation_data.action=None;pose('Idle',0);bpy.context.scene.frame_set(1)
manifest={'clips':quality,'run_reference_speed':3.2,'attack_hit_fraction':.49,
          'leap_takeoff_seconds':.18,'leap_land_seconds':.78,'leap_duration':64/60,
          'equipment_bones':{'left_weapon':'wrist.L','right_weapon':'wrist.R','boots':['foot.L','foot.R'],
                             'skirt':[f'tasset.{i:02}' for i in range(16)]},
          'grips':{side:{'origin':list(p),'axis':list(axis)} for side,(p,axis) in grip_frames.items()}}
(ROOT/'game/data/barbarian_animation.json').write_text(json.dumps(manifest,indent=2))
