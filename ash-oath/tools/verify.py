"""Run the real scene's interaction checks and capture the three opening views."""
import subprocess, pathlib, json, time, re
root=pathlib.Path(__file__).resolve().parents[1]
godot='/Applications/Godot.app/Contents/MacOS/Godot'
out=root/'artifacts'
def run(name,args,timeout=90):
    p=subprocess.run([godot,*args],cwd=root,capture_output=True,text=True,timeout=timeout)
    log=p.stdout+p.stderr
    (out/(name+'.log')).write_text(log)
    if p.returncode or 'SCRIPT ERROR' in log or '\nERROR:' in log:
        raise RuntimeError(name+' failed: '+log[-2500:])
    return log
run('godot-import',['--headless','--path','game','--editor','--import'])
result=run('smoke',['--headless','--max-fps','60','--quit-after','2200','--path','game','--','--smoke-test'])
assert 'SMOKE PASS' in result,result
print(result.strip(),flush=True)
images=[]
metrics=[]
for name,view in [('encampment',''),('akara','akara'),('blood-moor','moor'),('barbarian-ingame','hero'),('six-skills','combat')]:
    file=out/(name+'.png')
    args=['--max-fps','60','--quit-after','500','--path','game','--','--capture='+str(file)]
    if view:args.append('--view='+view)
    log=run('capture-'+name,args)
    assert file.exists() and 'Captured:' in log
    print(log.strip(),flush=True)
    images.append(str(file))
    m=re.search(r'fps=([0-9.]+), draw_calls=([0-9.]+)',log)
    metrics.append({'view':name,'fps_at_capture':float(m[1]),'draw_calls':int(float(m[2]))} if m else {'view':name})
(out/'verification.json').write_text(json.dumps({'date':time.strftime('%Y-%m-%d %H:%M:%S'), 'interaction_check':'passed','screenshots':images,'capture_metrics':metrics,'note':'Short single-window capture samples, not a sustained frame-time benchmark.'},indent=2))
