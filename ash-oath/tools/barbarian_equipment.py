"""Rest-space equipment authoring, executed by build_barbarian.py inside Blender.

All soft parts inherit anatomical weights; hard parts have explicit bone owners.
Weapon grips are derived from the curled finger joints, never world offsets.
"""
from mathutils.geometry import barycentric_transform

oxblood = mat('Faded oxblood war cloth', (.32, .075, .045), 0, .92)
linen = mat('Worn brown linen', (.22, .19, .145), 0, .94)
stitch = mat('Waxed linen stitches', (.48, .38, .25), 0, .86)
bone_mat = mat('Aged bone talismans', (.64, .56, .40), 0, .69)

# Color variation and fine scratches are exported textures, not Blender-only nodes.
size = 512
gy, gx = np.mgrid[:size, :size]
grain_rng = np.random.default_rng(38)
coarse = (np.sin(gx*.037)*np.sin(gy*.053)+np.sin(gx*.011+gy*.023))*.06
fine = grain_rng.normal(0, .035, (size, size))
creases = np.maximum(0, np.sin(gx*.43+np.sin(gy*.019)*8))**30 * .06
for material, color in [(leather, (.26, .17, .105)), (edge, (.39, .27, .15)),
                        (oxblood, (.34, .085, .055)), (linen, (.22, .19, .15)),
                        (steel, (.29, .31, .30))]:
    variation = np.clip(1+coarse+fine-creases, .55, 1.25)
    rgb = np.clip(np.array(color)[None, None, :] * variation[:, :, None], 0, 1)
    pixels = np.dstack((rgb, np.ones((size, size)))).astype('float32')
    tex = bpy.data.images.new(material.name+' albedo', width=size, height=size)
    tex.pixels.foreach_set(pixels.ravel())
    tex.pack()
    nt = material.node_tree
    node = nt.nodes.new('ShaderNodeTexImage'); node.image = tex
    principled = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    nt.links.new(node.outputs['Color'], principled.inputs['Base Color'])

surface_weights = {p.index:[(body.vertex_groups[g.group].name,g.weight) for g in p.groups] for p in body.data.vertices}

def fitted(o):
    """Barycentric transfer from the final smooth body, in rest space."""
    fit_uv(o)
    for vert in o.data.vertices:
        point, _, triangle_index, _ = bvh.find_nearest(o.matrix_world @ vert.co)
        triangle = body.data.loop_triangles[triangle_index]
        a,b,c = [body.data.vertices[i].co for i in triangle.vertices]
        bary = barycentric_transform(point,a,b,c,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        accum = {}
        for idx, influence in zip(triangle.vertices,bary):
            influence=max(0,influence)
            for bn, w in surface_weights[idx]:
                accum[bn] = accum.get(bn, 0)+w*influence
        total = sum(accum.values())
        assert total > 0, (o.name, vert.index)
        for bn, w in accum.items():
            group = o.vertex_groups.get(bn) or o.vertex_groups.new(name=bn)
            group.add([vert.index], w/total, 'REPLACE')
    modifier = o.modifiers.new('Continuous anatomical weights', 'ARMATURE')
    modifier.object = rig; o.parent = rig
    return o

def soften(o, thickness=.006, subdivision=1):
    if subdivision:
        mod = o.modifiers.new('Tailored smooth surface', 'SUBSURF')
        mod.levels = subdivision
    if thickness:
        mod = o.modifiers.new('Real material thickness', 'SOLIDIFY')
        mod.thickness = thickness
    return o

def soft_tube(name, points, radius, material):
    o = tube(name, points, [radius]*len(points), material, 'spine02', 6)
    o.vertex_groups.clear(); o.modifiers.clear()
    return fitted(o)

def surface(x, z, back=False, clearance=.024):
    hit = bvh.ray_cast(Vector((x, 1 if back else -1, z)), Vector((0, -1 if back else 1, 0)))
    assert hit[0] is not None, ('Missed torso surface', x, z)
    return hit[0] + hit[1]*clearance

def torso_band(name, points, width, back=False, clearance=.030):
    vs = []
    columns = 7
    for x, z in points:
        for j in range(columns):
            vs.append(surface(x+(j/(columns-1)-.5)*width, z, back, clearance))
    fs = [(i*columns+j, i*columns+j+1, (i+1)*columns+j+1, (i+1)*columns+j)
          for i in range(len(points)-1) for j in range(columns-1)]
    if back:fs=[tuple(reversed(f)) for f in fs]
    o = soften(fitted(mesh(name, vs, fs, leather)), .007, 1)
    # Small actual stitches follow the surface and its skin weights.
    for col in [1, columns-2]:
        for i in range(0, len(points)-2, 2):
            a = vs[i*columns+col]; b = vs[(i+1)*columns+col]
            soft_tube(name+' stitch', [a, a.lerp(b, .6)], .0011, stitch)
    for col in [0, columns-1]:
        soft_tube(name+' bound edge', vs[col::columns], .0028, edge)
    return o

# Underclothes use exactly the same topology and weights as the body.
chosen = [(f, fu) for f, fu in zip(faces, face_uv) if all(.55 <= v[i][2] <= 1.22 for i in f)]
ids = sorted({i for f, _ in chosen for i in f}); rm = {old:new for new, old in enumerate(ids)}
clothverts = []
for old in ids:
    p = Vector(v[old]); n = body.data.vertices[remap[old]].normal
    p += n*(.018+.003*math.sin(p.z*90+p.x*12))
    clothverts.append(p)
trousers = mesh('Tailored linen breeches', clothverts, [[rm[i] for i in f] for f, _ in chosen], linen)
uv = trousers.data.uv_layers.new()
for p, (_, fu) in zip(trousers.data.polygons, chosen):
    for li, t in zip(p.loop_indices, fu): uv.data[li].uv = texcoords[t]
skin_bind(trousers, ids); soften(trousers, .004)

# A broad corset-like war belt; continuous surface instead of stacked ropes.
def oval_shell(name, rows, material, bn='spine05', segments=64):
    vs = [(rx*math.cos(k*math.tau/segments), .018+ry*math.sin(k*math.tau/segments), z)
          for z, rx, ry in rows for k in range(segments)]
    fs = [(r*segments+k, r*segments+(k+1)%segments, (r+1)*segments+(k+1)%segments, (r+1)*segments+k)
          for r in range(len(rows)-1) for k in range(segments)]
    return soften(rigid(mesh(name, vs, fs, material), bn), .01, 0)

oval_shell('Wide fitted war girdle', [(1.115,.318,.247),(1.15,.313,.246),(1.25,.293,.239),(1.28,.289,.233)], leather)
for z, rx, ry in [(1.12,.319,.248),(1.275,.290,.234)]:
    ring('Girdle rolled seam', (0,.018,z),rx,ry,.004,edge)
for row in [1.15,1.245]:
    for i in range(24):
        a = i*math.tau/24
        sphere('Belt steel rivet', (.314*math.cos(a),.018+.248*math.sin(a),row),(.007,.007,.007),bronze,'spine05',8,6)
cube('Rectangular iron belt clasp', (0,-.240,1.19),(.12,.025,.104),steel,'spine05',.009)
for x in [-.045,.045]:tube('Clasp brass edge',[(x,-.260,1.148),(x,-.260,1.23)],[.004]*2,bronze,'spine05')
for z in [1.148,1.23]:tube('Clasp brass edge',[(-.045,-.260,z),(.045,-.260,z)],[.004]*2,bronze,'spine05')
tube('Clasp tongue',[(-.035,-.265,1.19),(.04,-.265,1.19)],[.005]*2,silver,'spine05')

# Separate skirt bones keep panels outside the leading thigh on every clip.
bpy.context.view_layer.objects.active=rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for i in range(16):
    a=i*math.tau/16
    b=rig.data.edit_bones.new(f'tasset.{i:02}')
    b.head=(.30*math.cos(a),.018+.24*math.sin(a),1.13)
    b.tail=(.37*math.cos(a),.018+.30*math.sin(a),.78)
    b.parent=rig.data.edit_bones['spine05']
    b.align_roll(Vector((0,-1,0)))
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
for i in range(16):
    a=i*math.tau/16; vs=[]; rows=9; cols=5
    for r in range(rows):
        t=r/(rows-1)
        for k in range(cols):
            u=k/(cols-1); angle=a+(u-.5)*math.tau/14.8
            fold=math.sin(u*math.pi*2+.3)*.008*t
            z=1.14-t*(.38+(.045 if i%2 else 0))+math.sin(u*math.pi*2+i)*.008*t**5
            vs.append(((.295+t*.08+fold)*math.cos(angle),.018+(.238+t*.055+fold)*math.sin(angle),z))
    fs=[(r*cols+k,r*cols+k+1,(r+1)*cols+k+1,(r+1)*cols+k) for r in range(rows-1) for k in range(cols-1)]
    bn=f'tasset.{i:02}'
    soften(rigid(mesh('Oxblood pleated war skirt',vs,fs,oxblood),bn),.005)
    tube('War skirt stitched hem',vs[-cols:],[.002]*cols,stitch,bn,5)
    # Short leather lames leave the faded red cloth showing below.
    if i%2==0:
        pts=[Vector(vs[r*cols+k])+Vector((math.cos(a)*.009,math.sin(a)*.009,0)) for r in range(6) for k in range(1,4)]
        fs2=[(r*3+k,r*3+k+1,(r+1)*3+k+1,(r+1)*3+k) for r in range(5) for k in range(2)]
        soften(rigid(mesh('Overlapping hide belt lames',pts,fs2,leather),bn),.007)
        for k in [1,16]:sphere('Lame rivet',pts[k],(.006,.006,.006),bronze,bn,8,6)

# Cross harness, front and back, conforms across the complete chest width.
for back in [False,True]:
    for sign in [-1,1]:
        points=[(sign*(.23-.41*t),1.775-.49*t) for t in np.linspace(0,1,45)]
        clearance=.032 if sign==-1 else .048
        torso_band('Crossed shoulder harness',points,.069,back,clearance)
        # Metal buckles have the same deformation as their nearby strap.
        t=.31; x=sign*(.23-.41*t); z=1.775-.49*t
        for dz in [-.032,.032]:
            soft_tube('Harness buckle bar',[surface(x-.028,z+dz,back,clearance+.014),surface(x+.028,z+dz,back,clearance+.014)],.005,bronze)
        for dx in [-.028,.028]:
            soft_tube('Harness buckle frame',[surface(x+dx,z-.032,back,clearance+.014),surface(x+dx,z+.032,back,clearance+.014)],.005,bronze)

# Continuous strap bridges across the shoulder; both ends meet the chest/back bands.
for sign in [-1,1]:
    vs=[]
    for y in np.linspace(-.12,.18,28):
        for x in np.linspace(sign*.23-.036,sign*.23+.036,5):
            hit=bvh.ray_cast(Vector((x,y,2.1)),Vector((0,0,-1)))
            if hit[0] is None:hit=bvh.find_nearest(Vector((x,y,1.78)))
            vs.append(hit[0]+hit[1]*.030)
    fs=[(r*5+k,r*5+k+1,(r+1)*5+k+1,(r+1)*5+k) for r in range(27) for k in range(4)]
    soften(fitted(mesh('Harness over shoulder bridge',vs,fs,leather)),.006,1)

# Shoulder saddles are continuous hide shells centered on the shoulder joint.
# Front-facing studs sit on the shell, not in a flat plane beside the body.
for sign, side in [(1,'L'),(-1,'R')]:
    shoulder=joint('upperarm01.'+side+'____head'); bn='upperarm01.'+side
    vs=[];rows=11;cols=19
    for r in range(rows):
        t=r/(rows-1); center=shoulder+Vector((sign*(.015+t*.19),0,-.02-t*.06))
        radius=.133+.025*math.sin(t*math.pi)
        for k in range(cols):
            a=-math.pi*.10+k/(cols-1)*math.pi*1.2
            candidate=center+Vector((0,-math.cos(a)*radius,math.sin(a)*radius))
            hit=bvh.find_nearest(candidate)
            vs.append(hit[0]+hit[1]*.024)
    fs=[(r*cols+k,r*cols+k+1,(r+1)*cols+k+1,(r+1)*cols+k) for r in range(rows-1) for k in range(cols-1)]
    if sign==1:fs=[tuple(reversed(f)) for f in fs]
    soften(fitted(mesh('Studded leather shoulder saddle '+side,vs,fs,leather)),.009)
    for r in [1,rows-2]:tube('Shoulder bound rim',vs[r*cols:(r+1)*cols],[.006]*cols,edge,bn)
    for r in [2,5,8]:
        for k in [2,5,8,11,14,16]:
            a=-math.pi*.10+k/(cols-1)*math.pi*1.2
            sphere('Shoulder iron stud',vs[r*cols+k]+Vector((0,-math.cos(a)*.01,math.sin(a)*.01)),(.009,.009,.009),steel,bn,8,6)

    # Tapered solid vambrace around the forearm; strapped metal splints outside.
    elbow=joint('lowerarm01.'+side+'____head');wrist=joint('wrist.'+side+'____head')
    q=(wrist-elbow).normalized().to_track_quat('Z','Y');bn='lowerarm01.'+side
    def armring(t,extra=0):
        c=elbow.lerp(wrist,t); radius=.106-t*.040+extra
        return [c+q@Vector((math.cos(k*math.tau/32)*radius,math.sin(k*math.tau/32)*radius,0)) for k in range(33)]
    rings=[armring(t) for t in np.linspace(.28,.91,9)]
    vs=[p for row in rings for p in row]
    fs=[(r*33+k,r*33+k+1,(r+1)*33+k+1,(r+1)*33+k) for r in range(8) for k in range(32)]
    soften(rigid(mesh('Shaped leather vambrace '+side,vs,fs,leather),bn),.008,0)
    for t in [.34,.81]:tube('Vambrace leather straps',armring(t,.008),[.006]*33,edge,bn)
    for k in [1,4,7,10,13]:
        a=k*math.tau/32
        pts=[elbow.lerp(wrist,t)+q@Vector((math.cos(a)*(.119-t*.04),math.sin(a)*(.119-t*.04),0)) for t in [.35,.82]]
        tube('Vambrace forged splint',pts,[.011,.008],steel,bn,6)
        for p in pts:sphere('Vambrace stud',p,(.006,.006,.006),bronze,bn,8,6)

    # Closed boot last: no copied toes. Stacked rings create toe box, instep and shaft.
    ankle=joint('foot.'+side+'____head');knee=joint('lowerleg01.'+side+'____head')
    bootrows=[(.018,.106,-.071,.213),(.045,.110,-.071,.214),(.090,.108,-.069,.208),
              (.14,.098,-.048,.166),(.19,.083,-.010,.105),(.25,.082,.004,.092),
              (.34,.093,.004,.102),(.44,.101,.003,.107),(.55,.106,.001,.112),(.60,.103,0,.110)]
    vs=[];segments=48
    for z,rx,cy,ry in bootrows:
        t=max(0,min(1,(z-ankle.z)/(knee.z-ankle.z)));center=ankle.lerp(knee,t)
        for k in range(segments):
            a=k*math.tau/segments
            vs.append((center.x+rx*math.cos(a),center.y+cy+ry*math.sin(a),z))
    fs=[(r*segments+k,r*segments+(k+1)%segments,(r+1)*segments+(k+1)%segments,(r+1)*segments+k)
        for r in range(len(bootrows)-1) for k in range(segments)]
    fs.append(tuple(range(segments-1,-1,-1)))
    boot=mesh('Closed leather boot '+side,vs,fs,leather);fit_uv(boot)
    for vert in boot.data.vertices:
        # Ankle band blends foot to shin, preserving the sealed toe box.
        blend=max(0,min(1,(vert.co.z-.14)/.10))
        for bone_name,w in [('foot.'+side,1-blend),('lowerleg01.'+side,blend)]:
            if w>0:
                g=boot.vertex_groups.get(bone_name) or boot.vertex_groups.new(name=bone_name)
                g.add([vert.index],w,'REPLACE')
    mod=boot.modifiers.new('Boot ankle articulation','ARMATURE');mod.object=rig;boot.parent=rig
    soften(boot,.005)
    for z in [.028,.053]:
        pts=[Vector((ankle.x+.112*math.cos(k*math.tau/48),ankle.y-.071+.218*math.sin(k*math.tau/48),z)) for k in range(49)]
        tube('Boot welt and sole',pts,[.009]*49,tread,'foot.'+side,6)
    for z in [.29,.47,.57]:
        c=ankle.lerp(knee,(z-ankle.z)/(knee.z-ankle.z))
        rx=float(np.interp(z,[r[0] for r in bootrows],[r[1] for r in bootrows]))+.005
        cy=float(np.interp(z,[r[0] for r in bootrows],[r[2] for r in bootrows]))
        ry=float(np.interp(z,[r[0] for r in bootrows],[r[3] for r in bootrows]))+.005
        ring('Boot securing strap',(c.x,c.y+cy,z),rx,ry,.006,edge,'lowerleg01.'+side)
        cube('Boot iron buckle',(c.x+sign*rx,c.y-.026,z),(.014,.037,.03),steel,'lowerleg01.'+side,.004)
    # Laces on the boot front, each tied to the shin.
    for j in range(6):
        z=.31+j*.037;c=ankle.lerp(knee,(z-ankle.z)/(knee.z-ankle.z))
        tube('Boot cross lace',[(c.x-.036,c.y-.115,z),(c.x+.036,c.y-.119,z+.027)],[.002]*2,stitch,'lowerleg01.'+side,5)

# Small belt pouches with lids, stitching and attached fasteners.
for sign in [-1,1]:
    p=Vector((sign*.292,.10,1.052))
    cube('Belt provision pouch',p,(.12,.105,.17),leather,'spine05',.025)
    cube('Pouch folded flap',p+Vector((0,-.057,.05)),(.13,.014,.075),edge,'spine05',.012)
    sphere('Pouch fastening stud',p+Vector((0,-.07,.032)),(.008,.006,.008),bronze,'spine05',8,6)

# Bare scalp and short brows match the remaster's recognizable silhouette.
for side in ['L','R']:
    c=joint('eye.'+side+'____head')
    sphere('Eyeball '+side,c,(.018,.018,.018),eye_mat,'head',24,16)
    sphere('Iris '+side,c+Vector((0,-.014,0)),(.008,.005,.008),iris_mat,'head',20,12)
    sphere('Pupil '+side,c+Vector((0,-.018,0)),(.0035,.002,.0035),black,'head',16,8)
for sign,side in [(1,'L'),(-1,'R')]:
    c=joint('eye.'+side+'____head')
    for i in range(60):
        t=i/59;x=c.x+sign*(t-.46)*.047;z=c.z+.027+.009*(1-t)
        p=surface(x,z,clearance=.002)
        tube('Short weathered eyebrow',[p,p+Vector((sign*.006,0,.002))],[.0008,.0002],hair,'head',4)

# Close-cropped stubble, forehead creases and healed cuts keep the face readable.
wrinkle=mat('Weathered facial creases',(.38,.27,.20),0,.83)
for level in [2.065,2.083,2.098]:
    pts=[surface(x,level+.002*math.cos(x*45),clearance=.0008) for x in np.linspace(-.074,.074,32)]
    tube('Forehead expression crease',pts,[.00055]*len(pts),wrinkle,'head',4)
for i in range(450):
    x=random.uniform(-.092,.092);z=random.uniform(1.905,1.957)
    if abs(x)<.052 and z>1.934:continue
    hit=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
    if hit[0] is None:continue
    p=hit[0]+hit[1]*.001
    tube('Shaved jaw stubble',[p,p+Vector((x*.008,-.0006,-random.uniform(.001,.003)))],[.00045,.0001],hairlight if i%3==0 else hair,'head',3)
for x,z,dx,dz,length in [(.058,2.045,.004,-.06,24),(-.145,1.65,.10,-.04,35)]:
    pts=[surface(x+dx*t,z+dz*t,clearance=.002) for t in np.linspace(0,1,length)]
    soft_tube('Healed battle scar',pts,.0014,scar)

# Surface-fitted woad inherits the face and torso's anatomical weights.
for name in ['Scalp and face woad','Woad chest stripe','Woad back stripe']:
    # Clip each body triangle in X/Z would create hard UV seams. A fitted sampled
    # ribbon retains a precise width while interpolating the original skin weights.
    if name.startswith('Scalp'):
        points=[]
        for angle in np.linspace(-.19,math.pi+.13,110):
            direction=Vector((0,math.cos(angle),-math.sin(angle)))
            for x in np.linspace(-.042,.006,7):
                origin=Vector((x,-.055,2.018))-direction*.4
                hit=bvh.ray_cast(origin,direction)
                assert hit[0] is not None, ('Scalp stripe',angle,x)
                points.append(hit[0]+hit[1]*.0018)
        fs=[(r*7+k,r*7+k+1,(r+1)*7+k+1,(r+1)*7+k) for r in range(109) for k in range(6)]
        fitted(mesh(name,points,fs,paint))
    else:
        back='back' in name;points=[]
        for z in np.linspace(1.36,1.78,72):
            for x in np.linspace(-.051,.009,7):points.append(surface(x,z,back,.0018))
        fs=[(r*7+k,r*7+k+1,(r+1)*7+k+1,(r+1)*7+k) for r in range(71) for k in range(6)]
        fitted(mesh(name,points,fs,paint))

# Hand closure and grip frame are shared by equipment and animation authoring.
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
def rest_rotate(name,axis,angle):
    pb=rig.pose.bones[name];q=pb.bone.matrix_local.to_quaternion()
    pb.rotation_quaternion=pb.rotation_quaternion @ (q.inverted()@Quaternion(Vector(axis),angle)@q)

grip_frames={}
finger_axes={}
for side,sign in [('L',1),('R',-1)]:
    index=rig.data.bones['finger2-1.'+side].head_local
    pinky=rig.data.bones['finger5-1.'+side].head_local
    axis=(index-pinky).normalized();finger_axes[side]=axis
    # Curl toward palm normal, same anatomical convention on both hands.
    for finger in range(2,6):
        for part,angle in [(1,1.05),(2,1.27),(3,.87)]:rest_rotate(f'finger{finger}-{part}.{side}',axis,-sign*angle)
    rest_rotate('finger1-1.'+side,(0,0,1),sign*.42)
    rest_rotate('finger1-2.'+side,axis,-sign*.65)
    rest_rotate('finger1-3.'+side,axis,-sign*.65)
bpy.context.view_layer.update()
for side in ['L','R']:
    # Average the inside of curled middle phalanges, then shift toward the palm.
    p=sum((rig.pose.bones[f'finger{f}-2.{side}'].head for f in [2,3,4,5]),Vector())/4
    knuckle=sum((rig.data.bones[f'finger{f}-1.{side}'].head_local for f in [2,3,4,5]),Vector())/4
    p=p.lerp(knuckle,.30)
    axis=finger_axes[side]
    # Upright direction, useful when checking the grip frame in the neutral pose.
    if axis.z<0:axis=-axis
    grip_frames[side]=(p,axis)
    bn='wrist.'+side
    # The complete weapon is built in its grip frame and rigidly follows the wrist.
    q=axis.to_track_quat('Z','Y')
    if side=='L':q=q@Quaternion(Vector((0,0,1)),math.radians(65))
    def wp(x,y,z):return p+q@Vector((x,y,z))
    def wt(name,ps,rs,material,sides=8):return tube(name,[wp(*point) for point in ps],rs,material,bn,sides)
    wt('Weapon leather handgrip',[(0,0,-.092),(0,0,.095)],[.023,.023],leather,12)
    for k in range(10):
        z=-.089+k*.019
        pts=[wp(.024*math.cos(j*math.tau/20),.024*math.sin(j*math.tau/20),z+j*.0005) for j in range(21)]
        tube('Grip leather winding',pts,[.0025]*21,edge,bn,5)
    if side=='R':
        wt('Axe ashwood haft',[(0,0,-.28),(0,0,.56)],[.019,.023],edge,12)
        # Crescent cutting edge and curved beard; broad bevel bands are geometry.
        profile=[(-.035,.51),(.08,.565),(.21,.66),(.285,.67),(.30,.59),(.31,.49),(.285,.37),(.23,.26),(.13,.22),(.15,.34),(.08,.405),(-.035,.405)]
        n=len(profile);vs=[wp(x,y,z) for y in [-.027,.027] for x,z in profile]
        fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        o=rigid(mesh('Forged crescent battle axe',vs,fs,steel),bn)
        bevel=o.modifiers.new('Axe forged bevel','BEVEL');bevel.width=.007;bevel.segments=3
        edgepts=[profile[k] for k in range(3,9)]
        bevelvs=[]
        for x,z in edgepts:bevelvs.extend([wp(x,-.029,z),wp(x-.032,-.031,z+.004)])
        rigid(mesh('Sharpened axe bevel',bevelvs,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(edgepts)-1)],silver),bn)
        wt('Axe counterweight',[(-.10,0,.46),(.04,0,.46)],[.025,.035],steel)
        for z in [.38,.53]:wt('Axe socket band',[(0,0,z-.014),(0,0,z+.014)],[.033,.033],bronze,12)
        sphere('Axe pommel',wp(0,0,-.285),(.027,.027,.032),steel,bn,12,8)
    else:
        wt('Sword curved guard',[(-.13,0,.12),(-.07,0,.15),(0,0,.155),(.07,0,.15),(.13,0,.12)],[.013,.014,.016,.014,.013],steel)
        vs=[wp(*x) for x in [(-.036,0,.17),(0,-.012,.17),(.036,0,.17),(0,.012,.17),(-.030,0,.65),(0,-.010,.65),(.030,0,.65),(0,.01,.65),(0,0,.80)]]
        rigid(mesh('Tempered one handed sword',vs,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,8),(5,6,8),(6,7,8),(7,4,8)],silver),bn)
        wt('Sword recessed fuller',[(0,-.013,.20),(0,-.011,.61)],[.0035,.0025],steel,5)
        sphere('Sword disc pommel',wp(0,0,-.12),(.030,.030,.037),bronze,bn,16,10)

# Hide only fully covered body faces; prevents toe/skin breakthroughs in boots.
# Leather shoulder edges and studs inherit the same distributed shoulder weights
# as the saddle, avoiding detached caps when the arms rise over the head.
for accessory in list(bpy.context.scene.objects):
    if accessory.type=='MESH' and accessory.name.startswith(('Shoulder bound rim','Shoulder iron stud')):
        accessory.vertex_groups.clear();accessory.modifiers.clear();fitted(accessory)
import bmesh
bm=bmesh.new();bm.from_mesh(body.data)
hidden=[f for f in bm.faces if all(vert.co.z<.57 for vert in f.verts)]
bmesh.ops.delete(bm,geom=hidden,context='FACES');bm.to_mesh(body.data);bm.free()
for pb in rig.pose.bones:pb.rotation_quaternion=Quaternion()
print('EQUIPMENT: fitted harness, 16 skirt joints, closed boots, anatomical grips',flush=True)
