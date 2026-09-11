"""Check the exported GLB, not just Blender authoring data. No dependencies.

python3 tools/verify_barbarian.py
python3 tools/verify_barbarian.py --captures
"""
import argparse
import json
import math
import pathlib
import struct
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
GODOT = '/Applications/Godot.app/Contents/MacOS/Godot'
blob = (ROOT / 'game/assets/models/barbarian.glb').read_bytes()
assert blob[:4] == b'glTF'
json_length = struct.unpack_from('<I', blob, 12)[0]
doc = json.loads(blob[20:20+json_length])
binary = blob[28+json_length:]
FORMATS = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}
COMPONENTS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def accessor(index):
    item = doc['accessors'][index]
    view = doc['bufferViews'][item['bufferView']]
    fmt = '<' + FORMATS[item['componentType']] * COMPONENTS[item['type']]
    stride = view.get('byteStride', struct.calcsize(fmt))
    offset = view.get('byteOffset', 0) + item.get('byteOffset', 0)
    return [struct.unpack_from(fmt, binary, offset+i*stride) for i in range(item['count'])]

report = {'asset': 'barbarian.glb', 'checks': [], 'animations': {}}
joint_count = len(doc['skins'][0]['joints'])
assert joint_count >= 179, joint_count
node_names = {node.get('name') for node in doc['nodes']}
assert all(f'tasset.{i:02}' in node_names for i in range(16))
report['joint_count'] = joint_count
vertices = triangles = 0
for mesh in doc['meshes']:
    for primitive in mesh['primitives']:
        attributes = primitive['attributes']
        vertices += doc['accessors'][attributes['POSITION']]['count']
        triangles += doc['accessors'][primitive['indices']]['count']//3
        assert 'WEIGHTS_0' in attributes and 'JOINTS_0' in attributes, mesh['name']
        for weights in accessor(attributes['WEIGHTS_0']):
            assert abs(sum(weights)-1) < .002, (mesh['name'], weights)
            assert all(0 <= w <= 1 for w in weights)
        for joints in accessor(attributes['JOINTS_0']):
            assert all(0 <= j < joint_count for j in joints)
report.update(vertex_count=vertices, triangle_count=triangles)
report['checks'].append('Every exported mesh has normalized skin weights and valid bone indices.')

expected = json.loads((ROOT/'game/data/barbarian_animation.json').read_text())
seen = set()
for animation in doc['animations']:
    name = animation['name'].split('|')[-1]
    assert name in expected['clips'], name
    seen.add(name)
    max_angle = 0
    seam = 0
    duration = 0
    for channel in animation['channels']:
        sampler = animation['samplers'][channel['sampler']]
        times = [t[0] for t in accessor(sampler['input'])]
        values = accessor(sampler['output'])
        assert all(b > a for a, b in zip(times, times[1:])), name
        assert all(math.isfinite(v) for row in values for v in row), name
        duration = max(duration, times[-1]-times[0])
        if channel['target']['path'] == 'rotation':
            for row in values:assert abs(sum(v*v for v in row)-1) < .002
            for a, b in zip(values, values[1:]):
                dot = min(1, abs(sum(x*y for x, y in zip(a, b))))
                max_angle = max(max_angle, 2*math.acos(dot))
            dot = min(1, abs(sum(x*y for x, y in zip(values[0], values[-1]))))
            seam = max(seam, 2*math.acos(dot))
        elif channel['target']['path'] == 'translation' and name in ['Idle', 'Run', 'Whirlwind']:
            assert math.dist(values[0], values[-1]) < .0001, ('Root loop seam', name)
    assert abs(duration-expected['clips'][name]['duration']) < .025, (name, duration)
    assert max_angle < .66, (name, 'Abrupt pose change', max_angle)
    if name in ['Idle', 'Run', 'Whirlwind']:
        assert seam < .002, (name, 'Loop seam', seam)
    report['animations'][name] = {'duration': round(duration, 4),
                                 'max_sample_rotation_degrees': round(math.degrees(max_angle), 3),
                                 'loop_seam_degrees': round(math.degrees(seam), 4) if name in ['Idle', 'Run', 'Whirlwind'] else None}
assert seen == set(expected['clips'])
report['checks'].append('All ten GLB clips have finite normalized transforms, continuous samples, and gameplay-matched durations.')
report['checks'].append('Idle, Run and Whirlwind close their root and rotation loops.')

args = argparse.ArgumentParser()
args.add_argument('--captures', action='store_true')
if args.parse_args().captures:
    destination = ART/'barbarian-motion'
    destination.mkdir(exist_ok=True)
    for name in expected['clips']:
        output = destination/(name.lower()+'.png')
        result = subprocess.run([GODOT, '--path', str(ROOT/'game'), 'res://scenes/hero_review.tscn',
                                 '--max-fps', '60', '--quit-after', '180', '--',
                                 '--review-capture='+str(output), '--clip='+name, '--phase=0.48'],
                                capture_output=True, text=True, timeout=40)
        log = result.stdout+result.stderr
        (destination/(name.lower()+'.log')).write_text(log)
        assert result.returncode == 0 and 'REVIEW CAPTURE:' in log and 'ERROR:' not in log, log
        print('Captured', name, flush=True)
    report['capture_directory'] = str(destination)

report['limits'] = 'Geometry and timing checks do not certify likeness to Diablo II: Resurrected or every possible cloth collision. Review engine captures and live transitions as well.'
(ART/'barbarian-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
