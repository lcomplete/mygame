shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, blend_add;
uniform float clock = 0.0;
uniform float phase = 0.0;
float hash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise(vec2 p) {
 vec2 i=floor(p); vec2 f=fract(p); f=f*f*(3.0-2.0*f);
 return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
void fragment() {
 float y=1.0-UV.y;
 float t=clock*2.8+phase;
 float n=noise(vec2(UV.x*5.0,y*5.0-t))*.65+noise(vec2(UV.x*12.0,y*10.0-t*1.7))*.35;
 float x=UV.x-.5+sin(y*6.0-t)*.055*y;
 float width=(1.0-y)*.33+(n-.42)*.18*y;
 float a=smoothstep(0.0,.065,width-abs(x))*smoothstep(1.0,.84,y)*smoothstep(0.0,.08,y);
 float core=smoothstep(.17,.0,abs(x))*smoothstep(.80,.12,y);
 ALBEDO=mix(vec3(1.5,.18,.015),vec3(2.5,1.4,.30),core);
 ALPHA=a*.70;
}
