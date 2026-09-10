"""Original synthesized ambience and UI/combat Foley; no commercial game recordings."""
from pathlib import Path
import math, random, struct, wave
root=Path(__file__).resolve().parents[1]/'game/assets/audio'
root.mkdir(parents=True,exist_ok=True)
random.seed(4)
rate=22050
def save(name,duration,fn):
    data=bytearray()
    low=0
    for i in range(int(rate*duration)):
        t=i/rate;n=random.uniform(-1,1);low=low*.97+n*.03
        v=max(-1,min(1,fn(t,n,low)))
        data+=struct.pack('<h',int(v*26000))
    with wave.open(str(root/(name+'.wav')),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(data)
save('wind',16,lambda t,n,l:l*.6+math.sin(t*math.tau*55)*.018+math.sin(t*math.tau*82.5)*.009)
save('click',.12,lambda t,n,l:math.sin(t*math.tau*(600-800*t))*math.exp(-t*55)*.17)
save('impact',.26,lambda t,n,l:(n*.40+math.sin(t*math.tau*90)*.6)*math.exp(-t*24))
save('swing',.3,lambda t,n,l:n*.35*math.sin(t/.3*math.pi)**2)
save('quest',1.6,lambda t,n,l:sum(math.sin(t*math.tau*f) for f in [220,330,440,554.37])*.085*math.sin(min(1,t*6)*math.pi/2)*math.exp(-t*2.5))
print('Original audio generated.')
save('shout',.85,lambda t,n,l:(sum(math.sin(t*math.tau*f) for f in [86,172,257,430])*.13+l*.5)*math.sin(min(1,t*12)*math.pi/2)*math.exp(-t*3))
save('slam',.7,lambda t,n,l:(n*.21+math.sin(t*math.tau*(65-25*t))*.65)*math.exp(-t*9))
save('leap',.55,lambda t,n,l:n*.30*math.sin(t/.55*math.pi)+math.sin(t*math.tau*(180+320*t))*.08*math.exp(-t*7))
