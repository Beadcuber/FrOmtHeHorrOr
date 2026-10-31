from pathlib import Path
import json, math, struct, subprocess, wave, re
root=Path('src/main/java/com/fromthehorror')
def read(n): return (root/n).read_text(encoding='utf-8')
def write(n,s): (root/n).write_text(s,encoding='utf-8')
p=read('CorisandeEntity.java')
if 'import net.minecraft.util.ActionResult;' not in p:
 p=p.replace('import net.minecraft.entity.mob.PathAwareEntity;','import net.minecraft.entity.mob.PathAwareEntity;\nimport net.minecraft.util.ActionResult;\nimport net.minecraft.util.Hand;')
method='''    /** Right-click the friendly orb with an empty hand to carry her; sneak to put her down. */
    @Override
    public ActionResult interactMob(PlayerEntity player, Hand hand) {
        if (isHostile() || getType() != FromTheHorror.CORISANDE || !player.getStackInHand(hand).isEmpty()) return ActionResult.PASS;
        if (!this.getWorld().isClient) {
            if (hasVehicle()) { stopRiding(); player.sendMessage(Text.literal("<Corisande> I can walk. You don't have to carry me forever."), false); }
            else if (player.getPassengerList().isEmpty() && startRiding(player, true)) {
                getNavigation().stop();
                player.sendMessage(Text.literal("<Corisande> Oh! A lift? I can see everything from up here."), false);
            }
        }
        return ActionResult.success(this.getWorld().isClient);
    }

'''
pat=r'    /\*\* Right-click[^\n]*\*/\s+@Override\s+public ActionResult interactMob\(PlayerEntity player, Hand hand\) \{.*?\n    \}\n'
if re.search(pat,p,re.S): p=re.sub(pat,method,p,count=1,flags=re.S)
elif 'public ActionResult interactMob(' not in p: p=p.replace('    @Override\n    public void tick() {',method+'    @Override\n    public void tick() {',1)
if 'if (hasVehicle()) return;' not in p: p=p.replace('        PlayerEntity p = w.getClosestPlayer(this, 64.0);','        if (hasVehicle()) return;\n        PlayerEntity p = w.getClosestPlayer(this, 64.0);',1)
write('CorisandeEntity.java',p)
p=read('FromTheHorror.java')
if 'import net.minecraft.sound.SoundEvent;' not in p: p=p.replace('import net.minecraft.registry.Registry;','import net.minecraft.registry.Registry;\nimport net.minecraft.sound.SoundEvent;')
if 'public static SoundEvent CORISANDE_THEME;' not in p: p=p.replace('    public static Item FLASHLIGHT;','    public static Item FLASHLIGHT;\n    public static SoundEvent CORISANDE_THEME;')
if 'CORISANDE_THEME = Registry.register' not in p: p=p.replace('    public void onInitialize() {','    public void onInitialize() {\n        CORISANDE_THEME = Registry.register(Registries.SOUND_EVENT, new Identifier(ID, "corisande_theme"), SoundEvent.of(new Identifier(ID, "corisande_theme")));')
if 'literal("music")' not in p:
 anchor='''                .then(CommandManager.literal("monster").executes(c -> {
                    CorisandeManager.summonMonster(c.getSource().getPlayerOrThrow()); return 1; }))'''
 if anchor in p: p=p.replace(anchor,anchor+'''\n                .then(CommandManager.literal("music").executes(c -> {
                    CorisandeManager.playTheme(c.getSource().getPlayerOrThrow()); return 1; }))''',1)
write('FromTheHorror.java',p)
p=read('CorisandeManager.java')
play='''    public static void playTheme(ServerPlayerEntity p) {
        p.getServerWorld().playSound(null, p.getBlockPos(), FromTheHorror.CORISANDE_THEME, SoundCategory.MUSIC, 0.85f, 1.0f);
        say(p, "I made this for the quiet moments. Stay with me until it ends.", false);
    }

'''
if 'public static void playTheme(' not in p: p=p.replace('    public static void summonMonster(ServerPlayerEntity p) {',play+'    public static void summonMonster(ServerPlayerEntity p) {',1)
write('CorisandeManager.java',p)
p=read('CorisandeBrain.java')
trigger='''        if (any(s, "play your music", "play music", "play your song", "play that song", "music please", "sing for me", "play your theme", "theme song")) {
            CorisandeManager.playTheme(p);
            return null;
        }
'''
if 'CorisandeManager.playTheme(p)' not in p: p=p.replace('        if (s.contains("verity"))',trigger+'        if (s.contains("verity"))',1)
write('CorisandeBrain.java',p)
assets=Path('src/main/resources/assets/fromthehorror'); (assets/'sounds').mkdir(parents=True,exist_ok=True)
(assets/'sounds.json').write_text(json.dumps({'corisande_theme':{'sounds':[{'name':'fromthehorror:corisande_theme','stream':True}],'subtitle':'subtitles.fromthehorror.corisande_theme'}},indent=2)+'\n')
lp=assets/'lang/en_us.json'; lang=json.loads(lp.read_text()); lang['subtitles.fromthehorror.corisande_theme']='Corisande plays a haunting melody'; lp.write_text(json.dumps(lang,indent=2)+'\n')
sr,duration=22050,28; wavp=assets/'sounds/corisande_theme.wav'
notes=[(1.8,392,2.4),(5.9,311.13,3.0),(10.7,349.23,2.5),(15.6,233.08,3.8),(21.2,277.18,2.8),(25.0,196.0,2.2)]
with wave.open(str(wavp),'wb') as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); frames=[]
 for i in range(sr*duration):
  t=i/sr; v=.105*math.sin(2*math.pi*55*t+.15*math.sin(2*math.pi*.035*t))+.052*math.sin(2*math.pi*82.41*t+1.4)+.032*math.sin(2*math.pi*110*t+2.2)
  for start,freq,decay in notes:
   x=t-start
   if 0<=x<decay:
    env=math.exp(-x*1.9)*(1-math.exp(-x*22)); v+=.095*env*(math.sin(2*math.pi*freq*x)+.34*math.sin(2*math.pi*freq*2.003*x+.2)+.12*math.sin(2*math.pi*freq*3.01*x+.7))
  pulse=t%3.7
  if pulse<.55: v+=.035*math.sin(2*math.pi*(48-12*pulse)*pulse)*math.exp(-pulse*9)
  fade=max(0,min(1,t/1.8,(duration-t)/1.8)); v=math.tanh(v*1.7)*.72*fade
  frames.append(struct.pack('<h',max(-32767,min(32767,int(v*32767)))))
 w.writeframes(b''.join(frames))
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wavp),'-c:a','libvorbis','-q:a','4',str(assets/'sounds/corisande_theme.ogg')],check=True); wavp.unlink()
print('Carry and original Corisande music features applied.')
